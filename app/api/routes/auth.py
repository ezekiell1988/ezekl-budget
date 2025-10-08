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
    token = jwe.encrypt(
        json.dumps(payload),
        JWE_SECRET_KEY.encode('utf-8'),
        algorithm=JWE_ALGORITHM,
        encryption=JWE_ENCRYPTION,
    )

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
async def microsoft_callback(code: str = None, state: str = None, error: str = None):
    """Endpoint callback para procesar la respuesta de Microsoft OAuth2."""
    try:
        logger.info(f"🔄 Procesando callback de Microsoft - Code: {bool(code)}, Error: {error}")
        
        # Verificar si hay errores en la respuesta
        if error:
            logger.warning(f"❌ Error en callback de Microsoft: {error}")
            # Redirigir al frontend con error
            return RedirectResponse(url="/#/login?microsoft_error=access_denied")
        
        if not code:
            logger.warning("❌ No se recibió código de autorización de Microsoft")
            return RedirectResponse(url="/#/login?microsoft_error=no_code")
        
        # Intercambiar código por token de acceso
        import httpx
        token_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/token"
        
        token_data = {
            "client_id": settings.azure_client_id,
            "client_secret": settings.azure_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "https://budget.ezekl.com/api/auth/microsoft/callback",
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_result = token_response.json()
        
        if token_response.status_code != 200:
            logger.error(f"❌ Error obteniendo token de Microsoft: {token_result}")
            return RedirectResponse(url="/#/login?microsoft_error=token_failed")
        
        access_token = token_result.get("access_token")
        if not access_token:
            logger.error("❌ No se recibió access_token de Microsoft")
            return RedirectResponse(url="/#/login?microsoft_error=no_token")
        
        # Obtener información del usuario de Microsoft Graph
        graph_url = "https://graph.microsoft.com/v1.0/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            user_response = await client.get(graph_url, headers=headers)
            user_data = user_response.json()
        
        if user_response.status_code != 200:
            logger.error(f"❌ Error obteniendo datos del usuario de Microsoft: {user_data}")
            return RedirectResponse(url="/#/login?microsoft_error=user_failed")
        
        # Extraer información del usuario
        microsoft_email = user_data.get("mail") or user_data.get("userPrincipalName")
        microsoft_name = user_data.get("displayName", "")
        
        logger.info(f"✅ Usuario autenticado con Microsoft: {microsoft_email} - {microsoft_name}")
        
        # Aquí deberías buscar al usuario en tu base de datos por email
        # y crear/actualizar su información según sea necesario
        
        # Por ahora, crear un token JWE temporal con los datos de Microsoft
        user_data_for_token = {
            "codeLogin": microsoft_email,  # Usar email como codeLogin temporal
            "name": microsoft_name,
            "email": microsoft_email,
            "position": "Usuario Microsoft",
            "department": "Externo",
            "permissions": ["user"]  # Permisos básicos
        }
        
        jwe_token, expiry_datetime = create_jwe_token(user_data_for_token)
        
        # Redirigir al frontend con el token
        from urllib.parse import urlencode
        redirect_params = {
            "microsoft_token": jwe_token,
            "microsoft_success": "true"
        }
        # Redirigir a la página de login donde está el código que maneja el callback de Microsoft
        redirect_url = f"/#/login?{urlencode(redirect_params)}"
        
        logger.info(f"🚀 Redirigiendo usuario autenticado al frontend: {microsoft_email}")
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"💥 Error inesperado en callback de Microsoft: {str(e)}")
        return RedirectResponse(url="/#/login?microsoft_error=internal_error")
