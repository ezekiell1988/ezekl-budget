"""
Endpoints de autenticación para el sistema Ezekl Budget.
Maneja el flujo de login de 2 pasos con tokens temporales y JWE.
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import logging
import json
import aiohttp
import base64
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

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de autenticación
router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Esquema de seguridad HTTP Bearer para Swagger UI
security = HTTPBearer(
    scheme_name="Bearer Token",
    description="Ingrese el token JWT obtenido del endpoint /api/v1/auth/login",
)

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
        JWE_SECRET_KEY.encode("utf-8"),
        algorithm=JWE_ALGORITHM,
        encryption=JWE_ENCRYPTION,
    )

    # Convertir bytes a string si es necesario
    if isinstance(token_bytes, bytes):
        token = token_bytes.decode("utf-8")
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
        payload_str = jwe.decrypt(token, JWE_SECRET_KEY.encode("utf-8"))
        payload = json.loads(payload_str)

        # Verificar expiración
        exp_timestamp = payload.get("exp")
        current_time = datetime.now(timezone.utc)

        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)

            if exp_datetime < current_time:
                logger.warning("Token JWE expirado")
                return None

        return payload

    except Exception as e:
        logger.error(f"Error verificando token JWE: {str(e)}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Dependency para obtener el usuario actual desde el token JWE en el header Authorization.
    Valida tanto el token JWE como la sesión activa en Redis.

    Args:
        credentials: Credenciales HTTP Bearer extraídas automáticamente del header Authorization

    Returns:
        Datos del usuario si el token es válido y la sesión existe en Redis

    Raises:
        HTTPException: Si el token no es válido, no está presente, o la sesión no existe
    """
    # El token ya está extraído por HTTPBearer
    token = credentials.credentials

    # Verificar token JWE
    payload = verify_jwe_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = payload.get("user", {})
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Datos de usuario no encontrados en token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validar sesión en Redis (verificar que no haya hecho logout)
    from app.services.auth_service import auth_service

    user_email = user_data.get("email")

    if user_email:
        is_session_active = await auth_service.is_authenticated(
            user_id=user_email, session_type="web"
        )

        if not is_session_active:
            raise HTTPException(
                status_code=401,
                detail="Sesión inválida o expirada. Por favor, inicie sesión nuevamente.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return {"user": user_data, "exp": payload.get("exp"), "iat": payload.get("iat")}


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


@router.post(
    "/microsoft/url",
    response_model=MicrosoftUrlResponse,
    summary="Iniciar autenticación con Microsoft con URL de retorno personalizada",
    description="""Inicia el flujo de autenticación con Microsoft y retorna la URL de autenticación.
    
    Este endpoint:
    1. Recibe una URL de retorno donde se redirigirá al usuario después del login
    2. Guarda la URL en Redis con un identificador único (24 horas de expiración)
    3. Retorna la URL de Microsoft para que el cliente redirija manualmente
    4. Al completar la autenticación, Microsoft redirige al callback que redirige a la URL especificada con el token JWT
    
    Ejemplo de uso:
    ```javascript
    const response = await fetch('/auth/microsoft/url', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({redirect_url: 'https://miapp.com/callback'})
    });
    const data = await response.json();
    window.location.href = data.auth_url; // Redirigir manualmente
    ```
    
    Resultado final:
    Después de la autenticación, el usuario será redirigido a: https://miapp.com/callback?token=eyJhbGc...
    """,
    responses={
        200: {
            "model": MicrosoftUrlResponse,
            "description": "URL de autenticación generada exitosamente",
        },
        400: {"description": "URL de retorno inválida o faltante"},
        500: {"description": "Error interno del servidor"},
    },
)
async def microsoft_login_with_redirect(data: MicrosoftUrlRequest):
    """Inicia autenticación con Microsoft con URL de retorno personalizada."""
    try:
        redirect_url = data.redirect_url

        # Validar que la URL sea válida
        try:
            parsed = urlparse(redirect_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("URL inválida")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="redirect_url debe ser una URL válida (ej: https://ejemplo.com/callback)",
            )

        # Validar credenciales de Azure AD
        if not all(
            [
                settings.azure_client_id,
                settings.azure_tenant_id,
                settings.azure_client_secret,
            ]
        ):
            logger.error("Credenciales de Azure AD no configuradas")
            raise HTTPException(
                status_code=500,
                detail="Autenticación con Microsoft no está configurada",
            )

        # Generar identificador único para este flujo
        import uuid

        flow_id = str(uuid.uuid4())

        # Guardar URL de retorno en Redis (expira en 24 horas)
        redis_key = f"microsoft_redirect:{flow_id}"
        await redis_client.set(
            redis_key,
            {
                "redirect_url": redirect_url,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            expires_in_seconds=86400,  # 24 horas
        )

        logger.info(
            f"✅ URL de redirección guardada en Redis: {flow_id} -> {redirect_url}"
        )

        # Crear state con el flow_id para identificar este flujo
        state_data = {"flow_type": "url_redirect", "flow_id": flow_id}
        state_encoded = base64.urlsafe_b64encode(
            json.dumps(state_data).encode()
        ).decode()

        # Construir URL de autorización de Microsoft
        base_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/authorize"

        params = {
            "client_id": settings.azure_client_id,
            "response_type": "code",
            "redirect_uri": settings.effective_microsoft_redirect_uri,
            "scope": "openid profile email User.Read",
            "response_mode": "query",
            "state": state_encoded,
        }

        auth_url = f"{base_url}?{urlencode(params)}"

        # Retornar JSON con la URL (el cliente debe redirigir manualmente)
        return MicrosoftUrlResponse(
            success=True,
            message="URL de autenticación generada exitosamente",
            auth_url=auth_url,
            flow_id=flow_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en microsoft_login_with_redirect: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get(
    "/microsoft",
    summary="Iniciar autenticación con Microsoft",
    description="Redirige al usuario a Microsoft Azure AD para autenticación OAuth2",
)
async def microsoft_login():
    """Endpoint para iniciar el flujo de autenticación con Microsoft."""
    try:
        # Validar que las credenciales de Azure AD estén configuradas
        if not all(
            [
                settings.azure_client_id,
                settings.azure_tenant_id,
                settings.azure_client_secret,
            ]
        ):
            logger.error("Credenciales de Azure AD no configuradas")
            raise HTTPException(
                status_code=500,
                detail="Autenticación con Microsoft no está configurada",
            )

        # Construir URL de autorización de Microsoft
        base_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/authorize"

        # Parámetros para la autenticación OAuth2
        params = {
            "client_id": settings.azure_client_id,
            "response_type": "code",
            "redirect_uri": settings.effective_microsoft_redirect_uri,
            "scope": "openid profile email User.Read",
            "response_mode": "query",
            "state": "security_token_here",  # En producción, usar un token seguro
        }

        # Construir URL completa
        from urllib.parse import urlencode

        auth_url = f"{base_url}?{urlencode(params)}"

        # Redirigir al usuario a Microsoft
        return RedirectResponse(url=auth_url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al construir URL de Microsoft: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


def _create_whatsapp_error_page(
    error_title: str, error_message: str, status_code: int = 400
):
    """Crea una página HTML de error para el flujo de WhatsApp."""
    from fastapi.responses import HTMLResponse

    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{error_title} - Ezekl Budget</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                }}
                h1 {{ color: #e74c3c; }}
                p {{ color: #555; line-height: 1.6; }}
                .icon {{ font-size: 60px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">❌</div>
                <h1>{error_title}</h1>
                <p>{error_message}</p>
                <p>Por favor, intenta nuevamente desde WhatsApp.</p>
            </div>
        </body>
        </html>
        """,
        status_code=status_code,
    )


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
            return HTMLResponse(
                content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Error de Autenticación - Ezekl Budget</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }}
                        .container {{
                            background: white;
                            padding: 40px;
                            border-radius: 12px;
                            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                            text-align: center;
                            max-width: 500px;
                        }}
                        h1 {{ color: #e74c3c; }}
                        p {{ color: #555; line-height: 1.6; }}
                        .icon {{ font-size: 60px; margin-bottom: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">❌</div>
                        <h1>Error de Autenticación</h1>
                        <p>No se pudo completar la autenticación con Microsoft.</p>
                        <p><strong>Error:</strong> {error_description or error}</p>
                    </div>
                </body>
                </html>
                """,
                status_code=400,
            )

        # 2. Validar que tenemos el código de autorización
        if not code:
            logger.error("No se recibió código de autorización de Microsoft")
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Error - Ezekl Budget</title>
                    <meta charset="UTF-8">
                    <style>
                        body { font-family: Arial; text-align: center; padding: 50px; }
                        h1 { color: #e74c3c; }
                    </style>
                </head>
                <body>
                    <h1>❌ Error</h1>
                    <p>No se recibió código de autorización.</p>
                </body>
                </html>
                """,
                status_code=400,
            )

        # 3. Recuperar URL de redirección desde Redis
        redis_key = f"microsoft_redirect:{flow_id}"
        redirect_data = await redis_client.get(redis_key)

        if not redirect_data:
            logger.error(f"No se encontró URL de redirección para flow_id: {flow_id}")
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Sesión Expirada - Ezekl Budget</title>
                    <meta charset="UTF-8">
                    <style>
                        body { font-family: Arial; text-align: center; padding: 50px; }
                        h1 { color: #e74c3c; }
                    </style>
                </head>
                <body>
                    <h1>⏰ Sesión Expirada</h1>
                    <p>La sesión de autenticación ha expirado. Por favor, intenta nuevamente.</p>
                </body>
                </html>
                """,
                status_code=400,
            )

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
                    return HTMLResponse(
                        content=f"""
                        <!DOCTYPE html>
                        <html>
                        <head><title>Error - Ezekl Budget</title></head>
                        <body style="font-family: Arial; text-align: center; padding: 50px;">
                            <h1>❌ Error</h1>
                            <p>No se pudo obtener el token de acceso.</p>
                        </body>
                        </html>
                        """,
                        status_code=500,
                    )

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
                    return HTMLResponse(
                        content="""
                        <!DOCTYPE html>
                        <html>
                        <head><title>Error - Ezekl Budget</title></head>
                        <body style="font-family: Arial; text-align: center; padding: 50px;">
                            <h1>❌ Error</h1>
                            <p>No se pudieron obtener los datos del usuario.</p>
                        </body>
                        </html>
                        """,
                        status_code=500,
                    )

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
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head><title>Error - Ezekl Budget</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>❌ Error</h1>
                    <p>No se pudo procesar la autenticación (respuesta vacía del servidor).</p>
                </body>
                </html>
                """,
                status_code=500,
            )

        # Verificar success (puede ser 1, True, "success", etc.)
        success = result.get("success")
        if not success or (isinstance(success, (int, bool)) and not success):
            error_msg = result.get("message", "Error desconocido")
            logger.error(f"❌ Error en spLoginMicrosoftAddOrEdit: {error_msg}")
            return HTMLResponse(
                content=f"""
                <!DOCTYPE html>
                <html>
                <head><title>Error - Ezekl Budget</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>❌ Error</h1>
                    <p>No se pudo procesar la autenticación.</p>
                    <p><small>{error_msg}</small></p>
                </body>
                </html>
                """,
                status_code=500,
            )

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

            return HTMLResponse(
                content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Asociación Requerida - Ezekl Budget</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }}
                        .container {{
                            background: white;
                            padding: 40px;
                            border-radius: 12px;
                            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                            text-align: center;
                            max-width: 500px;
                        }}
                        h1 {{ color: #f39c12; }}
                        p {{ color: #555; line-height: 1.6; }}
                        .icon {{ font-size: 60px; margin-bottom: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">⚠️</div>
                        <h1>Cuenta No Asociada</h1>
                        <p>Tu cuenta de Microsoft ({microsoft_user.get('email')}) no está asociada a ninguna cuenta del sistema.</p>
                        <p>Por favor, contacta al administrador para asociar tu cuenta.</p>
                    </div>
                </body>
                </html>
                """,
                status_code=403,
            )

        logger.info(f"👤 Datos del usuario para token: {user_login_data}")

        if not user_login_data or not isinstance(user_login_data, dict):
            logger.error(
                f"❌ No se obtuvieron datos válidos del usuario. Tipo: {type(user_login_data)}, Valor: {user_login_data}"
            )
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head><title>Error - Ezekl Budget</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>❌ Error</h1>
                    <p>No se pudieron obtener los datos del usuario.</p>
                </body>
                </html>
                """,
                status_code=500,
            )

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
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>Error - Ezekl Budget</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>❌ Error del Servidor</h1>
                <p>Ocurrió un error inesperado. Por favor, intenta nuevamente.</p>
            </body>
            </html>
            """,
            status_code=500,
        )


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
            return HTMLResponse(
                content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Asociar Cuenta - Ezekl Budget</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                        text-align: center;
                        max-width: 500px;
                        width: 90%;
                    }}
                    .icon {{ font-size: 60px; margin-bottom: 20px; }}
                    h1 {{
                        color: #333;
                        margin-bottom: 10px;
                        font-size: 28px;
                    }}
                    .user-info {{
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                    }}
                    .user-name {{
                        font-size: 20px;
                        font-weight: 600;
                        color: #2c3e50;
                        margin-bottom: 5px;
                    }}
                    .user-email {{
                        color: #7f8c8d;
                        font-size: 14px;
                    }}
                    .form-group {{
                        margin: 25px 0;
                        text-align: left;
                    }}
                    label {{
                        display: block;
                        margin-bottom: 8px;
                        color: #555;
                        font-weight: 500;
                    }}
                    input {{
                        width: 100%;
                        padding: 12px;
                        border: 2px solid #e0e0e0;
                        border-radius: 8px;
                        font-size: 16px;
                        box-sizing: border-box;
                        transition: border-color 0.3s;
                    }}
                    input:focus {{
                        outline: none;
                        border-color: #667eea;
                    }}
                    .button-group {{
                        display: flex;
                        gap: 10px;
                        margin-top: 25px;
                    }}
                    button {{
                        flex: 1;
                        padding: 15px 30px;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }}
                    .btn-primary {{
                        background: #667eea;
                        color: white;
                    }}
                    .btn-primary:hover {{
                        background: #5568d3;
                        transform: translateY(-2px);
                        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                    }}
                    .btn-secondary {{
                        background: #95a5a6;
                        color: white;
                    }}
                    .btn-secondary:hover {{
                        background: #7f8c8d;
                    }}
                    .error {{
                        color: #e74c3c;
                        font-size: 14px;
                        margin-top: 10px;
                        display: none;
                    }}
                    .info {{
                        background: #e3f2fd;
                        color: #1976d2;
                        padding: 15px;
                        border-radius: 8px;
                        margin-bottom: 20px;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">🔗</div>
                    <h1>Asociar Cuenta</h1>
                    
                    <div class="user-info">
                        <div class="user-name">{display_name}</div>
                        <div class="user-email">{email}</div>
                    </div>
                    
                    <div class="info">
                        <strong>Primera vez con Microsoft</strong><br>
                        Ingresa tu código de usuario existente para vincular tu cuenta de Microsoft.
                    </div>
                    
                    <form id="associateForm">
                        <div class="form-group">
                            <label for="codeLogin">Código de Usuario:</label>
                            <input 
                                type="text" 
                                id="codeLogin" 
                                name="codeLogin" 
                                placeholder="Ej: USR001"
                                required
                                autofocus
                            >
                        </div>
                        
                        <div class="error" id="errorMessage"></div>
                        
                        <div class="button-group">
                            <button type="button" class="btn-secondary" onclick="window.location.href='https://wa.me/{wa_number}'">
                                Cancelar
                            </button>
                            <button type="submit" class="btn-primary">
                                Asociar Cuenta
                            </button>
                        </div>
                    </form>
                </div>
                
                <script>
                    document.getElementById('associateForm').addEventListener('submit', async function(e) {{
                        e.preventDefault();
                        
                        const codeLogin = document.getElementById('codeLogin').value.trim();
                        const errorDiv = document.getElementById('errorMessage');
                        const submitBtn = e.target.querySelector('.btn-primary');
                        
                        if (!codeLogin) {{
                            errorDiv.textContent = 'Por favor ingresa tu código de usuario';
                            errorDiv.style.display = 'block';
                            return;
                        }}
                        
                        // Deshabilitar botón durante la petición
                        submitBtn.disabled = true;
                        submitBtn.textContent = 'Asociando...';
                        errorDiv.style.display = 'none';
                        
                        try {{
                            const response = await fetch('/api/auth/microsoft/associate/whatsapp', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json'
                                }},
                                body: JSON.stringify({{
                                    codeLogin: codeLogin,
                                    codeLoginMicrosoft: '{code_login_microsoft}',
                                    phoneNumber: '{phone_number}',
                                    whatsappToken: '{whatsapp_token}'
                                }})
                            }});
                            
                            const data = await response.json();
                            
                            if (response.ok && data.success) {{
                                // Mostrar éxito y redirigir a WhatsApp
                                document.querySelector('.container').innerHTML = `
                                    <div class="icon">✅</div>
                                    <h1>¡Cuenta Asociada!</h1>
                                    <div class="user-info">
                                        <div class="user-name">${{data.user.name || '{display_name}'}}</div>
                                        <div class="user-email">${{data.user.email || '{email}'}}</div>
                                    </div>
                                    <p>Tu cuenta de Microsoft está ahora vinculada.</p>
                                    <p>Tu sesión es válida por 24 horas.</p>
                                    <button onclick="window.location.href='https://wa.me/{wa_number}?text=Hola'" class="btn-primary" style="margin-top: 20px;">
                                        Volver a WhatsApp
                                    </button>
                                `;
                            }} else {{
                                errorDiv.textContent = data.message || data.detail || 'Error al asociar la cuenta';
                                errorDiv.style.display = 'block';
                                submitBtn.disabled = false;
                                submitBtn.textContent = 'Asociar Cuenta';
                            }}
                        }} catch (error) {{
                            errorDiv.textContent = 'Error de conexión. Por favor intenta nuevamente.';
                            errorDiv.style.display = 'block';
                            submitBtn.disabled = false;
                            submitBtn.textContent = 'Asociar Cuenta';
                        }}
                    }});
                </script>
            </body>
            </html>
            """
            )

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
            return HTMLResponse(
                content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Autenticación Exitosa - Ezekl Budget</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                        text-align: center;
                        max-width: 500px;
                    }}
                    h1 {{
                        color: #27ae60;
                        margin-bottom: 20px;
                    }}
                    p {{
                        color: #555;
                        line-height: 1.6;
                        margin-bottom: 15px;
                    }}
                    .icon {{
                        font-size: 80px;
                        margin-bottom: 20px;
                        animation: bounce 1s ease infinite;
                    }}
                    @keyframes bounce {{
                        0%, 100% {{ transform: translateY(0); }}
                        50% {{ transform: translateY(-10px); }}
                    }}
                    .user-info {{
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 20px 0;
                    }}
                    .user-name {{
                        font-weight: bold;
                        color: #667eea;
                        font-size: 18px;
                        margin-bottom: 5px;
                    }}
                    .user-email {{
                        color: #666;
                        font-size: 14px;
                    }}
                    .phone {{
                        background: #e8f5e9;
                        padding: 10px 20px;
                        border-radius: 6px;
                        display: inline-block;
                        margin-top: 15px;
                        font-family: monospace;
                        color: #27ae60;
                        font-weight: bold;
                    }}
                    .instruction {{
                        margin-top: 25px;
                        padding-top: 25px;
                        border-top: 2px solid #eee;
                        color: #666;
                        font-size: 15px;
                    }}
                    .whatsapp-button {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 15px 30px;
                        background: #25D366;
                        color: white;
                        text-decoration: none;
                        border-radius: 50px;
                        font-weight: bold;
                        font-size: 16px;
                        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
                        transition: all 0.3s ease;
                    }}
                    .whatsapp-button:hover {{
                        background: #20BA5A;
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(37, 211, 102, 0.5);
                    }}
                    .whatsapp-icon {{
                        display: inline-block;
                        margin-right: 8px;
                        font-size: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">✅</div>
                    <h1>¡Autenticación Exitosa!</h1>
                    <p>Tu cuenta de WhatsApp ha sido autenticada correctamente.</p>
                    
                    <div class="user-info">
                        <div class="user-name">{user_login_data.get('name', 'Usuario')}</div>
                        <div class="user-email">{user_login_data.get('email', '')}</div>
                    </div>
                    
                    <p>WhatsApp asociado:</p>
                    <div class="phone">+{phone_number}</div>
                    
                    <div class="instruction">
                        <p><strong>¡Todo listo!</strong></p>
                        <p>Ahora puedes usar el bot sin restricciones. Tu sesión es válida por 24 horas.</p>
                        <a href="https://wa.me/{wa_number}?text=Hola" class="whatsapp-button">
                            <span class="whatsapp-icon">💬</span>
                            Volver a WhatsApp
                        </a>
                    </div>
                </div>
            </body>
            </html>
            """
            )

        else:
            logger.error(f"Estado de asociación desconocido: {association_status}")
            return HTMLResponse(
                content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error - Ezekl Budget</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                        text-align: center;
                        max-width: 500px;
                    }
                    h1 { color: #e74c3c; }
                    p { color: #555; line-height: 1.6; }
                    .icon { font-size: 60px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">❌</div>
                    <h1>Error de Autenticación</h1>
                    <p>No se pudo completar la autenticación.</p>
                    <p>Por favor, contacta al administrador del sistema.</p>
                </div>
            </body>
            </html>
            """,
                status_code=500,
            )

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
    elif is_whatsapp_auth:
        return await microsoft_callback_whatsapp(
            code, state, error, error_description, whatsapp_data
        )
    else:
        return await microsoft_callback_normal(code, state, error, error_description)


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
                status_code=400, detail="codeLogin y codeLoginMicrosoft son requeridos"
            )

        # Preparar parámetros para el stored procedure de asociación
        association_data = {
            "codeLogin": code_login,
            "codeLoginMicrosoft": code_login_microsoft,
        }

        json_param = json.dumps(association_data)
        result = await execute_stored_procedure(
            "spLoginLoginMicrosoftAssociate", json_param
        )

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
                status_code=500, detail="Error obteniendo datos del usuario"
            )

        # Crear token JWE para el usuario
        jwe_token, expiry_date = create_jwe_token(user_data)

        # Guardar sesión en Redis también
        from app.services.auth_service import auth_service

        user_email = user_data.get("email")
        if user_email:
            await auth_service.save_session(
                user_id=user_email,
                user_data=user_data,
                session_type="web",
                expires_in_seconds=86400,  # 24 horas
            )

        return LoginResponse(
            success=True,
            message="Autenticación exitosa",
            user=UserData(**user_data),
            accessToken=jwe_token,
            expiresAt=expiry_date.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en asociación Microsoft: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post(
    "/microsoft/associate/whatsapp",
    summary="Asociar cuenta Microsoft con usuario existente (WhatsApp)",
    description="""Endpoint específico para asociar cuenta Microsoft desde WhatsApp.
    
    Similar a /microsoft/associate pero:
    1. Valida el token temporal de WhatsApp
    2. Asocia las cuentas usando spLoginLoginMicrosoftAssociate
    3. Crea sesión en Redis para WhatsApp (no devuelve token JWE)
    4. Retorna éxito para que el frontend redirija a WhatsApp
    """,
)
async def associate_microsoft_account_whatsapp(data: dict):
    """
    Asocia cuenta Microsoft con usuario existente y crea sesión de WhatsApp.

    Args:
        data: {
            "codeLogin": "USR001",
            "codeLoginMicrosoft": "uuid-microsoft",
            "phoneNumber": "5491112345678",
            "whatsappToken": "token-temporal"
        }

    Returns:
        {"success": True, "message": "...", "user": {...}}
    """
    try:
        code_login = data.get("codeLogin")
        code_login_microsoft = data.get("codeLoginMicrosoft")
        phone_number = data.get("phoneNumber")
        whatsapp_token = data.get("whatsappToken")

        if not all([code_login, code_login_microsoft, phone_number, whatsapp_token]):
            raise HTTPException(
                status_code=400, detail="Todos los campos son requeridos"
            )

        # Validar token temporal de WhatsApp
        from app.services.whatsapp_service import whatsapp_service

        token_data = await whatsapp_service.get_phone_from_auth_token(whatsapp_token)

        if not token_data or token_data[0] != phone_number:
            raise HTTPException(
                status_code=401, detail="Token de WhatsApp inválido o expirado"
            )

        # Ejecutar SP de asociación
        association_data = {
            "codeLogin": code_login,
            "codeLoginMicrosoft": code_login_microsoft,
        }

        json_param = json.dumps(association_data)
        result = await execute_stored_procedure(
            "spLoginLoginMicrosoftAssociate", json_param
        )

        if not result.get("success"):
            error_message = result.get("message", "Error en la asociación")
            logger.error(f"Error en asociación WhatsApp: {error_message}")

            if (
                "not found" in error_message.lower()
                or "no encontrado" in error_message.lower()
            ):
                raise HTTPException(status_code=404, detail=error_message)
            elif (
                "already associated" in error_message.lower()
                or "ya está asociada" in error_message.lower()
            ):
                raise HTTPException(status_code=409, detail=error_message)
            else:
                raise HTTPException(status_code=400, detail=error_message)

        # Obtener datos del usuario asociado
        user_data = result.get("userData", {})

        if not user_data:
            raise HTTPException(
                status_code=500, detail="Error obteniendo datos del usuario"
            )

        # Guardar sesión de WhatsApp en Redis (24 horas)
        await whatsapp_service.save_whatsapp_auth(
            phone_number=phone_number, user_data=user_data, expires_in_seconds=86400
        )

        # Eliminar token temporal (ya fue usado)
        await whatsapp_service.delete_auth_token(whatsapp_token)

        logger.info(
            f"✅ Cuenta Microsoft asociada y sesión WhatsApp creada para {phone_number}"
        )

        return {
            "success": True,
            "message": "Cuenta asociada exitosamente",
            "user": user_data,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en asociación Microsoft WhatsApp: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
