"""
Modelos Pydantic para responses de la API.
Contiene todas las estructuras de datos para las respuestas salientes.
"""

from pydantic import BaseModel, Field
from typing import Optional


class CredentialsResponse(BaseModel):
    """
    Modelo de respuesta para las credenciales de Azure OpenAI.
    
    Proporciona información de configuración sin exponer datos sensibles
    como API keys o connection strings.
    """
    
    azure_openai_endpoint: str = Field(
        description="URL del endpoint de Azure OpenAI configurado",
        examples=["https://mi-openai.openai.azure.com/"]
    )
    
    azure_openai_deployment_name: str = Field(
        description="Nombre del deployment/modelo de Azure OpenAI configurado",
        examples=["gpt-4", "gpt-35-turbo"]
    )
    
    message: str = Field(
        description="Mensaje descriptivo sobre el estado de las credenciales",
        examples=["Credenciales cargadas exitosamente desde .env"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "azure_openai_endpoint": "https://mi-openai.openai.azure.com/",
                "azure_openai_deployment_name": "gpt-4",
                "message": "Credenciales cargadas exitosamente desde .env"
            }
        }


class EmailSendResponse(BaseModel):
    """
    Modelo de respuesta para el envío de emails.
    
    Indica el resultado del intento de envío de email y proporciona
    información adicional sobre el proceso.
    """
    
    success: bool = Field(
        description="Indica si el email fue enviado exitosamente",
        examples=[True, False]
    )
    
    message: str = Field(
        description="Mensaje descriptivo del resultado del envío",
        examples=[
            "Email enviado exitosamente",
            "Error: Dirección de email inválida",
            "Error: Servicio de email no disponible"
        ]
    )
    
    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Email enviado exitosamente"
            }
        }


class HealthCheckResponse(BaseModel):
    """
    Modelo de respuesta para el health check del sistema.
    
    Proporciona información detallada sobre el estado de la aplicación
    y sus componentes críticos.
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

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "Ezekl Budget API está funcionando correctamente",
                "version": "1.0.0"
            }
        }


class WebhookEventResponse(BaseModel):
    """
    Modelo de respuesta para el webhook de eventos de Azure Event Grid.
    
    Proporciona respuestas apropiadas según el tipo de evento procesado,
    incluyendo validación de suscripción y confirmación de procesamiento.
    """
    
    # Para validación de suscripción
    validationResponse: Optional[str] = Field(
        default=None,
        description="Código de validación requerido por Azure Event Grid para confirmar suscripción",
        examples=["ABCD1234-VALIDATION-CODE"]
    )
    
    # Para eventos normales
    ok: Optional[bool] = Field(
        default=None,
        description="Indica si el evento fue procesado exitosamente",
        examples=[True, False]
    )
    
    message: Optional[str] = Field(
        default=None,
        description="Mensaje descriptivo del resultado del procesamiento",
        examples=[
            "Evento procesado exitosamente",
            "Email entrante procesado",
            "Error interno procesando evento"
        ]
    )
    
    event_type: Optional[str] = Field(
        default=None,
        description="Tipo de evento procesado (para logging y debugging)",
        examples=[
            "SubscriptionValidation",
            "InboundEmailReceived",
            "EmailDeliveryReportReceived"
        ]
    )
    
    processed_at: Optional[str] = Field(
        default=None,
        description="Timestamp de cuándo fue procesado el evento (ISO 8601)",
        examples=["2024-10-04T10:30:00.123Z"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "examples": [
                {
                    "description": "Respuesta de validación de suscripción",
                    "value": {
                        "validationResponse": "ABCD1234-VALIDATION-CODE"
                    }
                },
                {
                    "description": "Respuesta de evento procesado exitosamente",
                    "value": {
                        "ok": True,
                        "message": "Evento procesado exitosamente",
                        "event_type": "InboundEmailReceived",
                        "processed_at": "2024-10-04T10:30:00.123Z"
                    }
                },
                {
                    "description": "Respuesta de error",
                    "value": {
                        "ok": False,
                        "message": "Error interno procesando evento",
                        "event_type": "InboundEmailReceived",
                        "processed_at": "2024-10-04T10:30:00.123Z"
                    }
                }
            ]
        }