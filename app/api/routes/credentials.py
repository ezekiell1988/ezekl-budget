"""
Endpoints de credenciales para Azure OpenAI y WebSocket.
"""

from fastapi import APIRouter, Depends
from app.core.config import settings
from app.models.auth import CurrentUser
from app.models.responses import CredentialsResponse, RealtimeCredentialsResponse
from app.utils.auth import get_current_user

router = APIRouter(tags=["Credenciales"])


@router.get(
    "/websocket",
    response_model=CredentialsResponse,
    summary="Obtener configuración para WebSocket demo (Público)",
    description="""Obtiene la configuración básica para WebSocket de demostración.
    
    Este endpoint devuelve información de configuración del servidor necesaria
    para establecer conexiones WebSocket desde el cliente, especialmente útil
    para manejar diferencias entre sistemas operativos (Windows vs Linux).
    
    **Información devuelta:**
    - Endpoint de Azure OpenAI configurado
    - Nombre del deployment/modelo configurado
    - Sistema operativo del servidor (para configuración de WebSocket)
    - Mensaje de confirmación de carga exitosa
    
    **Casos de uso:**
    - Obtener SO del servidor para configuración de WebSocket en Windows
    - Configurar correctamente localhost vs 127.0.0.1
    - Debugging de configuración de variables de entorno
    """,
    response_description="Configuración básica del servidor para WebSocket"
)
async def get_websocket_credentials():
    """
    Obtiene las credenciales básicas para WebSocket demo desde las variables de entorno.

    Returns:
        CredentialsResponse: Las credenciales configuradas (sin incluir la API key por seguridad)
    """
    import platform
    
    return CredentialsResponse(
        azure_openai_endpoint=settings.azure_openai_endpoint,
        azure_openai_deployment_name=settings.azure_openai_deployment_name,
        message="Credenciales cargadas exitosamente desde .env",
        server_os=platform.system(),  # Windows, Linux, Darwin (macOS)
    )


@router.get(
    "/realtime",
    response_model=RealtimeCredentialsResponse,
    summary="Obtener credenciales para Azure OpenAI Realtime API (Privado)",
    description="""Obtiene las credenciales completas de Azure OpenAI Realtime API.
    
    🔒 **Este endpoint requiere autenticación.**
    
    Este endpoint devuelve la configuración necesaria para conectar con
    Azure OpenAI Realtime API, incluyendo endpoint, deployment y API key.
    
    **Información devuelta:**
    - Endpoint de Azure OpenAI
    - Nombre del deployment/modelo (gpt-realtime)
    - API key de Azure OpenAI (SENSIBLE)
    - Sistema operativo del servidor
    
    **Seguridad:**
    - Requiere token JWE válido en header Authorization
    - Devuelve API key sensible - usar solo en conexiones seguras
    
    **Casos de uso:**
    - Establecer conexión WebSocket con Azure OpenAI Realtime API
    - Chat en tiempo real con audio y texto
    - Implementaciones de Voice Activity Detection (VAD)
    """,
    response_description="Credenciales completas para Azure OpenAI Realtime API"
)
async def get_realtime_credentials(current_user: CurrentUser = Depends(get_current_user)):
    """
    Obtiene las credenciales completas para Azure OpenAI Realtime API.
    
    Args:
        current_user: Usuario autenticado (inyectado por Depends)

    Returns:
        RealtimeCredentialsResponse: Credenciales completas incluyendo API key
    """
    import platform
    
    return RealtimeCredentialsResponse(
        azure_openai_endpoint=settings.azure_openai_endpoint,
        azure_openai_api_key=settings.azure_openai_api_key,
        azure_openai_deployment_name=settings.azure_openai_deployment_name,
        server_os=platform.system(),
        message="Credenciales de Azure OpenAI Realtime cargadas exitosamente"
    )
