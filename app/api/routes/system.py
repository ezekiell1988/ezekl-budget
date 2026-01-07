"""
Endpoints de sistema y monitoreo.
"""

from fastapi import APIRouter, HTTPException, Request
from app.core.config import settings
from app.database.connection import test_db_connection
from app.models.responses import HealthCheckResponse

router = APIRouter(tags=["Sistema"])


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
async def health_check(request: Request):
    """
    Endpoint de salud para verificar que la API y la base de datos están funcionando.

    Returns:
        dict: Estado de la aplicación incluyendo conexión a base de datos y cola de emails
    """
    import asyncio
    
    # Verificar conexión a base de datos de forma asíncrona
    db_status = "healthy" if await test_db_connection() else "unhealthy"
    
    # Obtener estadísticas de la cola de emails con timeout
    email_queue_stats = None
    email_queue_status = "unknown"
    
    try:
        # Import local para evitar problemas circulares
        from app.services.email_queue import email_queue
        
        # Usar wait_for con timeout de 2 segundos para evitar deadlock
        email_queue_stats = await asyncio.wait_for(
            email_queue.get_stats(), 
            timeout=2.0
        )
        email_queue_status = "healthy" if email_queue_stats["is_running"] else "unhealthy"
        
    except asyncio.TimeoutError:
        email_queue_stats = {
            "error": "Timeout accessing queue",
            "is_running": False,
            "queue_size": 0,
            "processed_count": 0,
            "failed_count": 0,
            "success_rate": 0.0
        }
        email_queue_status = "timeout"
    except Exception as e:
        email_queue_stats = {
            "error": str(e),
            "is_running": False,
            "queue_size": 0,
            "processed_count": 0,
            "failed_count": 0,
            "success_rate": 0.0
        }
        email_queue_status = "error"

    # Si la BD no está disponible, devolver error 503
    if db_status == "unhealthy":
        raise HTTPException(
            status_code=503,
            detail="Servicio no disponible: Error de conexión a base de datos",
        )

    # Obtener la URL base del servidor desde el request
    server_url = f"{request.url.scheme}://{request.url.netloc}"

    return {
        "status": "healthy",
        "message": "Ezekl Budget API está funcionando correctamente",
        "version": "1.0.0",
        "domain": server_url,
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
        "email_queue": email_queue_stats,
        "components": {
            "api": "healthy", 
            "database": db_status,
            "email_queue": email_queue_status
        },
    }
