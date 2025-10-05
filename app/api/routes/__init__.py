"""
Endpoints HTTP de la API ezekl-budget.
Estructura preparada para escalar con múltiples rutas organizadas.
"""

from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.database.connection import test_db_connection
from app.models.responses import CredentialsResponse

# Router principal para todos los endpoints de la API
router = APIRouter()


@router.get("/credentials", response_model=CredentialsResponse)
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


@router.get("/health")
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

