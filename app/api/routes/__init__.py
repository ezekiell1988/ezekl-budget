"""
Endpoints HTTP de la API ezekl-budget.
Estructura preparada para escalar con múltiples rutas organizadas.
"""

from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.database.connection import test_db_connection
from app.models.responses import CredentialsResponse, HealthCheckResponse
from .email import router as email_router

# Router principal para todos los endpoints de la API
router = APIRouter()

# Incluir routers de módulos específicos
router.include_router(email_router, prefix="/email", tags=["email"])


@router.get(
    "/credentials",
    response_model=CredentialsResponse,
    summary="Obtener credenciales de Azure OpenAI",
    description="""Obtiene la configuración de credenciales de Azure OpenAI desde las variables de entorno.
    
    Este endpoint devuelve la información de configuración necesaria para conectar
    con los servicios de Azure OpenAI, excluyendo datos sensibles como las API keys.
    
    **Información devuelta:**
    - Endpoint de Azure OpenAI configurado
    - Nombre del deployment/modelo configurado
    - Mensaje de confirmación de carga exitosa
    
    **Seguridad:**
    - Las API keys y tokens sensibles NO son devueltos
    - Solo información de configuración pública
    - Ideal para validar configuración desde el frontend
    
    **Casos de uso:**
    - Verificar configuración de Azure OpenAI desde el cliente
    - Debugging de configuración de variables de entorno
    - Validación de conectividad con servicios Azure
    """,
    response_description="Configuración de credenciales de Azure OpenAI (sin datos sensibles)"
)
async def get_credentials():
    """
    Obtiene las credenciales de Azure OpenAI desde las variables de entorno.

    Returns:
        CredentialsResponse: Las credenciales configuradas (sin incluir la API key por seguridad)
    """
    return CredentialsResponse(
        azure_openai_endpoint=settings.azure_openai_endpoint,
        azure_openai_deployment_name=settings.azure_openai_deployment_name,
        message="Credenciales cargadas exitosamente desde .env",
    )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Verificación de salud del sistema",
    description="""Verifica el estado de salud de la aplicación y sus componentes críticos.
    
    Este endpoint realiza una verificación completa del estado del sistema,
    incluyendo la conectividad con la base de datos y otros servicios esenciales.
    
    **Componentes verificados:**
    - Estado general de la API
    - Conectividad con base de datos SQL Server
    - Configuración de entorno (producción vs desarrollo)
    - Host efectivo de base de datos
    
    **Códigos de respuesta:**
    - `200 OK`: Todos los componentes funcionan correctamente
    - `503 Service Unavailable`: La base de datos u otros servicios críticos no están disponibles
    
    **Información devuelta:**
    - Estado general del sistema (healthy/unhealthy)
    - Versión de la aplicación
    - Configuración de entorno actual
    - Estado detallado de cada componente
    - Información de conexión a base de datos
    
    **Uso recomendado:**
    - Monitoreo automatizado de servicios
    - Load balancers y health checks
    - Debugging de problemas de conectividad
    - Verificación post-deployment
    """,
    response_description="Estado detallado del sistema y todos sus componentes"
)
async def health_check():
    """
    Endpoint de salud para verificar que la API y la base de datos están funcionando.

    Returns:
        dict: Estado de la aplicación incluyendo conexión a base de datos
    """
    # Verificar conexión a base de datos de forma asíncrona
    db_status = "healthy" if await test_db_connection() else "unhealthy"

    # Si la BD no está disponible, devolver error 503
    if db_status == "unhealthy":
        raise HTTPException(
            status_code=503,
            detail="Servicio no disponible: Error de conexión a base de datos",
        )

    return {
        "status": "healthy",
        "message": "Ezekl Budget API está funcionando correctamente",
        "version": "1.0.0",
        "environment": {
            "is_production": settings.is_production,
            "configured_host": settings.db_host,
            "effective_host": settings.effective_db_host,
        },
        "database": {
            "status": db_status,
            "host": settings.effective_db_host,
            "database": settings.db_name,
        },
        "components": {"api": "healthy", "database": db_status},
    }


# 🚀 Estructura futura para escalar:
#
# Cuando tengas más endpoints, puedes crear archivos específicos:
# 
# api/routes/
# ├── __init__.py          # (este archivo - router principal)
# ├── auth.py              # /api/auth/* - endpoints de autenticación
# ├── budget.py            # /api/budget/* - gestión de presupuestos  
# ├── health.py            # /api/health - health check (separado)
# └── credentials.py       # /api/credentials - credenciales (separado)
#
# Y luego importar todos en este __init__.py:
# from .auth import router as auth_router
# from .budget import router as budget_router  
# router.include_router(auth_router, prefix="/auth", tags=["auth"])
# router.include_router(budget_router, prefix="/budget", tags=["budget"])

