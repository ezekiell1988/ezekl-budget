"""
Endpoints para gestión de emails recibidos a través de Azure Event Grid.
Maneja la recepción de emails entrantes y reportes de entrega.
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import json
import email
from email import policy
import logging
from app.core.http_request import get_text
from app.core.config import settings
from app.services.email_service import email_service
from app.models.responses import EmailSendRequest, EmailSendResponse

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de email
router = APIRouter()


@router.post("/send")
async def send_email(request: EmailSendRequest) -> EmailSendResponse:
    """
    Endpoint para enviar emails usando Azure Communication Services.
    
    Args:
        request: Datos del email a enviar (destinatarios, asunto, contenido)
        
    Returns:
        EmailSendResponse: Resultado del envío
        
    Raises:
        HTTPException: Si ocurre un error de validación
    """
    # Validar que al menos uno de los contenidos esté presente
    if not request.html_content and not request.text_content:
        raise HTTPException(
            status_code=400, 
            detail="Se debe proporcionar al menos html_content o text_content"
        )
    
    # Usar el servicio centralizado para enviar el email
    return await email_service.send_email_from_request(request)


@router.post("/webhook")
async def email_webhook(req: Request) -> Dict[str, Any]:
    """
    Webhook para recibir eventos de email desde Azure Event Grid.

    Maneja:
    - Validación de suscripción de Azure Event Grid
    - Procesamiento de emails entrantes
    - Reportes de entrega/rebote

    Args:
        req: Request object de FastAPI con headers y body

    Returns:
        Dict con la respuesta apropiada según el tipo de evento
    """
    try:
        # 1) Obtener headers y body
        aeg_type = req.headers.get("aeg-event-type")
        body = await req.json()

        logger.info(f"Recibido evento de tipo: {aeg_type}")

        # 2) Validación de suscripción de Azure Event Grid
        if aeg_type == "SubscriptionValidation":
            validation_code = body[0]["data"]["validationCode"]
            logger.info("Validando suscripción de Azure Event Grid")
            return {"validationResponse": validation_code}

        # 3) Procesamiento de eventos normales
        if aeg_type == "Notification":
            for ev in body:
                event_type = ev.get("eventType", "")
                data = ev.get("data", {})

                # Procesamiento de correos entrantes
                if event_type.endswith("InboundEmailReceived"):
                    await _process_inbound_email(data)

                # Procesamiento de reportes de entrega/rebote (opcional)
                elif event_type.endswith("EmailDeliveryReportReceived"):
                    await _process_delivery_report(data)

        return {"ok": True, "message": "Evento procesado exitosamente"}

    except Exception as e:
        logger.error(f"Error procesando evento de email: {str(e)}")
        # No lanzamos excepción para evitar reintentos innecesarios desde Azure
        return {"ok": False, "error": "Error interno procesando evento"}


async def _process_inbound_email(data: Dict[str, Any]) -> None:
    """
    Procesa un email entrante desde Azure Event Grid.

    Args:
        data: Datos del evento de email entrante
    """
    mime_url = data.get("emailContentUrl")
    to_addresses = data.get("to", [])
    from_address = data.get("from")
    subject = data.get("subject")

    logger.info(f"Procesando email de {from_address} a {to_addresses}")
    logger.info(f"Asunto: {subject}")

    # Descargar contenido MIME si está disponible
    if mime_url:
        try:
            # Usar nuestro cliente HTTP para descargas asíncronas
            mime_content = await get_text(mime_url)

            # Parsear el mensaje MIME
            msg = email.message_from_string(mime_content, policy=policy.default)

            # Extraer cuerpo de texto y HTML
            text_body, html_body = _extract_email_body(msg)

            # TODO: Implementar lógica de negocio aquí
            # - Guardar en base de datos
            # - Procesar adjuntos si los hay
            # - Enviar notificaciones
            # - Etc.

            # Log básico del contenido (limitado por seguridad)
            logger.info(f"FROM: {from_address}")
            logger.info(f"TO: {to_addresses}")
            logger.info(f"SUBJECT: {subject}")
            if text_body:
                logger.info(f"TEXT PREVIEW: {text_body[:500]}...")

            # Procesar adjuntos si existen
            attachments = list(msg.iter_attachments())
            if attachments:
                logger.info(f"Email contiene {len(attachments)} adjunto(s)")
                # TODO: Implementar procesamiento de adjuntos

        except Exception as e:
            logger.error(f"Error descargando o procesando contenido MIME: {str(e)}")
    else:
        logger.warning("No se proporcionó URL de contenido MIME")


async def _process_delivery_report(data: Dict[str, Any]) -> None:
    """
    Procesa un reporte de entrega/rebote de email.

    Args:
        data: Datos del reporte de entrega
    """
    logger.info("Procesando reporte de entrega:")
    logger.info(json.dumps(data, indent=2))

    # TODO: Implementar lógica para manejar reportes de entrega
    # - Actualizar estado de emails enviados
    # - Manejar rebotes
    # - Actualizar métricas
    # - Etc.


def _extract_email_body(
    msg: email.message.EmailMessage,
) -> tuple[str | None, str | None]:
    """
    Extrae el contenido de texto plano y HTML de un mensaje de email.

    Args:
        msg: Mensaje de email parseado

    Returns:
        Tupla con (texto_plano, html) o (None, None) si no hay contenido
    """
    text_body = None
    html_body = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()

            if content_type == "text/plain" and text_body is None:
                text_body = part.get_content()
            elif content_type == "text/html" and html_body is None:
                html_body = part.get_content()
    else:
        if msg.get_content_type() == "text/plain":
            text_body = msg.get_content()
        elif msg.get_content_type() == "text/html":
            html_body = msg.get_content()

    return text_body, html_body
