"""
Endpoints HTTP de la API ezekl-budget.
Estructura preparada para escalar con múltiples rutas organizadas.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from app.core.config import settings
from app.database.connection import test_db_connection
from app.models.responses import CredentialsResponse, RealtimeCredentialsResponse, HealthCheckResponse
from .email import router as email_router
from .auth import router as auth_router, get_current_user
from .accounting_account import router as accounting_account_router
from .company import router as company_router
from .whatsapp import router as whatsapp_router
from .ai import router as ai_router
from .copilot import router as copilot_router
from .exam_question import router as exam_question_router

# Importar routers CRM
from app.api.crm import cases_router, accounts_router, contacts_router, system_router, webhook_router

# Router principal para todos los endpoints de la API
router = APIRouter()

# Incluir routers de módulos específicos
router.include_router(email_router, prefix="/email", tags=["correo"])
router.include_router(auth_router, prefix="/auth", tags=["autenticación"])
router.include_router(accounting_account_router, prefix="/accounting-accounts", tags=["cuentas-contables"])
router.include_router(company_router, prefix="/companies", tags=["compañías"])
router.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])
router.include_router(ai_router, prefix="/ai", tags=["inteligencia-artificial"])
router.include_router(copilot_router, tags=["asistente-ia"])
router.include_router(exam_question_router, prefix="/exam-questions", tags=["preguntas-examen"])

# Incluir routers CRM con prefijo /crm
router.include_router(cases_router, prefix="/crm", tags=["CRM - Casos"])
router.include_router(accounts_router, prefix="/crm", tags=["CRM - Cuentas"])  
router.include_router(contacts_router, prefix="/crm", tags=["CRM - Contactos"])
router.include_router(system_router, prefix="/crm", tags=["CRM - Sistema"])
router.include_router(webhook_router, prefix="/crm", tags=["CRM - Webhook"])


@router.get(
    "/credentials/websocket",
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
    "/credentials/realtime",
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
async def get_realtime_credentials(current_user: Dict = Depends(get_current_user)):
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
        "email_queue": email_queue_stats,
        "components": {
            "api": "healthy", 
            "database": db_status,
            "email_queue": email_queue_status
        },
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
# router.include_router(auth_router, prefix="/auth", tags=["autenticación"])
# router.include_router(budget_router, prefix="/budget", tags=["presupuestos"])

