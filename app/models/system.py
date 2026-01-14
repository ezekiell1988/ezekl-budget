"""
Modelos Pydantic para endpoints de sistema y monitoreo.
Contiene las estructuras de datos para operaciones de sistema.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ConfigResponse(BaseModel):
    """
    Modelo de respuesta para la configuración de la aplicación.
    
    Proporciona información básica que necesita el frontend Angular.
    """
    
    success: bool = Field(
        description="Indica si la configuración se cargó exitosamente",
        examples=[True]
    )
    
    nameCompany: str = Field(
        description="Nombre de la compañía",
        examples=["Ezekl Budget", "Demo"]
    )
    
    sloganCompany: str = Field(
        description="Slogan de la compañía",
        examples=["Presupuestos simplificados para todos"]
    )
    
    apiVersion: str = Field(
        description="Versión de la API",
        examples=["1.0.0", "1.2.3"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "success": True,
                "nameCompany": "Ezekl Budget",
                "sloganCompany": "Presupuestos simplificados para todos",
                "apiVersion": "1.0.0"
            }
        }


class HealthCheckResponse(BaseModel):
    """
    Modelo de respuesta para el health check del sistema.
    
    Proporciona información detallada sobre el estado de la aplicación
    y sus componentes críticos, incluyendo estadísticas de email queue.
    """
    
    status: str = Field(
        description="Estado general del sistema",
        examples=["healthy", "unhealthy"]
    )
    
    message: str = Field(
        description="Mensaje descriptivo del estado general",
        examples=["Ezekl Budget API está funcionando correctamente"]
    )
    
    version: str = Field(
        description="Versión actual de la aplicación",
        examples=["1.0.0", "1.2.3"]
    )

    domain: str = Field(
        description="Dominio o URL base del servidor",
        examples=["https://budget.ezekl.com"]
    )
    
    environment: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Información del entorno de ejecución"
    )
    
    database: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Estado de la conexión a base de datos"
    )
    
    email_queue: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Estadísticas de la cola de emails en background"
    )
    
    components: Optional[Dict[str, str]] = Field(
        default=None,
        description="Estado de componentes individuales del sistema"
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "Ezekl Budget API está funcionando correctamente",
                "version": "1.0.0",
                "domain": "https://budget.ezekl.com",
                "email_queue": {
                    "is_running": True,
                    "queue_size": 0,
                    "processed_count": 5,
                    "failed_count": 0,
                    "success_rate": 100.0
                },
                "components": {
                    "api": "healthy",
                    "database": "healthy", 
                    "email_queue": "healthy"
                }
            }
        }
