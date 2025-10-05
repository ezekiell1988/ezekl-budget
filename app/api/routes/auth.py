"""
Endpoints de autenticación para el sistema Ezekl Budget.
Maneja el flujo de login de 2 pasos con tokens temporales y JWE.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import logging
import json
from jose import jwe
from app.core.config import settings
from app.database.connection import execute_sp
from app.services.email_service import send_notification_email
from app.services.email_queue import queue_email
import secrets
import string

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de autenticación
router = APIRouter()

# Clave secreta para JWE (en producción debe venir de variables de entorno)
JWE_SECRET_KEY = getattr(
    settings, "jwe_secret_key", "your-256-bit-secret-key-change-in-production!"
)
JWE_ALGORITHM = "A256KW"
JWE_ENCRYPTION = "A256GCM"

# Configuración de token
TOKEN_EXPIRY_HOURS = 24  # Token JWE válido por 24 horas


class AuthModels:
    """Modelos de request/response para autenticación"""

    class RequestTokenRequest:
        def __init__(self, codeLogin: str):
            self.codeLogin = codeLogin

    class RequestTokenResponse:
        def __init__(
            self,
            success: bool,
            message: str,
            user: Dict = None,
            tokenGenerated: bool = False,
        ):
            self.success = success
            self.message = message
            self.user = user
            self.tokenGenerated = tokenGenerated

    class LoginRequest:
        def __init__(self, codeLogin: str, token: str):
            self.codeLogin = codeLogin
            self.token = token

    class LoginResponse:
        def __init__(
            self,
            success: bool,
            message: str,
            user: Dict = None,
            accessToken: str = None,
            expiresAt: str = None,
        ):
            self.success = success
            self.message = message
            self.user = user
            self.accessToken = accessToken
            self.expiresAt = expiresAt


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

    # Crear token JWE
    token = jwe.encrypt(
        json.dumps(payload),
        JWE_SECRET_KEY,
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
        # Decodificar token JWE
        payload_str = jwe.decrypt(token, JWE_SECRET_KEY)
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
async def request_token(data: Dict[str, str]):
    """
    Solicita un token de acceso temporal para el usuario.

    Args:
        data: {"codeLogin": "codigo_usuario"}

    Returns:
        RequestTokenResponse con resultado de la operación
    """
    try:
        code_login = data.get("codeLogin")
        if not code_login:
            raise HTTPException(status_code=400, detail="codeLogin es requerido")

        # Ejecutar spLoginTokenAdd para generar token
        json_param = json.dumps({"codeLogin": code_login})
        result = await execute_stored_procedure("spLoginTokenAdd", json_param)

        if not result.get("success", False):
            logger.warning(f"Fallo al generar token para {code_login}")
            return {
                "success": False,
                "message": "Código de usuario no encontrado",
                "tokenGenerated": False,
            }

        # Extraer datos del usuario y token
        auth_data = result.get("auth", {})
        token = result.get("token")

        if not token or not auth_data:
            logger.error("Respuesta inválida del procedimiento spLoginTokenAdd")
            return {
                "success": False,
                "message": "Error generando token",
                "tokenGenerated": False,
            }

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

        return {
            "success": True,
            "message": "Token enviado por email exitosamente",
            "tokenGenerated": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en request-token: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post(
    "/login",
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
async def login(data: Dict[str, str]):
    """
    Autentica al usuario usando codeLogin y token temporal.

    Args:
        data: {"codeLogin": "codigo", "token": "12345"}

    Returns:
        LoginResponse con token JWE y datos del usuario
    """
    try:
        code_login = data.get("codeLogin")
        token = data.get("token")

        if not code_login or not token:
            raise HTTPException(
                status_code=400, detail="codeLogin y token son requeridos"
            )

        # Ejecutar spLoginAuth para validar y eliminar token
        json_param = json.dumps({"codeLogin": code_login, "token": token})
        result = await execute_stored_procedure("spLoginAuth", json_param)

        if not result.get("success", False):
            logger.warning(f"Fallo de autenticación para {code_login}")
            return {
                "success": False,
                "message": "Credenciales inválidas o token expirado",
            }

        # Extraer datos del usuario
        auth_data = result.get("auth", {})

        if not auth_data:
            logger.error(
                "Datos de usuario no encontrados en respuesta de autenticación"
            )
            return {"success": False, "message": "Error en datos de autenticación"}

        # Generar token JWE
        access_token, expires_at = create_jwe_token(auth_data)

        logger.info(f"Login exitoso para usuario {code_login}")

        return {
            "success": True,
            "message": "Autenticación exitosa",
            "user": auth_data,
            "accessToken": access_token,
            "expiresAt": expires_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post(
    "/verify-token",
    summary="Verificar token de sesión",
    description="""Verifica si un token JWE de sesión es válido.
    
    Útil para:
    - Validar sesión en guards de autenticación
    - Refrescar datos del usuario
    - Verificar expiración antes de operaciones críticas
    """,
)
async def verify_token(data: Dict[str, str]):
    """
    Verifica la validez de un token JWE de sesión.

    Args:
        data: {"token": "jwe_token"}

    Returns:
        Resultado de la verificación con datos del usuario si es válido
    """
    try:
        token = data.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="Token es requerido")

        # Verificar token
        payload = verify_jwe_token(token)

        if not payload:
            return {"valid": False, "message": "Token inválido o expirado"}

        user_data = payload.get("user", {})
        exp_timestamp = payload.get("exp")

        return {
            "valid": True,
            "message": "Token válido",
            "user": user_data,
            "expiresAt": (
                datetime.fromtimestamp(exp_timestamp, timezone.utc).isoformat()
                if exp_timestamp
                else None
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verificando token: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post(
    "/logout",
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

        return {"success": True, "message": "Sesión cerrada exitosamente"}

    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
