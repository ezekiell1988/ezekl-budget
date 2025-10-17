"""
Modelos Pydantic para WhatsApp Business API.
Define las estructuras de datos para webhooks y mensajes de WhatsApp.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class WhatsAppProfile(BaseModel):
    """Perfil del contacto de WhatsApp."""
    name: str = Field(description="Nombre del contacto")


class WhatsAppContact(BaseModel):
    """Información del contacto que envía el mensaje."""
    profile: WhatsAppProfile
    wa_id: str = Field(description="ID de WhatsApp del contacto")


class WhatsAppTextMessage(BaseModel):
    """Contenido de un mensaje de texto."""
    body: str = Field(description="Contenido del mensaje de texto")


class WhatsAppMessage(BaseModel):
    """Mensaje individual de WhatsApp."""
    from_: str = Field(alias="from", description="Número de teléfono del remitente")
    id: str = Field(description="ID único del mensaje")
    timestamp: str = Field(description="Timestamp del mensaje")
    type: str = Field(description="Tipo de mensaje (text, image, video, etc.)")
    text: Optional[WhatsAppTextMessage] = Field(default=None, description="Contenido si es mensaje de texto")
    
    class Config:
        populate_by_name = True


class WhatsAppMetadata(BaseModel):
    """Metadata del número de teléfono de WhatsApp Business."""
    display_phone_number: str = Field(description="Número de teléfono mostrado")
    phone_number_id: str = Field(description="ID del número de teléfono")


class WhatsAppValue(BaseModel):
    """Valor del cambio en el webhook."""
    messaging_product: str = Field(description="Producto de mensajería (whatsapp)")
    metadata: WhatsAppMetadata
    contacts: Optional[List[WhatsAppContact]] = Field(default=None, description="Contactos involucrados")
    messages: Optional[List[WhatsAppMessage]] = Field(default=None, description="Mensajes recibidos")
    statuses: Optional[List[Dict[str, Any]]] = Field(default=None, description="Estados de mensajes enviados")


class WhatsAppChange(BaseModel):
    """Cambio notificado en el webhook."""
    value: WhatsAppValue
    field: str = Field(description="Campo que cambió (messages, message_status, etc.)")


class WhatsAppEntry(BaseModel):
    """Entrada individual en el webhook."""
    id: str = Field(description="ID de WhatsApp Business Account")
    changes: List[WhatsAppChange] = Field(description="Lista de cambios")


class WhatsAppWebhookPayload(BaseModel):
    """
    Payload completo del webhook de WhatsApp Business API.
    Estructura enviada por Meta cuando se recibe un mensaje o cambio de estado.
    """
    object: str = Field(description="Tipo de objeto (whatsapp_business_account)")
    entry: List[WhatsAppEntry] = Field(description="Lista de entradas con cambios")

    class Config:
        json_schema_extra = {
            "example": {
                "object": "whatsapp_business_account",
                "entry": [
                    {
                        "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                        "changes": [
                            {
                                "value": {
                                    "messaging_product": "whatsapp",
                                    "metadata": {
                                        "display_phone_number": "15551234567",
                                        "phone_number_id": "PHONE_NUMBER_ID"
                                    },
                                    "contacts": [
                                        {
                                            "profile": {
                                                "name": "Juan Pérez"
                                            },
                                            "wa_id": "5491112345678"
                                        }
                                    ],
                                    "messages": [
                                        {
                                            "from": "5491112345678",
                                            "id": "wamid.XXX==",
                                            "timestamp": "1234567890",
                                            "type": "text",
                                            "text": {
                                                "body": "Hola, quiero información"
                                            }
                                        }
                                    ]
                                },
                                "field": "messages"
                            }
                        ]
                    }
                ]
            }
        }


class WhatsAppWebhookVerification(BaseModel):
    """
    Modelo para verificación del webhook.
    Meta envía estos parámetros en GET para verificar el endpoint.
    """
    hub_mode: str = Field(alias="hub.mode", description="Modo del hub (subscribe)")
    hub_verify_token: str = Field(alias="hub.verify_token", description="Token de verificación")
    hub_challenge: str = Field(alias="hub.challenge", description="Challenge a retornar")
    
    class Config:
        populate_by_name = True
