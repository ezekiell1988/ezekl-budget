"""
Endpoints de autenticación para el sistema Ezekl Budget.
Maneja el flujo de login de 2 pasos con tokens temporales y JWE.
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import logging
import json
import aiohttp
import base64
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs, urljoin
from jose import jwe
from app.core.config import settings
from app.core.redis import redis_client
from app.database.connection import execute_sp
from app.services.email_queue import queue_email
from app.utils.email_templates import render_request_token_email
from app.models.auth import (
    CurrentUser,
    RequestTokenRequest,
    RequestTokenResponse,
    LoginRequest,
    LoginResponse,
    VerifyTokenResponse,
    LogoutResponse,
    UserData,
    AuthErrorResponse,
    MicrosoftUrlRequest,
    MicrosoftUrlResponse,
)
from app.utils.auth import (
    create_jwe_token,
    verify_jwe_token,
    get_current_user,
    execute_stored_procedure,
    security,
)

# Configurar logging
logger = logging.getLogger(__name__)

# Configurar Jinja2 Templates
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Router para endpoints de autenticación
router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Incluir sub-routers (importar aquí para evitar circular imports)
from app.api.auth import microsoft as microsoft_router
router.include_router(microsoft_router.router)


@router.post(
    "/request-token",
    response_model=RequestTokenResponse,
    summary="Solicitar token de acceso",
    description="""Inicia el proceso de autenticación solicitando un token temporal.
    
    Este endpoint:
    1. Valida que el codeLogin exista en el sistema
    2. Genera un token de 5 dígitos aleatorio
    3. Envía el token por email al usuario registrado
    4. Retorna confirmación del envío (sin datos sensibles del usuario)
    
    **Flujo:**
    - Usuario ingresa su codeLogin
    - Sistema valida y genera token
    - Token se envía por email
    - Usuario procede al segundo paso del login
    
    **Seguridad:**
    - No se devuelven datos personales del usuario
    - Los datos solo se usan internamente para el envío del email
    """,
)
async def request_token(data: RequestTokenRequest):
    """
    Solicita un token de acceso temporal para el usuario.

    Args:
        data: {"codeLogin": "codigo_usuario"}

    Returns:
        RequestTokenResponse con resultado de la operación
    """
    try:
        code_login = data.codeLogin

        # Ejecutar spLoginTokenAdd para generar token
        json_param = json.dumps({"codeLogin": code_login})
        result = await execute_stored_procedure("spLoginTokenAdd", json_param)

        if not result.get("success", False):
            logger.warning(f"Fallo al generar token para {code_login}")
            return RequestTokenResponse(
                success=False,
                message="Código de usuario no encontrado",
                tokenGenerated=False,
            )

        # Extraer datos del usuario y token
        auth_data = result.get("auth", {})
        token = result.get("token")

        if not token or not auth_data:
            logger.error("Respuesta inválida del procedimiento spLoginTokenAdd")
            return RequestTokenResponse(
                success=False, message="Error generando token", tokenGenerated=False
            )

        # Enviar token por email usando cola en background
        user_email = auth_data.get("emailLogin")
        user_name = auth_data.get("nameLogin", "Usuario")

        # TEMPORAL: Prueba con Gmail (comentar después)
        # user_email = "TU_GMAIL_AQUI@gmail.com"  # Descomentar para probar

        if user_email:
            logger.info(f"📧 Preparando email para: {user_email}")
            email_subject = f"Código de acceso - {token}"

            # Renderizar templates HTML y texto plano del email
            email_html, email_text = render_request_token_email(
                user_name=user_name, token=token
            )
            logger.info(
                f"✅ Templates renderizados: HTML={len(email_html)} chars, TEXT={len(email_text)} chars"
            )

            # Agregar email a la cola para envío en background (no bloquea la respuesta)
            # Enviamos AMBAS versiones (HTML + texto plano) para evitar filtros de spam
            email_task_id = await queue_email(
                to=[user_email],
                subject=email_subject,
                message=email_html,
                is_html=True,
                text_message=email_text,
            )
            logger.info(f"✅ Email agregado a cola con ID: {email_task_id}")

        else:
            logger.warning(
                f"Usuario {code_login} no tiene email configurado, no se puede enviar token"
            )

        return RequestTokenResponse(
            success=True,
            message="Token enviado por email exitosamente",
            tokenGenerated=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en request-token: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Autenticación con token",
    description="""Completa el proceso de autenticación usando el token recibido por email.
    
    Este endpoint:
    1. Valida el codeLogin y token contra la base de datos
    2. Si es válido, elimina el token usado (un solo uso)
    3. Genera un token JWE de sesión con expiración
    4. Retorna el token y datos del usuario
    
    **Seguridad:**
    - Tokens de un solo uso (se eliminan después de usarse)
    - Token JWE con expiración de 24 horas
    - Validación de fecha de expiración
    """,
)
async def login(data: LoginRequest):
    """
    Autentica al usuario usando codeLogin y token temporal.

    Args:
        data: {"codeLogin": "codigo", "token": "12345"}

    Returns:
        LoginResponse con token JWE y datos del usuario
    """
    try:
        code_login = data.codeLogin
        token = data.token

        # Ejecutar spLoginAuth para validar y eliminar token
        json_param = json.dumps({"codeLogin": code_login, "token": token})
        result = await execute_stored_procedure("spLoginAuth", json_param)

        if not result.get("success", False):
            logger.warning(f"Fallo de autenticación para {code_login}")
            return LoginResponse(
                success=False, message="Credenciales inválidas o token expirado"
            )

        # Extraer datos del usuario
        auth_data = result.get("auth", {})

        if not auth_data:
            logger.error(
                "Datos de usuario no encontrados en respuesta de autenticación"
            )
            return LoginResponse(
                success=False, message="Error en datos de autenticación"
            )

        # Generar token JWE
        access_token, expires_at = create_jwe_token(auth_data)

        # Guardar sesión en Redis (24 horas) para unificar con WhatsApp
        from app.services.auth_service import auth_service

        user_email = auth_data.get("email")
        if user_email:
            await auth_service.save_session(
                user_id=user_email,
                user_data=auth_data,
                session_type="web",
                expires_in_seconds=86400,  # 24 horas
            )

        return LoginResponse(
            success=True,
            message="Autenticación exitosa",
            user=UserData(**auth_data),
            accessToken=access_token,
            expiresAt=expires_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get(
    "/verify-token",
    response_model=VerifyTokenResponse,
    summary="Obtener información del usuario autenticado",
    description="""Endpoint privado que retorna los datos del usuario actual y fecha de vencimiento del token.
    
    **Autenticación requerida:**
    - Header: Authorization: Bearer {jwe_token}
    
    **Útil para:**
    - Obtener datos del usuario autenticado
    - Verificar tiempo restante de sesión
    - Guards de autenticación en frontend
    - Refrescar información del usuario
    
    **Respuesta:**
    - Datos completos del usuario
    - Fecha de vencimiento del token
    - Tiempo de emisión del token
    """,
    responses={
        401: {
            "model": AuthErrorResponse,
            "description": "Token requerido, inválido o expirado",
        }
    },
)
async def verify_token(current_user: CurrentUser = Depends(get_current_user)):
    """
    Endpoint privado que retorna información del usuario autenticado.

    Args:
        current_user: Datos del usuario obtenidos del token JWE (inyectado por dependencia)

    Returns:
        Datos del usuario y información del token
    """
    try:
        user_data = current_user["user"]
        exp_timestamp = current_user["exp"]
        iat_timestamp = current_user["iat"]

        return VerifyTokenResponse(
            user=UserData(**user_data),
            expiresAt=(
                datetime.fromtimestamp(exp_timestamp, timezone.utc).isoformat()
                if exp_timestamp
                else None
            ),
            issuedAt=(
                datetime.fromtimestamp(iat_timestamp, timezone.utc).isoformat()
                if iat_timestamp
                else None
            ),
        )

    except Exception as e:
        logger.error(f"Error obteniendo información de usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post(
    "/refresh-token",
    response_model=LoginResponse,
    summary="Extender tiempo de expiración del token",
    description="""Endpoint privado para renovar/extender la expiración del token actual.
    
    **Autenticación requerida:**
    - Header: Authorization: Bearer {jwe_token}
    
    **Funcionalidad:**
    - Valida el token actual del usuario
    - Genera un nuevo token JWE con tiempo extendido (+24 horas)
    - Mantiene los mismos datos de usuario
    - Útil para mantener sesiones activas sin reautenticación
    
    **Casos de uso:**
    - Extender sesión antes de que expire
    - Mantener actividad del usuario automáticamente
    - Evitar relogin innecesario en sesiones largas
    """,
    responses={
        401: {
            "model": AuthErrorResponse,
            "description": "Token requerido, inválido o expirado",
        }
    },
)
async def refresh_token(current_user: CurrentUser = Depends(get_current_user)):
    """
    Extiende la expiración del token actual del usuario autenticado.

    Args:
        current_user: Datos del usuario obtenidos del token JWE (inyectado por dependencia)

    Returns:
        Nuevo token JWE con expiración extendida
    """
    try:
        user_data = current_user["user"]

        # Generar nuevo token JWE con tiempo extendido
        new_access_token, new_expires_at = create_jwe_token(user_data)

        # Extender también la sesión en Redis
        from app.services.auth_service import auth_service

        user_email = user_data.get("email")
        if user_email:
            await auth_service.extend_session(
                user_id=user_email,
                session_type="web",
                expires_in_seconds=86400,  # 24 horas
            )

        return LoginResponse(
            success=True,
            message="Token renovado exitosamente",
            user=UserData(**user_data),
            accessToken=new_access_token,
            expiresAt=new_expires_at.isoformat(),
        )

    except Exception as e:
        logger.error(f"Error renovando token: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Cerrar sesión (Web y WhatsApp)",
    description="""Invalida la sesión actual del usuario en Redis.
    
    **Autenticación requerida:**
    - Header: Authorization: Bearer {jwe_token}
    
    **Query Parameters:**
    - `microsoft_logout` (opcional): Si es "true", también cierra sesión en Microsoft
    
    **Funcionalidad:**
    - Elimina la sesión del usuario en Redis
    - El token JWE queda inválido para futuras peticiones
    - Funciona tanto para web como para WhatsApp
    - Opcionalmente redirige a Microsoft para cerrar sesión completa
    
    **Nota:** El cliente también debe eliminar el token almacenado localmente.
    """,
)
async def logout(
    current_user: CurrentUser = Depends(get_current_user),
    microsoft_logout: str = Query(
        default="false", description="Si es 'true', también cierra sesión en Microsoft"
    ),
):
    """
    Procesa el logout del usuario (web o WhatsApp).

    Args:
        current_user: Datos del usuario obtenidos del token JWE
        microsoft_logout: Si es "true", redirige a logout de Microsoft

    Returns:
        Confirmación del logout o redirección a Microsoft
    """
    try:
        from app.services.auth_service import auth_service

        user_data = current_user.get("user", {})
        user_email = user_data.get("email")

        if user_email:
            # Eliminar sesión de Redis (funciona para web y whatsapp)
            await auth_service.delete_session(user_id=user_email, session_type="web")
            logger.info(f"✅ Sesión eliminada para {user_email}")

        # Si se solicita logout de Microsoft, redirigir
        if microsoft_logout.lower() == "true":
            # URL de post-logout (donde redirigir después del logout de Microsoft)
            post_logout_redirect = (
                f"{settings.effective_url_base}/#/login?logout=success"
            )

            # Construir URL de logout de Microsoft
            logout_url = (
                f"{settings.microsoft_logout_endpoint}"
                f"?post_logout_redirect_uri={post_logout_redirect}"
            )

            logger.info(f"🔄 Redirigiendo a logout de Microsoft: {logout_url}")

            # Retornar la URL de logout para que el cliente redirija
            return {
                "success": True,
                "message": "Sesión cerrada exitosamente",
                "microsoft_logout_url": logout_url,
                "redirect_required": True,
            }

        return LogoutResponse(success=True, message="Sesión cerrada exitosamente")

    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


def _create_whatsapp_error_page(
    error_title: str, error_message: str, status_code: int = 400
):
    """Crea una página HTML de error para el flujo de WhatsApp usando template."""
    html_content = templates.TemplateResponse(
        "auth/whatsapp_error.html",
        {
            "request": {},
            "error_title": error_title,
            "error_message": error_message,
        },
    ).body.decode("utf-8")
    
    return HTMLResponse(content=html_content, status_code=status_code)


async def microsoft_callback_normal(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    """
    Procesa el callback de Microsoft para el flujo web normal.

    Maneja todo el proceso: validaciones, obtención de tokens, datos de usuario,
    stored procedure y redireccionamiento al frontend.
    """
    try:
        # 1. Manejo de errores de OAuth
        if error:
            logger.error(f"Error de Microsoft OAuth: {error} - {error_description}")
            redirect_url = (
                f"{settings.effective_url_base}/#/login?microsoft_error={error}"
            )
            return RedirectResponse(url=redirect_url)

        # 2. Validar que se recibió el código de autorización
        if not code:
            logger.error("No se recibió código de autorización de Microsoft")
            redirect_url = (
                f"{settings.effective_url_base}/#/login?microsoft_error=no_code"
            )
            return RedirectResponse(url=redirect_url)

        # 3. Intercambiar código por token de acceso
        token_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/token"

        token_data = {
            "client_id": settings.azure_client_id,
            "client_secret": settings.azure_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.effective_microsoft_redirect_uri,
            "scope": "openid profile email User.Read",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=token_data) as token_response:
                if token_response.status != 200:
                    error_text = await token_response.text()
                    logger.error(f"Error obteniendo token: {error_text}")
                    redirect_url = f"{settings.effective_url_base}/#/login?microsoft_error=token_error"
                    return RedirectResponse(url=redirect_url)

                token_json = await token_response.json()

        access_token = token_json.get("access_token")

        # 4. Obtener información del usuario de Microsoft Graph
        graph_url = "https://graph.microsoft.com/v1.0/me"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(graph_url, headers=headers) as user_response:
                if user_response.status != 200:
                    error_text = await user_response.text()
                    logger.error(f"Error obteniendo datos de usuario: {error_text}")
                    redirect_url = f"{settings.effective_url_base}/#/login?microsoft_error=user_error"
                    return RedirectResponse(url=redirect_url)

                user_data = await user_response.json()

        # 5. Preparar datos para el stored procedure
        microsoft_data = {
            "displayName": user_data.get("displayName", ""),
            "mail": user_data.get("mail") or user_data.get("userPrincipalName", ""),
            "id": user_data.get("id", ""),
            "userPrincipalName": user_data.get("userPrincipalName", ""),
            "givenName": user_data.get("givenName", ""),
            "surname": user_data.get("surname", ""),
            "jobTitle": user_data.get("jobTitle", ""),
            "mobilePhone": user_data.get("mobilePhone", ""),
            "businessPhones": ",".join(user_data.get("businessPhones", [])),
            "officeLocation": user_data.get("officeLocation", ""),
            "preferredLanguage": user_data.get("preferredLanguage", ""),
            "department": user_data.get("department", ""),
            "companyName": user_data.get("companyName", ""),
            "country": user_data.get("country", ""),
            "city": user_data.get("city", ""),
            "postalCode": user_data.get("postalCode", ""),
            "state": user_data.get("state", ""),
            "streetAddress": user_data.get("streetAddress", ""),
            "ageGroup": user_data.get("ageGroup", ""),
            "consentProvidedForMinor": user_data.get("consentProvidedForMinor", ""),
        }

        # 6. Llamar al stored procedure para manejar el usuario de Microsoft
        json_param = json.dumps(microsoft_data)
        result = await execute_stored_procedure("spLoginMicrosoftAddOrEdit", json_param)

        if not result.get("success"):
            logger.error(f"Error en stored procedure: {result.get('message')}")
            redirect_url = (
                f"{settings.effective_url_base}/#/login?microsoft_error=db_error"
            )
            return RedirectResponse(url=redirect_url)

        # 7. Procesar según el estado de asociación
        association_status = result.get("associationStatus", "unknown")
        microsoft_user_info = result.get("microsoftUser", {})
        code_login_microsoft = microsoft_user_info.get(
            "microsoftUserId", user_data.get("id", "")
        )
        display_name = microsoft_data.get("displayName", "")
        email = microsoft_data.get("mail", "")

        if association_status == "needs_association":
            # Usuario Microsoft no asociado - necesita vincular con cuenta existente
            redirect_url = (
                f"{settings.effective_url_base}/#/login?"
                f"microsoft_pending=true&"
                f"codeLoginMicrosoft={code_login_microsoft}&"
                f"displayName={display_name}&"
                f"email={email}"
            )
            return RedirectResponse(url=redirect_url)

        elif association_status == "associated":
            # Usuario ya asociado - login automático
            user_login_data = result.get("linkedUser", {})

            # Crear token JWE para el usuario asociado
            jwe_token, expiry_date = create_jwe_token(user_login_data)

            # Guardar sesión en Redis
            from app.services.auth_service import auth_service

            user_email = user_login_data.get("email")
            if user_email:
                await auth_service.save_session(
                    user_id=user_email,
                    user_data=user_login_data,
                    session_type="web",
                    expires_in_seconds=86400,  # 24 horas
                )

            redirect_url = (
                f"{settings.effective_url_base}/#/login?"
                f"microsoft_success=true&"
                f"token={jwe_token}"
            )
            return RedirectResponse(url=redirect_url)

        else:
            logger.error(f"Estado de asociación desconocido: {association_status}")
            redirect_url = (
                f"{settings.effective_url_base}/#/login?microsoft_error=unknown_status"
            )
            return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.error(f"Error en microsoft_callback_normal: {str(e)}")
        redirect_url = (
            f"{settings.effective_url_base}/#/login?microsoft_error=server_error"
        )
        return RedirectResponse(url=redirect_url)


async def microsoft_callback_redirect(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    url_redirect_data: dict = None,
):
    """
    Procesa el callback de Microsoft para el flujo de redirección a URL personalizada.

    Este flujo:
    1. Completa la autenticación con Microsoft
    2. Crea o asocia la cuenta del usuario
    3. Genera un token JWT
    4. Redirige a la URL personalizada con el token como query param
    """
    from fastapi.responses import HTMLResponse

    try:
        flow_id = url_redirect_data.get("flow_id")

        # 1. Manejo de errores de OAuth
        if error:
            logger.error(f"Error de Microsoft OAuth: {error} - {error_description}")
            html_content = templates.TemplateResponse(
                "auth/microsoft_oauth_error.html",
                {
                    "request": {},
                    "error_description": error_description or error,
                },
            ).body.decode("utf-8")
            return HTMLResponse(content=html_content, status_code=400)

        # 2. Validar que tenemos el código de autorización
        if not code:
            logger.error("No se recibió código de autorización de Microsoft")
            html_content = templates.TemplateResponse(
                "auth/microsoft_no_code.html",
                {"request": {}},
            ).body.decode("utf-8")
            return HTMLResponse(content=html_content, status_code=400)

        # 3. Recuperar URL de redirección desde Redis
        redis_key = f"microsoft_redirect:{flow_id}"
        redirect_data = await redis_client.get(redis_key)

        if not redirect_data:
            logger.error(f"No se encontró URL de redirección para flow_id: {flow_id}")
            html_content = templates.TemplateResponse(
                "auth/microsoft_session_expired.html",
                {"request": {}},
            ).body.decode("utf-8")
            return HTMLResponse(content=html_content, status_code=400)

        redirect_url = redirect_data.get("redirect_url")

        # 4. Intercambiar código por access token
        token_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/token"
        token_data = {
            "client_id": settings.azure_client_id,
            "scope": "openid profile email User.Read",
            "code": code,
            "redirect_uri": settings.effective_microsoft_redirect_uri,
            "grant_type": "authorization_code",
            "client_secret": settings.azure_client_secret,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=token_data) as token_response:
                if token_response.status != 200:
                    error_text = await token_response.text()
                    logger.error(f"Error obteniendo access token: {error_text}")
                    html_content = templates.TemplateResponse(
                        "auth/microsoft_generic_error.html",
                        {
                            "request": {},
                            "error_message": "No se pudo obtener el token de acceso.",
                        },
                    ).body.decode("utf-8")
                    return HTMLResponse(content=html_content, status_code=500)

                token_json = await token_response.json()

        access_token = token_json.get("access_token")

        # 5. Obtener información del usuario de Microsoft Graph
        graph_url = "https://graph.microsoft.com/v1.0/me"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(graph_url, headers=headers) as user_response:
                if user_response.status != 200:
                    error_text = await user_response.text()
                    logger.error(f"Error obteniendo datos de usuario: {error_text}")
                    html_content = templates.TemplateResponse(
                        "auth/microsoft_generic_error.html",
                        {
                            "request": {},
                            "error_message": "No se pudieron obtener los datos del usuario.",
                        },
                    ).body.decode("utf-8")
                    return HTMLResponse(content=html_content, status_code=500)

                user_data = await user_response.json()

        # 6. Ejecutar stored procedure para crear/login usuario Microsoft
        user_principal_name = user_data.get("userPrincipalName")
        display_name = user_data.get("displayName")
        mail = user_data.get("mail") or user_principal_name
        microsoft_id = user_data.get("id")

        logger.info(
            f"🔍 Datos de Microsoft Graph obtenidos - ID: {microsoft_id}, Email: {mail}, Name: {display_name}"
        )
        logger.info(f"🔍 User data completo: {user_data}")

        # El SP espera estos campos con estos nombres exactos
        sp_params = {
            "id": microsoft_id,  # El SP espera "id" no "microsoftId"
            "mail": mail,
            "displayName": display_name,
            "userPrincipalName": user_principal_name,
        }

        logger.info(f"📤 Enviando a spLoginMicrosoftAddOrEdit: {sp_params}")

        result = await execute_sp("spLoginMicrosoftAddOrEdit", sp_params)

        logger.info(f"📦 Resultado de spLoginMicrosoftAddOrEdit: {result}")

        # Verificar resultado - el SP retorna success=1 y associationStatus
        if not result:
            logger.error(f"❌ spLoginMicrosoftAddOrEdit retornó None o vacío")
            html_content = templates.TemplateResponse(
                "auth/microsoft_generic_error.html",
                {
                    "request": {},
                    "error_message": "No se pudo procesar la autenticación (respuesta vacía del servidor).",
                },
            ).body.decode("utf-8")
            return HTMLResponse(content=html_content, status_code=500)

        # Verificar success (puede ser 1, True, "success", etc.)
        success = result.get("success")
        if not success or (isinstance(success, (int, bool)) and not success):
            error_msg = result.get("message", "Error desconocido")
            logger.error(f"❌ Error en spLoginMicrosoftAddOrEdit: {error_msg}")
            html_content = templates.TemplateResponse(
                "auth/microsoft_generic_error.html",
                {
                    "request": {},
                    "error_message": f"No se pudo procesar la autenticación. {error_msg}",
                },
            ).body.decode("utf-8")
            return HTMLResponse(content=html_content, status_code=500)

        # Verificar el estado de asociación
        association_status = result.get("associationStatus")
        logger.info(f"🔗 Estado de asociación: {association_status}")

        # 7. Generar token JWT para el usuario autenticado
        # Si está asociado, usar linkedUser; si no, usar microsoftUser
        if association_status == "associated":
            user_login_data = result.get("linkedUser")
        else:
            # Usuario no asociado - podemos crear una sesión temporal o requerir asociación
            # Por ahora, mostramos mensaje de que necesita asociación
            microsoft_user = result.get("microsoftUser", {})
            logger.warning(
                f"⚠️ Usuario Microsoft no asociado a cuenta del sistema: {microsoft_user.get('email')}"
            )

            html_content = templates.TemplateResponse(
                "auth/microsoft_needs_association.html",
                {
                    "request": {},
                    "user_email": microsoft_user.get("email", ""),
                },
            ).body.decode("utf-8")
            return HTMLResponse(content=html_content, status_code=403)

        logger.info(f"👤 Datos del usuario para token: {user_login_data}")

        if not user_login_data or not isinstance(user_login_data, dict):
            logger.error(
                f"❌ No se obtuvieron datos válidos del usuario. Tipo: {type(user_login_data)}, Valor: {user_login_data}"
            )
            html_content = templates.TemplateResponse(
                "auth/microsoft_generic_error.html",
                {
                    "request": {},
                    "error_message": "No se pudieron obtener los datos del usuario.",
                },
            ).body.decode("utf-8")
            return HTMLResponse(content=html_content, status_code=500)

        # Crear token JWE
        token_jwe, expiry = create_jwe_token(user_login_data)

        # 8. Limpiar Redis (ya no necesitamos la URL guardada)
        await redis_client.delete(redis_key)

        logger.info(f"✅ Usuario autenticado exitosamente via URL redirect: {mail}")

        # 9. Redirigir a la URL personalizada con el token como query param
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        query_params["token"] = [token_jwe]

        # Reconstruir la URL con el nuevo parámetro
        from urllib.parse import urlunparse

        new_query = urlencode(query_params, doseq=True)
        final_url = urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment,
            )
        )

        logger.info(f"🔄 Redirigiendo a: {final_url[:100]}...")

        return RedirectResponse(url=final_url)

    except Exception as e:
        logger.error(f"Error en microsoft_callback_redirect: {str(e)}")
        html_content = templates.TemplateResponse(
            "auth/microsoft_generic_error.html",
            {
                "request": {},
                "error_message": "Ocurrió un error inesperado. Por favor, intenta nuevamente.",
            },
        ).body.decode("utf-8")
        return HTMLResponse(content=html_content, status_code=500)


async def microsoft_callback_whatsapp(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    whatsapp_data: dict = None,
):
    """
    Procesa el callback de Microsoft para el flujo de autenticación de WhatsApp.

    Maneja todo el proceso: validaciones, obtención de tokens, datos de usuario,
    stored procedure y generación de páginas HTML de respuesta.
    """
    from fastapi.responses import HTMLResponse

    try:
        # 1. Manejo de errores de OAuth
        if error:
            logger.error(
                f"Error de Microsoft OAuth (WhatsApp): {error} - {error_description}"
            )
            return _create_whatsapp_error_page(
                "Error de Autenticación", error_description or error
            )

        # 2. Validar que se recibió el código de autorización
        if not code:
            logger.error("No se recibió código de autorización de Microsoft (WhatsApp)")
            return _create_whatsapp_error_page(
                "Error de Autenticación", "No se recibió código de autorización."
            )

        # 3. Intercambiar código por token de acceso
        token_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/token"

        token_data = {
            "client_id": settings.azure_client_id,
            "client_secret": settings.azure_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.effective_microsoft_redirect_uri,
            "scope": "openid profile email User.Read",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=token_data) as token_response:
                if token_response.status != 200:
                    error_text = await token_response.text()
                    logger.error(f"Error obteniendo token (WhatsApp): {error_text}")
                    return _create_whatsapp_error_page(
                        "Error de Autenticación", "Error al obtener token de Microsoft."
                    )

                token_json = await token_response.json()

        access_token = token_json.get("access_token")

        # 4. Obtener información del usuario de Microsoft Graph
        graph_url = "https://graph.microsoft.com/v1.0/me"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(graph_url, headers=headers) as user_response:
                if user_response.status != 200:
                    error_text = await user_response.text()
                    logger.error(
                        f"Error obteniendo datos de usuario (WhatsApp): {error_text}"
                    )
                    return _create_whatsapp_error_page(
                        "Error de Autenticación", "Error al obtener datos del usuario."
                    )

                user_data = await user_response.json()

        logger.info(
            f"🔄 Flujo de autenticación de WhatsApp detectado para {whatsapp_data['phone_number']}"
        )

        # 5. Preparar datos para el stored procedure
        microsoft_data = {
            "displayName": user_data.get("displayName", ""),
            "mail": user_data.get("mail") or user_data.get("userPrincipalName", ""),
            "id": user_data.get("id", ""),
            "userPrincipalName": user_data.get("userPrincipalName", ""),
            "givenName": user_data.get("givenName", ""),
            "surname": user_data.get("surname", ""),
            "jobTitle": user_data.get("jobTitle", ""),
            "mobilePhone": user_data.get("mobilePhone", ""),
            "businessPhones": ",".join(user_data.get("businessPhones", [])),
            "officeLocation": user_data.get("officeLocation", ""),
            "preferredLanguage": user_data.get("preferredLanguage", ""),
            "department": user_data.get("department", ""),
            "companyName": user_data.get("companyName", ""),
            "country": user_data.get("country", ""),
            "city": user_data.get("city", ""),
            "postalCode": user_data.get("postalCode", ""),
            "state": user_data.get("state", ""),
            "streetAddress": user_data.get("streetAddress", ""),
            "ageGroup": user_data.get("ageGroup", ""),
            "consentProvidedForMinor": user_data.get("consentProvidedForMinor", ""),
        }

        # 6. Llamar al stored procedure para manejar el usuario de Microsoft
        json_param = json.dumps(microsoft_data)
        result = await execute_stored_procedure("spLoginMicrosoftAddOrEdit", json_param)

        if not result.get("success"):
            logger.error(
                f"Error en stored procedure (WhatsApp): {result.get('message')}"
            )
            return _create_whatsapp_error_page(
                "Error de Autenticación",
                "Error en el procesamiento de la autenticación.",
                500,
            )

        # 7. Procesar según el estado de asociación
        association_status = result.get("associationStatus", "unknown")
        microsoft_user_info = result.get("microsoftUser", {})
        code_login_microsoft = microsoft_user_info.get(
            "microsoftUserId", user_data.get("id", "")
        )
        display_name = microsoft_data.get("displayName", "")
        email = microsoft_data.get("mail", "")

        phone_number = whatsapp_data["phone_number"]
        whatsapp_token = whatsapp_data["whatsapp_token"]
        bot_phone_number = whatsapp_data.get("bot_phone_number")

        # Preparar número de WhatsApp para el botón
        if bot_phone_number:
            wa_number = (
                bot_phone_number.replace("+", "")
                .replace(" ", "")
                .replace("-", "")
                .replace("(", "")
                .replace(")", "")
            )
        else:
            wa_number = settings.whatsapp_phone_number_id

        if association_status == "needs_association":
            # Usuario Microsoft no asociado - mostrar formulario de asociación
            html_content = templates.TemplateResponse(
                "auth/whatsapp_association_form.html",
                {
                    "request": {},
                    "display_name": display_name,
                    "email": email,
                    "wa_number": wa_number,
                    "code_login_microsoft": code_login_microsoft,
                    "phone_number": phone_number,
                    "whatsapp_token": whatsapp_token,
                },
            ).body.decode("utf-8")
            return HTMLResponse(content=html_content)

        elif association_status == "associated":
            # Usuario ya asociado - guardar sesión y mostrar página de éxito
            from app.services.whatsapp_service import whatsapp_service

            user_login_data = result.get("linkedUser", {})

            # Guardar autenticación en Redis (válida por 24 horas)
            await whatsapp_service.save_whatsapp_auth(
                phone_number=phone_number,
                user_data=user_login_data,
                expires_in_seconds=86400,  # 24 horas
            )

            # Eliminar el token de autenticación temporal (ya fue usado)
            await whatsapp_service.delete_auth_token(whatsapp_token)

            logger.info(
                f"✅ Usuario de WhatsApp autenticado exitosamente: {phone_number}"
            )

            # Mostrar página de éxito
            html_content = templates.TemplateResponse(
                "auth/whatsapp_auth_success.html",
                {
                    "request": {},
                    "user_name": user_login_data.get('name', 'Usuario'),
                    "user_email": user_login_data.get('email', ''),
                    "phone_number": phone_number,
                    "wa_number": wa_number,
                },
            ).body.decode("utf-8")
            return HTMLResponse(content=html_content)

        else:
            logger.error(f"Estado de asociación desconocido: {association_status}")
            html_content = templates.TemplateResponse(
                "auth/whatsapp_unknown_error.html",
                {"request": {}},
            ).body.decode("utf-8")
            return HTMLResponse(content=html_content, status_code=500)

    except Exception as e:
        logger.error(f"Error en microsoft_callback_whatsapp: {str(e)}")
        return _create_whatsapp_error_page(
            "Error del Servidor", "Ocurrió un error inesperado.", 500
        )


@router.get(
    "/callback",
    summary="Callback de autenticación con Microsoft",
    description="Procesa la respuesta de Microsoft Azure AD y completa el login",
)
async def microsoft_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    """
    Callback de Microsoft OAuth2 - Router principal.
    Detecta el tipo de flujo y delega a la función correspondiente.

    Tipos de flujo soportados:
    1. Normal (Web): Redirección a la aplicación web principal
    2. WhatsApp: Autenticación para usuarios de WhatsApp
    3. URL Redirect: Redirección a URL personalizada con token JWT
    """
    # Detectar el tipo de flujo basado en el state
    is_whatsapp_auth = False
    is_url_redirect = False
    whatsapp_data = None
    url_redirect_data = None

    if state:
        try:
            decoded_state = base64.urlsafe_b64decode(state.encode()).decode()
            state_data = json.loads(decoded_state)

            # Detectar flujo de URL redirect
            if state_data.get("flow_type") == "url_redirect" and state_data.get(
                "flow_id"
            ):
                is_url_redirect = True
                url_redirect_data = state_data
                logger.info(
                    f"🔄 Flujo de URL redirect detectado: {state_data.get('flow_id')}"
                )

            # Detectar flujo de WhatsApp
            elif state_data.get("whatsapp_token") and state_data.get("phone_number"):
                is_whatsapp_auth = True
                whatsapp_data = state_data
                logger.info(
                    f"📱 Flujo de WhatsApp detectado: {state_data.get('phone_number')}"
                )

        except Exception as e:
            logger.warning(
                f"No se pudo decodificar state, usando flujo normal: {str(e)}"
            )

    # Delegar al flujo correspondiente
    if is_url_redirect:
        return await microsoft_callback_redirect(
            code, state, error, error_description, url_redirect_data
        )
    else:
        return await microsoft_callback_normal(code, state, error, error_description)
