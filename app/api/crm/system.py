"""
Rutas de sistema y diagnóstico para el módulo CRM.
Proporciona endpoints para health check, diagnóstico y información del token.
"""

from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.auth import CurrentUser
from app.services.crm_service import crm_service
from app.services.crm_auth import crm_auth_service
from app.models.crm import CRMHealthResponse, CRMDiagnoseResponse, CRMTokenResponse
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["CRM - Sistema"])


@router.get(
    "/health",
    response_model=CRMHealthResponse,
    summary="Health Check del CRM",
    description="""
    Endpoint de health check para verificar el estado básico del servicio CRM.
    
    **🔒 Requiere Autenticación:** Este endpoint requiere un token JWT válido.
    
    **Funcionalidad:**
    - Verifica la configuración básica del servicio
    - Retorna información de la instancia de Dynamics 365 configurada
    - Indica la versión de la API en uso
    
    **Estados posibles:**
    - `ok`: Servicio configurado correctamente
    - `error`: Falta configuración o hay problemas
    
    **Uso recomendado:**
    - Monitoreo de servicios
    - Verificación rápida de configuración
    - Debugging inicial
    """,
    responses={
        200: {"description": "Estado del servicio CRM"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error interno del servidor"}
    }
)
async def health_check(
    current_user: CurrentUser = Depends(get_current_user)
):
    """Health check básico del servicio CRM."""
    
    try:
        
        result = await crm_service.health_check()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error en health check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en health check: {str(e)}")


@router.get(
    "/token",
    response_model=CRMTokenResponse,
    summary="Información del Token CRM",
    description="""
    Obtiene información del token de acceso actual para Dynamics 365.
    
    **⚠️ Nota de Seguridad:**
    Este endpoint solo muestra una vista previa parcial del token por seguridad.
    NO expone el token completo.
    
    **Información incluida:**
    - Vista previa del token (primeros y últimos caracteres)
    - Tiempo de expiración en timestamp Unix
    - Estado de validez del token
    
    **Uso recomendado:**
    - Debugging de problemas de autenticación
    - Verificación de expiración de tokens
    - Monitoreo de estado de autenticación
    """,
    responses={
        200: {"description": "Información del token obtenida"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error obteniendo información del token"}
    }
)
async def get_token_info(
    current_user: CurrentUser = Depends(get_current_user)
):
    """Obtiene información del token actual (para debugging)."""
    
    try:
        
        # Obtener token actual
        token = await crm_auth_service.get_access_token()
        token_info = crm_auth_service.get_token_info()
        
        # Crear vista previa segura del token
        token_preview = f"{token[:12]}...{token[-8:]}" if len(token) > 20 else "***"
        
        result = CRMTokenResponse(
            token_preview=token_preview,
            expires_at=token_info["expires_at"]
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo info del token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo token: {str(e)}")


@router.get(
    "/diagnose",
    response_model=CRMDiagnoseResponse,
    summary="Diagnóstico Completo del CRM",
    description="""
    Ejecuta un diagnóstico completo de la configuración y conectividad del CRM.
    
    **Verificaciones incluidas:**
    
    1. **Variables de entorno:**
       - Presencia de todas las variables CRM requeridas
       - Validación de formato básico
    
    2. **Adquisición de token:**
       - Capacidad de obtener token de Azure AD
       - Validez y tiempo de expiración del token
    
    3. **Conectividad con Dynamics 365:**
       - Prueba de conexión con la API de D365
       - Verificación de permisos mediante WhoAmI
       - Información de usuario y organización
    
    **Recomendaciones automáticas:**
    - Identificación de problemas comunes
    - Sugerencias de configuración
    - Pasos de solución de problemas
    
    **Uso recomendado:**
    - Configuración inicial del CRM
    - Troubleshooting de problemas de conectividad
    - Auditoría de configuración
    """,
    responses={
        200: {"description": "Diagnóstico completado"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error ejecutando diagnóstico"}
    }
)
async def diagnose_crm(
    current_user: CurrentUser = Depends(get_current_user)
):
    """Ejecuta un diagnóstico completo del servicio CRM."""
    
    try:
        
        result = await crm_service.diagnose()
        
        # Log del resultado del diagnóstico
        env_status = result.environment_variables
        token_status = result.token_acquisition.get("status", "Unknown")
        d365_status = result.d365_connectivity.get("status", "Unknown")
        
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error ejecutando diagnóstico: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en diagnóstico: {str(e)}")


@router.post(
    "/clear-cache",
    summary="Limpiar Caché de Token",
    description="""
    Limpia el caché del token de acceso CRM.
    
    **Funcionalidad:**
    - Elimina el token actual del caché en memoria
    - Fuerza la obtención de un nuevo token en la próxima petición
    - Útil para resolver problemas de tokens expirados o corruptos
    
    **Casos de uso:**
    - Troubleshooting de problemas de autenticación
    - Forzar renovación de token
    - Testing y desarrollo
    
    **⚠️ Nota:**
    Esto no invalida el token en Azure AD, solo lo elimina del caché local.
    """,
    responses={
        200: {"description": "Caché limpiado exitosamente"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error limpiando caché"}
    }
)
async def clear_token_cache(
    current_user: CurrentUser = Depends(get_current_user)
):
    """Limpia el caché del token CRM."""
    
    try:
        
        crm_auth_service.clear_token_cache()
        
        return {"status": "success", "message": "Caché del token CRM limpiado exitosamente"}
        
    except Exception as e:
        logger.error(f"❌ Error limpiando caché: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error limpiando caché: {str(e)}")