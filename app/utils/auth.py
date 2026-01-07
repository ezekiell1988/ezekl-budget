"""
Utilidades compartidas para autenticación.
Funciones reutilizables para tokens JWE, validación de usuarios y stored procedures.
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import logging
import json
from jose import jwe

from app.core.config import settings
from app.database.connection import execute_sp

# Configurar logging
logger = logging.getLogger(__name__)

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
