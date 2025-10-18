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


class WhatsAppImageMessage(BaseModel):
    """Contenido de un mensaje de imagen."""
    id: str = Field(description="ID del media en WhatsApp")
    mime_type: str = Field(description="Tipo MIME de la imagen")
    sha256: str = Field(description="Hash SHA256 del archivo")
    caption: Optional[str] = Field(default=None, description="Caption de la imagen")


class WhatsAppAudioMessage(BaseModel):
    """Contenido de un mensaje de audio."""
    id: str = Field(description="ID del media en WhatsApp")
    mime_type: str = Field(description="Tipo MIME del audio")
    sha256: str = Field(description="Hash SHA256 del archivo")
    voice: Optional[bool] = Field(default=None, description="Si es mensaje de voz")


class WhatsAppVideoMessage(BaseModel):
    """Contenido de un mensaje de video."""
    id: str = Field(description="ID del media en WhatsApp")
    mime_type: str = Field(description="Tipo MIME del video")
    sha256: str = Field(description="Hash SHA256 del archivo")
    caption: Optional[str] = Field(default=None, description="Caption del video")


class WhatsAppDocumentMessage(BaseModel):
    """Contenido de un mensaje de documento."""
    id: str = Field(description="ID del media en WhatsApp")
    mime_type: str = Field(description="Tipo MIME del documento")
    sha256: str = Field(description="Hash SHA256 del archivo")
    filename: Optional[str] = Field(default=None, description="Nombre del archivo")
    caption: Optional[str] = Field(default=None, description="Caption del documento")


class WhatsAppMessage(BaseModel):
    """Mensaje individual de WhatsApp."""
    from_: str = Field(alias="from", description="Número de teléfono del remitente")
    id: str = Field(description="ID único del mensaje")
    timestamp: str = Field(description="Timestamp del mensaje")
    type: str = Field(description="Tipo de mensaje (text, image, video, audio, document, etc.)")
    
    # Diferentes tipos de contenido según el tipo de mensaje
    text: Optional[WhatsAppTextMessage] = Field(default=None, description="Contenido si es mensaje de texto")
    image: Optional[WhatsAppImageMessage] = Field(default=None, description="Contenido si es imagen")
    audio: Optional[WhatsAppAudioMessage] = Field(default=None, description="Contenido si es audio")
    video: Optional[WhatsAppVideoMessage] = Field(default=None, description="Contenido si es video")
    document: Optional[WhatsAppDocumentMessage] = Field(default=None, description="Contenido si es documento")
    
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


# ============== MODELOS PARA ENVÍO DE MENSAJES ==============

class WhatsAppTextMessageSend(BaseModel):
    """Contenido de mensaje de texto a enviar."""
    body: str = Field(description="Contenido del mensaje", max_length=4096)
    preview_url: Optional[bool] = Field(default=False, description="Mostrar preview de URLs")


class WhatsAppMediaObject(BaseModel):
    """Objeto de media (imagen, video, documento, audio)."""
    id: Optional[str] = Field(default=None, description="ID del media subido previamente")
    link: Optional[str] = Field(default=None, description="URL pública del media")
    caption: Optional[str] = Field(default=None, description="Caption del media", max_length=1024)
    filename: Optional[str] = Field(default=None, description="Nombre del archivo (solo documentos)")


class WhatsAppLocationMessage(BaseModel):
    """Mensaje de ubicación."""
    longitude: float = Field(description="Longitud")
    latitude: float = Field(description="Latitud")
    name: Optional[str] = Field(default=None, description="Nombre del lugar", max_length=1000)
    address: Optional[str] = Field(default=None, description="Dirección", max_length=1000)


class WhatsAppContactName(BaseModel):
    """Nombre de un contacto."""
    formatted_name: str = Field(description="Nombre formateado completo")
    first_name: Optional[str] = Field(default=None, description="Nombre")
    last_name: Optional[str] = Field(default=None, description="Apellido")
    middle_name: Optional[str] = Field(default=None, description="Segundo nombre")
    suffix: Optional[str] = Field(default=None, description="Sufijo")
    prefix: Optional[str] = Field(default=None, description="Prefijo")


class WhatsAppContactPhone(BaseModel):
    """Teléfono de un contacto."""
    phone: str = Field(description="Número de teléfono")
    type: Optional[str] = Field(default="CELL", description="Tipo de teléfono")
    wa_id: Optional[str] = Field(default=None, description="WhatsApp ID")


class WhatsAppContactEmail(BaseModel):
    """Email de un contacto."""
    email: str = Field(description="Dirección de email")
    type: Optional[str] = Field(default="WORK", description="Tipo de email")


class WhatsAppContactUrl(BaseModel):
    """URL de un contacto."""
    url: str = Field(description="URL")
    type: Optional[str] = Field(default="WORK", description="Tipo de URL")


class WhatsAppContactAddress(BaseModel):
    """Dirección de un contacto."""
    street: Optional[str] = Field(default=None, description="Calle")
    city: Optional[str] = Field(default=None, description="Ciudad")
    state: Optional[str] = Field(default=None, description="Estado/Provincia")
    zip: Optional[str] = Field(default=None, description="Código postal")
    country: Optional[str] = Field(default=None, description="País")
    country_code: Optional[str] = Field(default=None, description="Código de país")
    type: Optional[str] = Field(default="WORK", description="Tipo de dirección")


class WhatsAppContactOrg(BaseModel):
    """Organización de un contacto."""
    company: Optional[str] = Field(default=None, description="Nombre de la empresa")
    department: Optional[str] = Field(default=None, description="Departamento")
    title: Optional[str] = Field(default=None, description="Título/Cargo")


class WhatsAppContact(BaseModel):
    """Contacto a compartir."""
    name: WhatsAppContactName = Field(description="Nombre del contacto")
    phones: Optional[List[WhatsAppContactPhone]] = Field(default=None, description="Teléfonos")
    emails: Optional[List[WhatsAppContactEmail]] = Field(default=None, description="Emails")
    urls: Optional[List[WhatsAppContactUrl]] = Field(default=None, description="URLs")
    addresses: Optional[List[WhatsAppContactAddress]] = Field(default=None, description="Direcciones")
    org: Optional[WhatsAppContactOrg] = Field(default=None, description="Organización")
    birthday: Optional[str] = Field(default=None, description="Cumpleaños (YYYY-MM-DD)")


class WhatsAppContactsMessage(BaseModel):
    """Mensaje con contactos."""
    contacts: List[WhatsAppContact] = Field(description="Lista de contactos")


class WhatsAppTemplateComponent(BaseModel):
    """Componente de plantilla."""
    type: str = Field(description="Tipo de componente (body, header, button)")
    parameters: List[Dict[str, Any]] = Field(description="Parámetros del componente")


class WhatsAppTemplateMessage(BaseModel):
    """Mensaje usando plantilla aprobada."""
    name: str = Field(description="Nombre de la plantilla")
    language: Dict[str, str] = Field(description="Idioma de la plantilla", example={"code": "es"})
    components: Optional[List[WhatsAppTemplateComponent]] = Field(default=None, description="Componentes")


class WhatsAppInteractiveButton(BaseModel):
    """Botón interactivo."""
    type: str = Field(description="Tipo de botón (reply)")
    reply: Dict[str, str] = Field(description="Datos del botón", example={"id": "btn1", "title": "Sí"})


class WhatsAppInteractiveAction(BaseModel):
    """Acción interactiva."""
    buttons: List[WhatsAppInteractiveButton] = Field(description="Lista de botones", max_items=3)


class WhatsAppInteractiveHeader(BaseModel):
    """Header de mensaje interactivo."""
    type: str = Field(description="Tipo de header (text, image, video, document)")
    text: Optional[str] = Field(default=None, description="Texto del header")
    image: Optional[WhatsAppMediaObject] = Field(default=None, description="Imagen del header")
    video: Optional[WhatsAppMediaObject] = Field(default=None, description="Video del header")
    document: Optional[WhatsAppMediaObject] = Field(default=None, description="Documento del header")


class WhatsAppInteractiveBody(BaseModel):
    """Body de mensaje interactivo."""
    text: str = Field(description="Texto del body", max_length=1024)


class WhatsAppInteractiveFooter(BaseModel):
    """Footer de mensaje interactivo."""
    text: str = Field(description="Texto del footer", max_length=60)


class WhatsAppInteractiveMessage(BaseModel):
    """Mensaje interactivo con botones."""
    type: str = Field(description="Tipo de interactivo (button, list)")
    header: Optional[WhatsAppInteractiveHeader] = Field(default=None, description="Header opcional")
    body: WhatsAppInteractiveBody = Field(description="Cuerpo del mensaje")
    footer: Optional[WhatsAppInteractiveFooter] = Field(default=None, description="Footer opcional")
    action: WhatsAppInteractiveAction = Field(description="Acción con botones")


class WhatsAppMessageSendRequest(BaseModel):
    """Request para enviar un mensaje de WhatsApp."""
    messaging_product: str = Field(default="whatsapp", description="Producto de mensajería")
    recipient_type: str = Field(default="individual", description="Tipo de destinatario")
    to: str = Field(description="Número de teléfono del destinatario (formato internacional)")
    type: str = Field(description="Tipo de mensaje (text, image, video, document, audio, location, contacts, template, interactive)")
    
    # Tipos de mensaje (solo uno debe estar presente según el tipo)
    text: Optional[WhatsAppTextMessageSend] = Field(default=None, description="Mensaje de texto")
    image: Optional[WhatsAppMediaObject] = Field(default=None, description="Imagen")
    video: Optional[WhatsAppMediaObject] = Field(default=None, description="Video")
    document: Optional[WhatsAppMediaObject] = Field(default=None, description="Documento")
    audio: Optional[WhatsAppMediaObject] = Field(default=None, description="Audio")
    location: Optional[WhatsAppLocationMessage] = Field(default=None, description="Ubicación")
    contacts: Optional[WhatsAppContactsMessage] = Field(default=None, description="Contactos")
    template: Optional[WhatsAppTemplateMessage] = Field(default=None, description="Plantilla")
    interactive: Optional[WhatsAppInteractiveMessage] = Field(default=None, description="Mensaje interactivo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": "5491112345678",
                "type": "text",
                "text": {
                    "body": "Hola, este es un mensaje de prueba desde la API"
                }
            }
        }


class WhatsAppMessageSendResponse(BaseModel):
    """Respuesta al enviar un mensaje."""
    messaging_product: str = Field(description="Producto de mensajería")
    contacts: List[Dict[str, str]] = Field(description="Información del contacto")
    messages: List[Dict[str, str]] = Field(description="Información del mensaje enviado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "messaging_product": "whatsapp",
                "contacts": [{"input": "5491112345678", "wa_id": "5491112345678"}],
                "messages": [{"id": "wamid.HBgLNTU1NTU1NTU1NTUVAgARGBI5QTBDQTA1RjZGMEREMkU4RjYA"}]
            }
        }


class WhatsAppErrorResponse(BaseModel):
    """Respuesta de error de la API de WhatsApp."""
    error: Dict[str, Any] = Field(description="Información del error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "message": "Invalid parameter",
                    "type": "OAuthException",
                    "code": 100,
                    "error_subcode": 2388001,
                    "fbtrace_id": "ABC123"
                }
            }
        }
