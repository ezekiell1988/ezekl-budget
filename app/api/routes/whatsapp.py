"""
Endpoints para integración con WhatsApp Business API.
Proporciona webhook para recibir mensajes y notificaciones de WhatsApp.
"""

from fastapi import APIRouter, HTTPException, Request, Query, Header, Depends
from fastapi.responses import PlainTextResponse
from typing import Optional, Dict
import logging
from app.models.whatsapp import (
    WhatsAppWebhookPayload,
    WhatsAppMessageSendRequest,
    WhatsAppMessageSendResponse,
)
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_service
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
    """,
)
async def verify_webhook(
    request: Request,
    mode: str = Query(alias="hub.mode", description="Modo del hub"),
    token: str = Query(alias="hub.verify_token", description="Token de verificación"),
    challenge: str = Query(alias="hub.challenge", description="Challenge a retornar"),
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

    # Verificar que el modo sea "subscribe"
    if mode != "subscribe":
        logger.warning(f"❌ Modo inválido: {mode}")
        raise HTTPException(status_code=403, detail="Modo de verificación inválido")

    # Verificar que el token coincida
    if token != WEBHOOK_VERIFY_TOKEN:
        logger.warning(f"❌ Token de verificación incorrecto")
        raise HTTPException(status_code=403, detail="Token de verificación inválido")

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
        200: {"description": "Webhook procesado exitosamente"},
        500: {"description": "Error interno del servidor"},
    },
)
async def receive_webhook(
    request: Request,
    payload: WhatsAppWebhookPayload,
    x_hub_signature_256: Optional[str] = Header(
        None, description="Firma de Meta para validación"
    ),
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
        pass  # Logger eliminado

        # Log de la firma de seguridad
        if x_hub_signature_256:
            pass  # Logger eliminado
        else:
            logger.warning("⚠️ Sin firma de seguridad (x-hub-signature-256)")

        # Log del objeto principal

        # Procesar cada entrada
        for entry_idx, entry in enumerate(payload.entry, 1):
            pass  # Logger eliminado

            # Procesar cada cambio
            for change_idx, change in enumerate(entry.changes, 1):

                # Metadata del número de teléfono
                metadata = change.value.metadata

                # Procesar mensajes entrantes
                if change.value.messages:
                    pass  # Logger eliminado

                    for msg_idx, message in enumerate(change.value.messages, 1):
                        pass  # Logger eliminado

                        # Si es mensaje de texto, mostrar el contenido
                        if message.type == "text" and message.text:
                            pass  # Logger eliminado

                        # Si es imagen, mostrar detalles
                        if message.type == "image" and message.image:
                            pass  # Logger eliminado
                            if message.image.caption:
                                pass  # Logger eliminado

                        # Si es audio, mostrar detalles
                        if message.type == "audio" and message.audio:
                            pass  # Logger eliminado
                            if message.audio.voice:
                                pass  # Logger eliminado

                        # Si es video, mostrar detalles
                        if message.type == "video" and message.video:
                            pass  # Logger eliminado
                            if message.video.caption:
                                pass  # Logger eliminado

                        # Log del contacto
                        contact_name = "Desconocido"
                        if change.value.contacts:
                            for contact in change.value.contacts:
                                if contact.wa_id == message.from_:
                                    contact_name = contact.profile.name

                        # 🤖 RESPUESTA AUTOMÁTICA CON IA MULTIMODAL
                        # Soporta: texto, imágenes y audios
                        if message.type in ["text", "image", "audio"]:
                            try:
                                # ✅ Marcar mensaje como leído (doble check azul)
                                await whatsapp_service.mark_message_as_read(message.id)

                                # Extraer texto (puede ser mensaje directo o caption)
                                user_text = None
                                image_data = None
                                audio_data = None
                                media_type = None

                                if message.type == "text" and message.text:
                                    user_text = message.text.body

                                elif message.type == "image" and message.image:
                                    # Descargar la imagen
                                    image_data = (
                                        await whatsapp_service.get_media_content(
                                            message.image.id
                                        )
                                    )
                                    user_text = (
                                        message.image.caption
                                        or "¿Qué ves en esta imagen?"
                                    )
                                    media_type = message.image.mime_type

                                elif message.type == "audio" and message.audio:
                                    # Descargar el audio
                                    audio_data = (
                                        await whatsapp_service.get_media_content(
                                            message.audio.id
                                        )
                                    )
                                    # Para audios, dejar user_text vacío - la transcripción lo reemplazará
                                    user_text = None
                                    media_type = message.audio.mime_type

                                # Generar y enviar respuesta usando IA
                                ai_result = await ai_service.process_and_reply(
                                    user_message=user_text,
                                    phone_number=message.from_,
                                    contact_name=contact_name,
                                    image_data=image_data,
                                    audio_data=audio_data,
                                    media_type=media_type
                                )

                                if ai_result["success"]:
                                    pass  # Logger eliminado
                                    if ai_result.get("processed_media"):
                                        media_info = ai_result["processed_media"]
                                        if media_info.get("has_image"):
                                            pass  # Logger eliminado
                                        if media_info.get("has_audio"):
                                            pass  # Logger eliminado
                                else:
                                    logger.error(
                                        f"      ❌ Error procesando con IA: {ai_result.get('error')}"
                                    )

                            except Exception as reply_error:
                                logger.error(
                                    f"      ❌ Error en respuesta automática con IA: {str(reply_error)}",
                                    exc_info=True,
                                )

                # Procesar cambios de estado
                if change.value.statuses:
                    pass  # Logger eliminado

                    for status_idx, status in enumerate(change.value.statuses, 1):
                        pass  # Logger eliminado

        # Log del payload completo en formato JSON

        # Retornar confirmación de recepción
        return {"status": "received", "message": "Webhook procesado exitosamente"}

    except Exception as e:
        logger.error(
            f"❌ Error procesando webhook de WhatsApp: {str(e)}", exc_info=True
        )

        # Meta requiere que siempre retornemos 200 para evitar reintentos
        # Por eso capturamos el error pero retornamos éxito
        return {"status": "error", "message": f"Error procesando webhook: {str(e)}"}


@router.get(
    "/status",
    summary="Estado del servicio de WhatsApp",
    description="Verifica que el servicio de WhatsApp está activo y configurado correctamente",
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
            "validate_signature": False,  # Pendiente implementar
        },
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
            "model": WhatsAppMessageSendResponse,
        },
        401: {"description": "No autorizado - Token inválido o ausente"},
        400: {"description": "Request inválido - Parámetros incorrectos"},
        500: {"description": "Error del servidor o de WhatsApp API"},
    },
)
async def send_whatsapp_message(
    message_request: WhatsAppMessageSendRequest,
    current_user: Dict = Depends(get_current_user),
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

    try:
        response = await whatsapp_service.send_message(message_request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado enviando mensaje: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error inesperado al enviar mensaje: {str(e)}"
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
        200: {"description": "Mensaje enviado exitosamente"},
        401: {"description": "No autorizado"},
        500: {"description": "Error al enviar mensaje"},
    },
)
async def send_text_message(
    to: str = Query(
        description="Número de teléfono del destinatario", example="5491112345678"
    ),
    message: str = Query(
        description="Contenido del mensaje", example="Hola, ¿cómo estás?"
    ),
    preview_url: bool = Query(default=False, description="Mostrar preview de URLs"),
    current_user: Dict = Depends(get_current_user),
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

    try:
        response = await whatsapp_service.send_text_message(to, message, preview_url)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando texto: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error al enviar mensaje de texto: {str(e)}"
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
        500: {"description": "Error al enviar imagen"},
    },
)
async def send_image_message(
    to: str = Query(description="Número de teléfono del destinatario"),
    image_url: Optional[str] = Query(
        default=None, description="URL pública de la imagen"
    ),
    image_id: Optional[str] = Query(default=None, description="ID de imagen subida"),
    caption: Optional[str] = Query(default=None, description="Caption de la imagen"),
    current_user: Dict = Depends(get_current_user),
):
    """Envía una imagen."""

    try:
        response = await whatsapp_service.send_image(to, image_url, image_id, caption)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando imagen: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al enviar imagen: {str(e)}")


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
        500: {"description": "Error al enviar documento"},
    },
)
async def send_document(
    to: str = Query(
        ..., description="Número de teléfono con código de país (ej: 5491112345678)"
    ),
    link: str = Query(..., description="URL del documento"),
    caption: Optional[str] = Query(None, description="Texto descriptivo opcional"),
    filename: Optional[str] = Query(None, description="Nombre del archivo"),
    current_user: dict = Depends(get_current_user),
):
    """Envía un documento a un número de WhatsApp."""
    try:
        result = await whatsapp_service.send_document(
            to=to, link=link, caption=caption, filename=filename
        )
        return result
    except Exception as e:
        logger.error(f"Error enviando documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== ENDPOINTS DE IA PARA WHATSAPP ==============


@router.post(
    "/ai/chat",
    summary="Chat con IA (sin enviar por WhatsApp)",
    description="""Genera una respuesta de IA sin enviarla por WhatsApp.
    
    🔒 **Requiere autenticación.**
    
    Soporta procesamiento multimodal:
    - Texto simple
    - Imagen (via media_id de WhatsApp)
    - Audio (via media_id de WhatsApp)
    - Combinaciones de texto + imagen o texto + audio
    
    Útil para:
    - Probar respuestas de IA antes de enviarlas
    - Integrar la IA en otros flujos
    - Depuración y testing
    """,
    responses={
        200: {
            "description": "Respuesta generada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "response": "¡Hola! 👋 Soy el asistente de Ezekl Budget...",
                        "phone_number": "5491112345678",
                        "contact_name": "Juan Pérez",
                        "processed_media": {"has_image": False, "has_audio": False},
                    }
                }
            },
        },
        401: {"description": "No autorizado"},
        500: {"description": "Error generando respuesta"},
    },
)
async def ai_chat(
    message: str = Query(..., description="Mensaje del usuario (texto o caption)"),
    phone_number: str = Query(
        ..., description="Número de teléfono (para contexto/historial)"
    ),
    contact_name: Optional[str] = Query(None, description="Nombre del contacto"),
    image_id: Optional[str] = Query(
        None, description="ID de imagen de WhatsApp para procesar"
    ),
    audio_id: Optional[str] = Query(
        None, description="ID de audio de WhatsApp para procesar"
    ),
    current_user: dict = Depends(get_current_user),
):
    """Genera una respuesta de IA sin enviarla por WhatsApp. Soporta multimedia."""
    try:
        image_data = None
        audio_data = None
        media_type = None

        # Descargar imagen si se proporcionó ID
        if image_id:
            image_data = await whatsapp_service.get_media_content(image_id)
            media_type = "image/jpeg"  # WhatsApp generalmente usa JPEG

        # Descargar audio si se proporcionó ID
        if audio_id:
            audio_data = await whatsapp_service.get_media_content(audio_id)
            media_type = "audio/ogg"  # WhatsApp voice messages son OGG

        response = await ai_service.generate_response(
            user_message=message,
            phone_number=phone_number,
            contact_name=contact_name,
            image_data=image_data,
            audio_data=audio_data,
            media_type=media_type,
        )

        return {
            "response": response,
            "phone_number": phone_number,
            "contact_name": contact_name,
            "processed_media": {
                "has_image": bool(image_data),
                "has_audio": bool(audio_data),
            },
        }
    except Exception as e:
        logger.error(f"Error generando respuesta de IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/ai/reply",
    summary="Enviar respuesta de IA por WhatsApp",
    description="""Genera una respuesta de IA y la envía automáticamente por WhatsApp.
    
    🔒 **Requiere autenticación.**
    
    Soporta procesamiento multimodal:
    - Texto simple
    - Imagen (via media_id de WhatsApp)
    - Audio (via media_id de WhatsApp)
    - Combinaciones de texto + imagen o texto + audio
    
    Este endpoint:
    1. Genera una respuesta usando IA basada en el mensaje del usuario
    2. Procesa imágenes o audios si se proporcionan
    3. Envía la respuesta automáticamente por WhatsApp
    4. Mantiene el historial de conversación
    """,
    responses={
        200: {"description": "Respuesta generada y enviada exitosamente"},
        401: {"description": "No autorizado"},
        500: {"description": "Error procesando mensaje"},
    },
)
async def ai_reply(
    message: str = Query(..., description="Mensaje del usuario (texto o caption)"),
    phone_number: str = Query(..., description="Número de teléfono destino"),
    contact_name: Optional[str] = Query(None, description="Nombre del contacto"),
    image_id: Optional[str] = Query(
        None, description="ID de imagen de WhatsApp para procesar"
    ),
    audio_id: Optional[str] = Query(
        None, description="ID de audio de WhatsApp para procesar"
    ),
    current_user: dict = Depends(get_current_user),
):
    """Genera y envía una respuesta de IA por WhatsApp. Soporta multimedia."""
    try:
        image_data = None
        audio_data = None
        media_type = None

        # Descargar imagen si se proporcionó ID
        if image_id:
            image_data = await whatsapp_service.get_media_content(image_id)
            media_type = "image/jpeg"

        # Descargar audio si se proporcionó ID
        if audio_id:
            audio_data = await whatsapp_service.get_media_content(audio_id)
            media_type = "audio/ogg"

        result = await ai_service.process_and_reply(
            user_message=message,
            phone_number=phone_number,
            contact_name=contact_name,
            image_data=image_data,
            audio_data=audio_data,
            media_type=media_type,
        )

        return result
    except Exception as e:
        logger.error(f"Error en respuesta automática de IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/ai/history/{phone_number}",
    summary="Limpiar historial de conversación",
    description="""Limpia el historial de conversación de un usuario.
    
    🔒 **Requiere autenticación.**
    
    Útil para:
    - Reiniciar una conversación
    - Liberar memoria
    - Resolver problemas de contexto
    """,
    responses={
        200: {"description": "Historial limpiado exitosamente"},
        401: {"description": "No autorizado"},
    },
)
async def clear_ai_history(
    phone_number: str, current_user: dict = Depends(get_current_user)
):
    """Limpia el historial de conversación de un usuario."""
    ai_service.clear_history(phone_number)
    return {"success": True, "message": f"Historial limpiado para {phone_number}"}


@router.get(
    "/ai/statistics",
    summary="Estadísticas del servicio de IA",
    description="""Obtiene estadísticas del servicio de IA para WhatsApp.
    
    🔒 **Requiere autenticación.**
    
    Muestra:
    - Conversaciones activas
    - Total de mensajes procesados
    - Configuración del servicio
    """,
    responses={
        200: {"description": "Estadísticas obtenidas exitosamente"},
        401: {"description": "No autorizado"},
    },
)
async def get_ai_statistics(current_user: dict = Depends(get_current_user)):
    """Obtiene estadísticas del servicio de IA."""
    return ai_service.get_statistics()


@router.post(
    "/send/document-message",
    response_model=WhatsAppMessageSendResponse,
    summary="Enviar documento (alternativo)",
    description="Endpoint alternativo para envío de documentos",
)
async def send_document_message(
    to: str = Query(description="Número de teléfono del destinatario"),
    document_url: Optional[str] = Query(
        default=None, description="URL pública del documento"
    ),
    document_id: Optional[str] = Query(
        default=None, description="ID de documento subido"
    ),
    filename: Optional[str] = Query(default=None, description="Nombre del archivo"),
    caption: Optional[str] = Query(default=None, description="Caption del documento"),
    current_user: Dict = Depends(get_current_user),
):
    """Envía un documento."""

    try:
        response = await whatsapp_service.send_document(
            to, document_url, document_id, filename, caption
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando documento: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error al enviar documento: {str(e)}"
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
        500: {"description": "Error al enviar ubicación"},
    },
)
async def send_location_message(
    to: str = Query(description="Número de teléfono del destinatario"),
    latitude: float = Query(description="Latitud"),
    longitude: float = Query(description="Longitud"),
    name: Optional[str] = Query(default=None, description="Nombre del lugar"),
    address: Optional[str] = Query(default=None, description="Dirección"),
    current_user: Dict = Depends(get_current_user),
):
    """Envía una ubicación."""

    try:
        response = await whatsapp_service.send_location(
            to, latitude, longitude, name, address
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando ubicación: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error al enviar ubicación: {str(e)}"
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
        500: {"description": "Error al enviar plantilla"},
    },
)
async def send_template_message(
    to: str = Query(description="Número de teléfono del destinatario"),
    template_name: str = Query(description="Nombre de la plantilla aprobada"),
    language_code: str = Query(default="es", description="Código de idioma"),
    current_user: Dict = Depends(get_current_user),
):
    """Envía una plantilla aprobada."""

    try:
        response = await whatsapp_service.send_template(
            to, template_name, language_code
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando plantilla: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error al enviar plantilla: {str(e)}"
        )
