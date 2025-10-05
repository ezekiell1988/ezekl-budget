"""
Modelos Pydantic para requests de la API.
Contiene todas las estructuras de datos para las peticiones entrantes.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class EmailSendRequest(BaseModel):
    """
    Modelo para request de envío de email mediante Azure Communication Services.
    
    Este modelo define la estructura de datos necesaria para enviar emails
    a través del endpoint /email/send.
    """
    
    to: List[EmailStr] = Field(
        description="Lista de direcciones de email de destinatarios principales",
        min_length=1,
        max_length=50,
        examples=[["usuario@ejemplo.com"], ["user1@test.com", "user2@test.com"]]
    )
    
    subject: str = Field(
        description="Asunto del email",
        min_length=1,
        max_length=255,
        examples=["Bienvenido a Ezekl Budget", "Notificación de presupuesto"]
    )
    
    html_content: Optional[str] = Field(
        default=None,
        description="Contenido del email en formato HTML. Al menos uno de html_content o text_content debe estar presente",
        max_length=100000,
        examples=["<h1>¡Hola!</h1><p>Gracias por registrarte en <strong>Ezekl Budget</strong>.</p>"]
    )
    
    text_content: Optional[str] = Field(
        default=None,
        description="Contenido del email en texto plano. Al menos uno de html_content o text_content debe estar presente",
        max_length=100000,
        examples=["¡Hola! Gracias por registrarte en Ezekl Budget."]
    )
    
    cc: Optional[List[EmailStr]] = Field(
        default=None,
        description="Lista de direcciones de email para copia (CC)",
        max_length=20,
        examples=[["supervisor@ejemplo.com"]]
    )
    
    bcc: Optional[List[EmailStr]] = Field(
        default=None,
        description="Lista de direcciones de email para copia oculta (BCC)",
        max_length=20,
        examples=[["admin@ezekl-budget.com"]]
    )
    
    reply_to: Optional[EmailStr] = Field(
        default=None,
        description="Dirección de email para respuestas. Si no se especifica, las respuestas van al remitente",
        examples=["support@ezekl-budget.com"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "to": ["usuario@ejemplo.com"],
                "subject": "Bienvenido a Ezekl Budget",
                "html_content": "<h1>¡Hola!</h1><p>Gracias por registrarte en <strong>Ezekl Budget</strong>.</p>",
                "text_content": "¡Hola! Gracias por registrarte en Ezekl Budget."
            }
        }


class WebhookEventRequest(BaseModel):
    """
    Modelo para eventos de webhook de Azure Event Grid.
    
    Este modelo maneja cualquier tipo de evento que llegue desde Azure Event Grid,
    incluyendo validación de suscripción, emails entrantes y reportes de entrega.
    """
    
    # Campos dinámicos - Azure Event Grid envía diferentes estructuras
    # dependiendo del tipo de evento
    
    class Config:
        """Configuración del modelo Pydantic."""
        # Permitir campos adicionales para flexibilidad con diferentes tipos de eventos
        extra = "allow"
        json_schema_extra = {
            "examples": [
                {
                    "description": "Validación de suscripción",
                    "value": [
                        {
                            "id": "12345678-abcd-1234-abcd-123456789012",
                            "eventType": "Microsoft.EventGrid.SubscriptionValidationEvent",
                            "subject": "",
                            "eventTime": "2024-10-04T10:00:00Z",
                            "data": {
                                "validationCode": "ABCD1234-VALIDATION-CODE",
                                "validationUrl": "https://..."
                            },
                            "dataVersion": "1.0",
                            "metadataVersion": "1"
                        }
                    ]
                },
                {
                    "description": "Email entrante",
                    "value": [
                        {
                            "id": "87654321-dcba-4321-dcba-987654321012",
                            "eventType": "Microsoft.Communication.InboundEmailReceived",
                            "subject": "/subscriptions/.../InboundEmailReceived",
                            "eventTime": "2024-10-04T10:30:00Z",
                            "data": {
                                "to": ["budget@ezekl.com"],
                                "from": "usuario@ejemplo.com",
                                "subject": "Consulta sobre presupuesto",
                                "emailContentUrl": "https://storage.azure.com/path/to/mime"
                            },
                            "dataVersion": "1.0",
                            "metadataVersion": "1"
                        }
                    ]
                }
            ]
        }
