"""
Endpoints de autenticación para el sistema Ezekl Budget.
Maneja el flujo de login de 2 pasos con tokens temporales y JWE.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import logging
import json
import aiohttp
from jose import jwe
from app.core.config import settings
from app.database.connection import execute_sp
from app.services.email_service import send_notification_email
from app.services.email_queue import queue_email
from app.models.auth import (
    RequestTokenRequest,
    RequestTokenResponse,
    LoginRequest,
    LoginResponse,
    VerifyTokenResponse,
    LogoutResponse,
    UserData,
    AuthErrorResponse
)
import secrets
import string

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de autenticación
router = APIRouter()

# Clave secreta para JWE (debe ser exactamente 32 bytes)
JWE_SECRET_KEY = settings.jwe_secret_key
JWE_ALGORITHM = "A256KW"
JWE_ENCRYPTION = "A256GCM"

# Configuración de token
TOKEN_EXPIRY_HOURS = 24  # Token JWE válido por 24 horas


def create_jwe_token(user_data: Dict[str, Any]) -> tuple[str, datetime]:
    """
    Crea un token JWE con los datos del usuario.

    Args:
        user_data: Datos del usuario a incluir en el token

    Returns:
        Tuple con (token_jwe, fecha_expiracion)
    """
    # Crear timestamp de expiración
    expiry = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS)

    # Payload del token
    payload = {
        "user": user_data,
        "exp": int(expiry.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "access_token",
    }

    # Crear token JWE (convertir clave a bytes)
    token_bytes = jwe.encrypt(
        json.dumps(payload),
        JWE_SECRET_KEY.encode('utf-8'),
        algorithm=JWE_ALGORITHM,
        encryption=JWE_ENCRYPTION,
    )
    
    # Convertir bytes a string si es necesario
    if isinstance(token_bytes, bytes):
        token = token_bytes.decode('utf-8')
    else:
        token = token_bytes

    return token, expiry


def verify_jwe_token(token: str) -> Dict[str, Any] | None:
    """
    Verifica y decodifica un token JWE.

    Args:
        token: Token JWE a verificar

    Returns:
        Payload del token si es válido, None si no es válido
    """
    try:
        # Decodificar token JWE (convertir clave a bytes)
        payload_str = jwe.decrypt(token, JWE_SECRET_KEY.encode('utf-8'))
        payload = json.loads(payload_str)

        # Verificar expiración
        exp_timestamp = payload.get("exp")
        if exp_timestamp and datetime.fromtimestamp(
            exp_timestamp, timezone.utc
        ) < datetime.now(timezone.utc):
            logger.warning("Token JWE expirado")
            return None

        return payload

    except Exception as e:
        logger.error(f"Error verificando token JWE: {str(e)}")
        return None


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency para obtener el usuario actual desde el token JWE en el header Authorization.
    
    Args:
        authorization: Header Authorization con formato "Bearer {token}"
        
    Returns:
        Datos del usuario si el token es válido
        
    Raises:
        HTTPException: Si el token no es válido o no está presente
    """
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail="Token de autorización requerido",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verificar formato "Bearer {token}"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401, 
                detail="Esquema de autorización inválido. Use: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except ValueError:
        raise HTTPException(
            status_code=401, 
            detail="Formato de autorización inválido. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verificar token JWE
    payload = verify_jwe_token(token)
    if not payload:
        raise HTTPException(
            status_code=401, 
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_data = payload.get("user", {})
    if not user_data:
        raise HTTPException(
            status_code=401, 
            detail="Datos de usuario no encontrados en token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "user": user_data,
        "exp": payload.get("exp"),
        "iat": payload.get("iat")
    }


async def execute_stored_procedure(
    procedure_name: str, json_param: str
) -> Dict[str, Any]:
    """
    Ejecuta un procedimiento almacenado y retorna el resultado.

    Args:
        procedure_name: Nombre del procedimiento almacenado
        json_param: Parámetro JSON para el procedimiento

    Returns:
        Resultado del procedimiento como diccionario
    """
    try:
        # Convertir el string JSON a diccionario para la función execute_sp
        param_dict = json.loads(json_param)

        # Usar la función de conveniencia de execute_sp
        result = await execute_sp(procedure_name, param_dict)
        return result

    except Exception as e:
        logger.error(f"Error ejecutando {procedure_name}: {str(e)}")
        return {"success": False, "message": f"Error de base de datos: {str(e)}"}


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
                tokenGenerated=False
            )

        # Extraer datos del usuario y token
        auth_data = result.get("auth", {})
        token = result.get("token")

        if not token or not auth_data:
            logger.error("Respuesta inválida del procedimiento spLoginTokenAdd")
            return RequestTokenResponse(
                success=False,
                message="Error generando token",
                tokenGenerated=False
            )

        # Enviar token por email usando cola en background
        user_email = auth_data.get("emailLogin")
        user_name = auth_data.get("nameLogin", "Usuario")

        if user_email:
            email_subject = "Código de acceso - Ezekl Budget"
            email_content = f"""Hola {user_name},

Tu código de acceso es: {token}

Este código es válido por 30 minutos.

Si no solicitaste este código, puedes ignorar este mensaje.

Saludos,
Equipo Ezekl Budget"""

            # Agregar email a la cola para envío en background (no bloquea la respuesta)
            email_task_id = await queue_email(
                to=[user_email],
                subject=email_subject,
                message=email_content,
                is_html=False,
            )

            logger.info(
                f"Email agregado a cola para envío en background: {email_task_id} -> {user_email}"
            )
        else:
            logger.warning(
                f"Usuario {code_login} no tiene email configurado, no se puede enviar token"
            )

        logger.info(f"Token generado exitosamente para {code_login}")

        return RequestTokenResponse(
            success=True,
            message="Token enviado por email exitosamente",
            tokenGenerated=True
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
                success=False,
                message="Credenciales inválidas o token expirado"
            )

        # Extraer datos del usuario
        auth_data = result.get("auth", {})

        if not auth_data:
            logger.error(
                "Datos de usuario no encontrados en respuesta de autenticación"
            )
            return LoginResponse(
                success=False,
                message="Error en datos de autenticación"
            )

        # Generar token JWE
        access_token, expires_at = create_jwe_token(auth_data)

        logger.info(f"Login exitoso para usuario {code_login}")

        return LoginResponse(
            success=True,
            message="Autenticación exitosa",
            user=UserData(**auth_data),
            accessToken=access_token,
            expiresAt=expires_at.isoformat()
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
        401: {"model": AuthErrorResponse, "description": "Token requerido, inválido o expirado"}
    }
)
async def verify_token(current_user: Dict = Depends(get_current_user)):
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
            )
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
        401: {"model": AuthErrorResponse, "description": "Token requerido, inválido o expirado"}
    }
)
async def refresh_token(current_user: Dict = Depends(get_current_user)):
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

        logger.info(f"Token renovado para usuario {user_data.get('codeLogin', 'unknown')}")

        return LoginResponse(
            success=True,
            message="Token renovado exitosamente",
            user=UserData(**user_data),
            accessToken=new_access_token,
            expiresAt=new_expires_at.isoformat()
        )

    except Exception as e:
        logger.error(f"Error renovando token: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Cerrar sesión",
    description="""Invalida la sesión actual del usuario.
    
    Nota: Con JWE no podemos invalidar tokens del lado servidor,
    por lo que este endpoint principalmente serve para limpiar
    datos del cliente y registrar el evento de logout.
    """,
)
async def logout():
    """
    Procesa el logout del usuario.

    Returns:
        Confirmación del logout
    """
    try:
        # Con JWE no podemos invalidar tokens del lado servidor
        # El cliente debe eliminar el token almacenado localmente

        logger.info("Logout procesado")

        return LogoutResponse(
            success=True,
            message="Sesión cerrada exitosamente"
        )

    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get(
    "/microsoft",
    summary="Iniciar autenticación con Microsoft",
    description="Redirige al usuario a Microsoft Azure AD para autenticación OAuth2"
)
async def microsoft_login():
    """Endpoint para iniciar el flujo de autenticación con Microsoft."""
    try:
        # Validar que las credenciales de Azure AD estén configuradas
        if not all([settings.azure_client_id, settings.azure_tenant_id, settings.azure_client_secret]):
            logger.error("❌ Credenciales de Azure AD no configuradas")
            raise HTTPException(
                status_code=500, 
                detail="Autenticación con Microsoft no está configurada"
            )
        
        # Construir URL de autorización de Microsoft
        base_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/authorize"
        
        # Parámetros para la autenticación OAuth2
        params = {
            "client_id": settings.azure_client_id,
            "response_type": "code",
            "redirect_uri": "https://budget.ezekl.com/api/auth/microsoft/callback",
            "scope": "openid profile email User.Read",
            "response_mode": "query",
            "state": "security_token_here"  # En producción, usar un token seguro
        }
        
        # Construir URL completa
        from urllib.parse import urlencode
        auth_url = f"{base_url}?{urlencode(params)}"
        
        logger.info(f"🔗 Redirigiendo a Microsoft para autenticación: {auth_url}")
        
        # Redirigir al usuario a Microsoft
        return RedirectResponse(url=auth_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error al construir URL de Microsoft: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get(
    "/microsoft/callback",
    summary="Callback de autenticación con Microsoft",
    description="Procesa la respuesta de Microsoft Azure AD y completa el login"
)
async def microsoft_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None
):
    """
    Callback de Microsoft OAuth2.
    Procesa el código de autorización y completa el flujo de autenticación.
    """
    try:
        if error:
            logger.error(f"Error de Microsoft OAuth: {error} - {error_description}")
            # Redirigir al frontend con error
            redirect_url = f"{settings.effective_url_base}/#/login?microsoft_error={error}"
            return RedirectResponse(url=redirect_url)

        if not code:
            logger.error("No se recibió código de autorización de Microsoft")
            redirect_url = f"{settings.effective_url_base}/#/login?microsoft_error=no_code"
            return RedirectResponse(url=redirect_url)

        # Intercambiar código por token de acceso
        token_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/token"
        
        token_data = {
            "client_id": settings.azure_client_id,
            "client_secret": settings.azure_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": f"{settings.effective_url_base}/api/auth/microsoft/callback",
            "scope": "openid profile email User.Read"
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

        # Obtener información del usuario de Microsoft Graph
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
        
        # Preparar datos para el stored procedure
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
            "consentProvidedForMinor": user_data.get("consentProvidedForMinor", "")
        }

        # Llamar al stored procedure para manejar el usuario de Microsoft
        json_param = json.dumps(microsoft_data)
        result = await execute_stored_procedure("spLoginMicrosoftAddOrEdit", json_param)
        
        if not result.get("success"):
            logger.error(f"Error en stored procedure: {result.get('message')}")
            redirect_url = f"{settings.effective_url_base}/#/login?microsoft_error=db_error"
            return RedirectResponse(url=redirect_url)

        # Verificar si necesita asociación
        association_status = result.get("associationStatus", "unknown")
        
        if association_status == "needs_association":
            # Usuario Microsoft no asociado - redirigir para asociación
            code_login_microsoft = result.get("codeLoginMicrosoft", "")
            display_name = microsoft_data.get("displayName", "")
            email = microsoft_data.get("mail", "")
            
            redirect_url = (f"{settings.effective_url_base}/#/login?"
                          f"microsoft_pending=true&"
                          f"codeLoginMicrosoft={code_login_microsoft}&"
                          f"displayName={display_name}&"
                          f"email={email}")
            return RedirectResponse(url=redirect_url)
        
        elif association_status == "associated":
            # Usuario ya asociado - login automático
            user_login_data = result.get("userData", {})
            
            # Crear token JWE para el usuario asociado
            jwe_token, expiry_date = create_jwe_token(user_login_data)
            
            redirect_url = (f"{settings.effective_url_base}/#/login?"
                          f"microsoft_success=true&"
                          f"token={jwe_token}")
            return RedirectResponse(url=redirect_url)
        
        else:
            logger.error(f"Estado de asociación desconocido: {association_status}")
            redirect_url = f"{settings.effective_url_base}/#/login?microsoft_error=unknown_status"
            return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.error(f"Error en callback de Microsoft: {str(e)}")
        redirect_url = f"{settings.effective_url_base}/#/login?microsoft_error=server_error"
        return RedirectResponse(url=redirect_url)


@router.post(
    "/microsoft/associate",
    response_model=LoginResponse,
    summary="Asociar cuenta Microsoft con usuario existente",
    description="""Asocia una cuenta de Microsoft con un usuario existente del sistema.
    
    Este endpoint:
    1. Valida que el codeLogin existe en el sistema
    2. Valida que el codeLoginMicrosoft existe y no está asociado
    3. Crea la asociación entre ambas cuentas
    4. **AUTENTICA automáticamente al usuario (igual que spLoginAuth + login())**
    5. Genera un token JWE de sesión para el usuario
    6. Retorna el token y datos del usuario
    
    **Flujo de uso:**
    - Usuario se autentica con Microsoft (callback redirige con microsoft_pending=true)
    - Frontend muestra formulario de asociación
    - Usuario ingresa su codeLogin existente
    - Frontend llama este endpoint
    - Sistema asocia cuentas y autentica automáticamente (misma respuesta que login normal)
    
    **Seguridad:**
    - Validación de existencia de ambos códigos
    - Prevención de doble asociación
    - Autenticación completa como en flujo de login normal
    - Token JWE seguro con expiración
    """,
)
async def associate_microsoft_account(data: dict):
    """
    Asocia una cuenta de Microsoft con un usuario existente y lo autentica.
    
    Después de asociar exitosamente, hace exactamente lo mismo que:
    - spLoginAuth.sql (validación y autenticación)
    - función login() de Python (generación de token JWE)
    
    Args:
        data: {"codeLogin": "ABC123", "codeLoginMicrosoft": "uuid-de-microsoft"}

    Returns:
        LoginResponse idéntica al login normal con token JWE y datos del usuario
    """
    try:
        code_login = data.get("codeLogin")
        code_login_microsoft = data.get("codeLoginMicrosoft")
        
        if not code_login or not code_login_microsoft:
            raise HTTPException(
                status_code=400,
                detail="codeLogin y codeLoginMicrosoft son requeridos"
            )

        # Preparar parámetros para el stored procedure de asociación
        association_data = {
            "codeLogin": code_login,
            "codeLoginMicrosoft": code_login_microsoft
        }

        json_param = json.dumps(association_data)
        result = await execute_stored_procedure("spLoginLoginMicrosoftAssociate", json_param)
        
        if not result.get("success"):
            error_message = result.get("message", "Error desconocido en la asociación")
            logger.error(f"Error en asociación: {error_message}")
            
            # Determinar tipo de error para respuesta más específica
            if "not found" in error_message.lower():
                raise HTTPException(status_code=404, detail=error_message)
            elif "already associated" in error_message.lower():
                raise HTTPException(status_code=409, detail=error_message)
            else:
                raise HTTPException(status_code=400, detail=error_message)

        # Obtener datos del usuario asociado
        user_data = result.get("userData", {})
        
        if not user_data:
            logger.error("No se obtuvieron datos del usuario tras la asociación")
            raise HTTPException(
                status_code=500, 
                detail="Error obteniendo datos del usuario"
            )

        # Crear token JWE para el usuario
        jwe_token, expiry_date = create_jwe_token(user_data)

        logger.info(f"Asociación exitosa: {code_login} <-> {code_login_microsoft}")
        
        return LoginResponse(
            success=True,
            message="Autenticación exitosa",
            user=UserData(**user_data),
            accessToken=jwe_token,
            expiresAt=expiry_date.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en asociación Microsoft: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )
