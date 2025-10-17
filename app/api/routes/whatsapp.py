"""
Endpoints para integración con WhatsApp Business API.
Proporciona webhook para recibir mensajes y notificaciones de WhatsApp.
"""

from fastapi import APIRouter, HTTPException, Request, Query, Header, Depends
from fastapi.responses import PlainTextResponse
from typing import Optional, Dict
import logging
import json
from app.models.whatsapp import (
    WhatsAppWebhookPayload,
    WhatsAppMessageSendRequest,
    WhatsAppMessageSendResponse
)
from app.services.whatsapp_service import whatsapp_service
from app.core.config import settings
from app.api.routes.auth import get_current_user

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de WhatsApp
router = APIRouter()

# Token de verificación del webhook desde settings
WEBHOOK_VERIFY_TOKEN = settings.whatsapp_verify_token


@router.get(
    "/webhook",
    response_class=PlainTextResponse,
    summary="Verificación del webhook de WhatsApp",
    description="""Endpoint para verificación del webhook de WhatsApp Business API.
    
    Meta/Facebook envía una petición GET a este endpoint para verificar que el webhook
    está configurado correctamente. Debes configurar el mismo verify_token en la 
    consola de desarrolladores de Meta.
    
    **Parámetros de verificación:**
    - `hub.mode`: Debe ser "subscribe"
    - `hub.verify_token`: Debe coincidir con el token configurado
    - `hub.challenge`: Valor que debe retornarse para completar la verificación
    
    **Respuesta exitosa:**
    - Retorna el valor de hub.challenge como texto plano
    
    **Configuración en Meta:**
    1. Ve a la consola de desarrolladores de Meta
    2. Configura el webhook URL: https://tu-dominio.com/api/whatsapp/webhook
    3. Configura el verify token: mi_token_secreto_whatsapp_2024
    4. Suscríbete a los eventos: messages
    """
)
async def verify_webhook(
    request: Request,
    mode: str = Query(alias="hub.mode", description="Modo del hub"),
    token: str = Query(alias="hub.verify_token", description="Token de verificación"),
    challenge: str = Query(alias="hub.challenge", description="Challenge a retornar")
):
    """
    Verifica el webhook de WhatsApp.
    
    Args:
        mode: Modo del hub (debe ser "subscribe")
        token: Token de verificación (debe coincidir con WEBHOOK_VERIFY_TOKEN)
        challenge: Challenge enviado por Meta
        
    Returns:
        PlainTextResponse: El challenge si la verificación es exitosa
        
    Raises:
        HTTPException: Error 403 si la verificación falla
    """
    logger.info(f"📞 Verificación de webhook recibida")
    logger.debug(f"Mode: {mode}, Token recibido: {token[:10]}..., Challenge: {challenge[:20]}...")
    
    # Verificar que el modo sea "subscribe"
    if mode != "subscribe":
        logger.warning(f"❌ Modo inválido: {mode}")
        raise HTTPException(
            status_code=403,
            detail="Modo de verificación inválido"
        )
    
    # Verificar que el token coincida
    if token != WEBHOOK_VERIFY_TOKEN:
        logger.warning(f"❌ Token de verificación incorrecto")
        raise HTTPException(
            status_code=403,
            detail="Token de verificación inválido"
        )
    
    logger.info(f"✅ Webhook verificado exitosamente")
    
    # Retornar el challenge para completar la verificación
    return PlainTextResponse(content=challenge)


@router.post(
    "/webhook",
    summary="Recibir webhooks de WhatsApp",
    description="""Endpoint para recibir notificaciones de WhatsApp Business API.
    
    Este endpoint recibe notificaciones de Meta cuando:
    - Se recibe un nuevo mensaje
    - Cambia el estado de un mensaje enviado
    - Ocurren otros eventos configurados
    
    **Eventos soportados:**
    - `messages`: Mensajes entrantes de usuarios
    - `message_status`: Cambios de estado de mensajes enviados (enviado, entregado, leído)
    
    **Tipos de mensajes soportados:**
    - text: Mensajes de texto
    - image: Imágenes
    - video: Videos
    - document: Documentos
    - audio: Audios
    - location: Ubicaciones
    - contacts: Contactos
    
    **Seguridad:**
    - Meta firma las peticiones con x-hub-signature-256
    - Se debe validar la firma para producción (pendiente implementar)
    
    **Respuesta:**
    - Siempre retorna 200 OK para confirmar recepción
    - El procesamiento es asíncrono (actualmente solo logging)
    """,
    responses={
        200: {
            "description": "Webhook procesado exitosamente"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def receive_webhook(
    request: Request,
    payload: WhatsAppWebhookPayload,
    x_hub_signature_256: Optional[str] = Header(None, description="Firma de Meta para validación")
):
    """
    Recibe y procesa webhooks de WhatsApp.
    
    Args:
        request: Request de FastAPI
        payload: Payload del webhook validado con Pydantic
        x_hub_signature_256: Firma de seguridad de Meta
        
    Returns:
        dict: Confirmación de recepción
        
    Note:
        Por ahora solo imprime los datos recibidos.
        TODO: Implementar validación de firma x-hub-signature-256
        TODO: Implementar procesamiento de mensajes
        TODO: Implementar respuestas automáticas
    """
    try:
        logger.info("=" * 80)
        logger.info(f"📱 WEBHOOK DE WHATSAPP RECIBIDO")
        logger.info("=" * 80)
        
        # Log de la firma de seguridad
        if x_hub_signature_256:
            logger.info(f"🔐 Firma de seguridad: {x_hub_signature_256[:30]}...")
        else:
            logger.warning("⚠️ Sin firma de seguridad (x-hub-signature-256)")
        
        # Log del objeto principal
        logger.info(f"📦 Tipo de objeto: {payload.object}")
        
        # Procesar cada entrada
        for entry_idx, entry in enumerate(payload.entry, 1):
            logger.info(f"\n📋 ENTRADA #{entry_idx}")
            logger.info(f"  - WhatsApp Business Account ID: {entry.id}")
            
            # Procesar cada cambio
            for change_idx, change in enumerate(entry.changes, 1):
                logger.info(f"\n  🔄 CAMBIO #{change_idx}")
                logger.info(f"    - Campo: {change.field}")
                logger.info(f"    - Producto: {change.value.messaging_product}")
                
                # Metadata del número de teléfono
                metadata = change.value.metadata
                logger.info(f"    - Número de teléfono: {metadata.display_phone_number}")
                logger.info(f"    - Phone Number ID: {metadata.phone_number_id}")
                
                # Procesar mensajes entrantes
                if change.value.messages:
                    logger.info(f"\n    📨 MENSAJES ENTRANTES: {len(change.value.messages)}")
                    
                    for msg_idx, message in enumerate(change.value.messages, 1):
                        logger.info(f"\n      💬 MENSAJE #{msg_idx}")
                        logger.info(f"        - ID: {message.id}")
                        logger.info(f"        - De: {message.from_}")
                        logger.info(f"        - Timestamp: {message.timestamp}")
                        logger.info(f"        - Tipo: {message.type}")
                        
                        # Si es mensaje de texto, mostrar el contenido
                        if message.type == "text" and message.text:
                            logger.info(f"        - Contenido: '{message.text.body}'")
                        
                        # Log del contacto
                        contact_name = "Desconocido"
                        if change.value.contacts:
                            for contact in change.value.contacts:
                                if contact.wa_id == message.from_:
                                    contact_name = contact.profile.name
                                    logger.info(f"        - Nombre del contacto: {contact_name}")
                                    logger.info(f"        - WhatsApp ID: {contact.wa_id}")
                        
                        # 🤖 RESPUESTA AUTOMÁTICA: Enviar "Hola" cuando se recibe un mensaje
                        try:
                            logger.info(f"\n      🤖 Enviando respuesta automática a {message.from_}...")
                            response_msg = await whatsapp_service.send_text_message(
                                to=message.from_,
                                body=f"Hola {contact_name}! 👋 Gracias por tu mensaje. Este es un mensaje automático de prueba."
                            )
                            logger.info(f"      ✅ Respuesta enviada: {response_msg.messages[0]['id']}")
                        except Exception as reply_error:
                            logger.error(f"      ❌ Error enviando respuesta automática: {str(reply_error)}")
                
                # Procesar cambios de estado
                if change.value.statuses:
                    logger.info(f"\n    📊 ESTADOS DE MENSAJES: {len(change.value.statuses)}")
                    
                    for status_idx, status in enumerate(change.value.statuses, 1):
                        logger.info(f"\n      📍 ESTADO #{status_idx}")
                        logger.info(f"        - Estado: {json.dumps(status, indent=10)}")
        
        # Log del payload completo en formato JSON
        logger.info("\n" + "=" * 80)
        logger.info("📄 PAYLOAD COMPLETO (JSON):")
        logger.info("=" * 80)
        logger.info(json.dumps(payload.model_dump(by_alias=True), indent=2, ensure_ascii=False))
        logger.info("=" * 80)
        
        # Retornar confirmación de recepción
        return {
            "status": "received",
            "message": "Webhook procesado exitosamente"
        }
        
    except Exception as e:
        logger.error(f"❌ Error procesando webhook de WhatsApp: {str(e)}", exc_info=True)
        
        # Meta requiere que siempre retornemos 200 para evitar reintentos
        # Por eso capturamos el error pero retornamos éxito
        return {
            "status": "error",
            "message": f"Error procesando webhook: {str(e)}"
        }


@router.get(
    "/status",
    summary="Estado del servicio de WhatsApp",
    description="Verifica que el servicio de WhatsApp está activo y configurado correctamente"
)
async def whatsapp_status():
    """
    Verifica el estado del servicio de WhatsApp.
    
    Returns:
        dict: Estado del servicio
    """
    service_status = await whatsapp_service.get_service_status()
    
    return {
        **service_status,
        "webhook_configured": True,
        "verify_token_set": bool(WEBHOOK_VERIFY_TOKEN),
        "features": {
            "receive_messages": True,
            "send_messages": service_status["configured"],
            "validate_signature": False  # Pendiente implementar
        }
    }


# ============== ENDPOINTS PARA ENVÍO DE MENSAJES ==============

@router.post(
    "/send",
    response_model=WhatsAppMessageSendResponse,
    summary="Enviar mensaje de WhatsApp",
    description="""Envía un mensaje de WhatsApp de cualquier tipo.
    
    🔒 **Requiere autenticación.**
    
    **Tipos de mensajes soportados:**
    - `text`: Mensajes de texto simple
    - `image`: Imágenes (con caption opcional)
    - `video`: Videos (con caption opcional)
    - `document`: Documentos PDF, Word, Excel, etc.
    - `audio`: Archivos de audio
    - `location`: Ubicaciones con coordenadas
    - `contacts`: Compartir contactos
    - `template`: Plantillas aprobadas
    - `interactive`: Mensajes con botones (máximo 3)
    
    **Formato del número de teléfono:**
    - Debe incluir código de país sin '+'
    - Ejemplo: "5491112345678" para Argentina
    - Ejemplo: "521234567890" para México
    
    **Notas importantes:**
    - Para imágenes/videos/documentos puedes usar URL pública o ID de media previamente subido
    - Las plantillas deben estar aprobadas previamente en Meta Business
    - Los mensajes interactivos permiten máximo 3 botones
    """,
    responses={
        200: {
            "description": "Mensaje enviado exitosamente",
            "model": WhatsAppMessageSendResponse
        },
        401: {
            "description": "No autorizado - Token inválido o ausente"
        },
        400: {
            "description": "Request inválido - Parámetros incorrectos"
        },
        500: {
            "description": "Error del servidor o de WhatsApp API"
        }
    }
)
async def send_whatsapp_message(
    message_request: WhatsAppMessageSendRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Envía un mensaje de WhatsApp.
    
    Args:
        message_request: Datos del mensaje a enviar
        current_user: Usuario autenticado (dependency)
        
    Returns:
        WhatsAppMessageSendResponse: Información del mensaje enviado
        
    Raises:
        HTTPException: Si hay error al enviar el mensaje
    """
    logger.info(f"👤 Usuario {current_user['user'].get('codeLogin', 'unknown')} enviando mensaje WhatsApp")
    
    try:
        response = await whatsapp_service.send_message(message_request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado enviando mensaje: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al enviar mensaje: {str(e)}"
        )


@router.post(
    "/send/text",
    response_model=WhatsAppMessageSendResponse,
    summary="Enviar mensaje de texto simple",
    description="""Envía un mensaje de texto simple a un número de WhatsApp.
    
    🔒 **Requiere autenticación.**
    
    Este es un endpoint simplificado para enviar mensajes de texto.
    Para otros tipos de mensajes usa el endpoint `/send`.
    
    **Parámetros:**
    - `to`: Número de teléfono con código de país (ej: "5491112345678")
    - `message`: Contenido del mensaje (máximo 4096 caracteres)
    - `preview_url`: Si es true, muestra preview de URLs (default: false)
    """,
    responses={
        200: {
            "description": "Mensaje enviado exitosamente"
        },
        401: {
            "description": "No autorizado"
        },
        500: {
            "description": "Error al enviar mensaje"
        }
    }
)
async def send_text_message(
    to: str = Query(description="Número de teléfono del destinatario", example="5491112345678"),
    message: str = Query(description="Contenido del mensaje", example="Hola, ¿cómo estás?"),
    preview_url: bool = Query(default=False, description="Mostrar preview de URLs"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Envía un mensaje de texto simple.
    
    Args:
        to: Número de teléfono del destinatario
        message: Contenido del mensaje
        preview_url: Si es True, muestra preview de URLs
        current_user: Usuario autenticado
        
    Returns:
        WhatsAppMessageSendResponse
    """
    logger.info(f"👤 Usuario {current_user['user'].get('codeLogin', 'unknown')} enviando texto a {to}")
    
    try:
        response = await whatsapp_service.send_text_message(to, message, preview_url)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando texto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar mensaje de texto: {str(e)}"
        )


@router.post(
    "/send/image",
    response_model=WhatsAppMessageSendResponse,
    summary="Enviar imagen",
    description="""Envía una imagen a un número de WhatsApp.
    
    🔒 **Requiere autenticación.**
    
    Puedes enviar la imagen de dos formas:
    1. URL pública (la imagen debe ser accesible por WhatsApp)
    2. ID de media previamente subido a WhatsApp
    
    **Formatos soportados:** JPG, PNG
    **Tamaño máximo:** 5MB
    """,
    responses={
        200: {"description": "Imagen enviada exitosamente"},
        401: {"description": "No autorizado"},
        400: {"description": "Parámetros inválidos"},
        500: {"description": "Error al enviar imagen"}
    }
)
async def send_image_message(
    to: str = Query(description="Número de teléfono del destinatario"),
    image_url: Optional[str] = Query(default=None, description="URL pública de la imagen"),
    image_id: Optional[str] = Query(default=None, description="ID de imagen subida"),
    caption: Optional[str] = Query(default=None, description="Caption de la imagen"),
    current_user: Dict = Depends(get_current_user)
):
    """Envía una imagen."""
    logger.info(f"👤 Usuario {current_user['user'].get('codeLogin', 'unknown')} enviando imagen a {to}")
    
    try:
        response = await whatsapp_service.send_image(to, image_url, image_id, caption)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando imagen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar imagen: {str(e)}"
        )


@router.post(
    "/send/document",
    response_model=WhatsAppMessageSendResponse,
    summary="Enviar documento",
    description="""Envía un documento (PDF, Word, Excel, etc.) a un número de WhatsApp.
    
    🔒 **Requiere autenticación.**
    
    **Formatos soportados:** PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, etc.
    **Tamaño máximo:** 100MB
    """,
    responses={
        200: {"description": "Documento enviado exitosamente"},
        401: {"description": "No autorizado"},
        500: {"description": "Error al enviar documento"}
    }
)
async def send_document_message(
    to: str = Query(description="Número de teléfono del destinatario"),
    document_url: Optional[str] = Query(default=None, description="URL pública del documento"),
    document_id: Optional[str] = Query(default=None, description="ID de documento subido"),
    filename: Optional[str] = Query(default=None, description="Nombre del archivo"),
    caption: Optional[str] = Query(default=None, description="Caption del documento"),
    current_user: Dict = Depends(get_current_user)
):
    """Envía un documento."""
    logger.info(f"👤 Usuario {current_user['user'].get('codeLogin', 'unknown')} enviando documento a {to}")
    
    try:
        response = await whatsapp_service.send_document(to, document_url, document_id, filename, caption)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando documento: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar documento: {str(e)}"
        )


@router.post(
    "/send/location",
    response_model=WhatsAppMessageSendResponse,
    summary="Enviar ubicación",
    description="""Envía una ubicación geográfica a un número de WhatsApp.
    
    🔒 **Requiere autenticación.**
    
    Envía coordenadas de latitud y longitud, opcionalmente con nombre y dirección.
    """,
    responses={
        200: {"description": "Ubicación enviada exitosamente"},
        401: {"description": "No autorizado"},
        500: {"description": "Error al enviar ubicación"}
    }
)
async def send_location_message(
    to: str = Query(description="Número de teléfono del destinatario"),
    latitude: float = Query(description="Latitud"),
    longitude: float = Query(description="Longitud"),
    name: Optional[str] = Query(default=None, description="Nombre del lugar"),
    address: Optional[str] = Query(default=None, description="Dirección"),
    current_user: Dict = Depends(get_current_user)
):
    """Envía una ubicación."""
    logger.info(f"👤 Usuario {current_user['user'].get('codeLogin', 'unknown')} enviando ubicación a {to}")
    
    try:
        response = await whatsapp_service.send_location(to, latitude, longitude, name, address)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando ubicación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar ubicación: {str(e)}"
        )


@router.post(
    "/send/template",
    response_model=WhatsAppMessageSendResponse,
    summary="Enviar plantilla aprobada",
    description="""Envía un mensaje usando una plantilla previamente aprobada en Meta Business.
    
    🔒 **Requiere autenticación.**
    
    Las plantillas deben ser aprobadas por Meta antes de poder usarse.
    Este es el único tipo de mensaje que puedes enviar a usuarios que no han
    iniciado la conversación contigo en las últimas 24 horas.
    """,
    responses={
        200: {"description": "Plantilla enviada exitosamente"},
        401: {"description": "No autorizado"},
        400: {"description": "Plantilla no encontrada o no aprobada"},
        500: {"description": "Error al enviar plantilla"}
    }
)
async def send_template_message(
    to: str = Query(description="Número de teléfono del destinatario"),
    template_name: str = Query(description="Nombre de la plantilla aprobada"),
    language_code: str = Query(default="es", description="Código de idioma"),
    current_user: Dict = Depends(get_current_user)
):
    """Envía una plantilla aprobada."""
    logger.info(f"👤 Usuario {current_user['user'].get('codeLogin', 'unknown')} enviando plantilla '{template_name}' a {to}")
    
    try:
        response = await whatsapp_service.send_template(to, template_name, language_code)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando plantilla: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar plantilla: {str(e)}"
        )
