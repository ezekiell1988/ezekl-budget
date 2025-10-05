"""
Endpoints para gestión de emails recibidos a través de Azure Event Grid.
Maneja la recepción de emails entrantes y reportes de entrega.
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, List
import json
from datetime import datetime
import email
from email import policy
import logging
from app.core.http_request import get_text
from app.core.config import settings
from app.services.email_service import email_service
from app.models.requests import EmailSendRequest, WebhookEventRequest
from app.models.responses import EmailSendResponse, WebhookEventResponse

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de email
router = APIRouter()


@router.post(
    "/send",
    summary="Enviar email",
    description="""Envía un email utilizando Azure Communication Services.
    
    Este endpoint permite enviar emails a uno o múltiples destinatarios con contenido
    en formato HTML y/o texto plano. Requiere que se proporcione al menos uno de
    los dos tipos de contenido.
    
    **Características:**
    - Soporte para múltiples destinatarios (TO, CC, BCC)
    - Contenido HTML y/o texto plano
    - Validación automática de formato de email
    - Integración con Azure Communication Services
    
    **Ejemplo de uso:**
    ```json
    {
        "to": ["usuario@ejemplo.com"],
        "subject": "Bienvenido a Ezekl Budget",
        "html_content": "<h1>¡Hola!</h1><p>Gracias por registrarte.</p>",
        "text_content": "¡Hola! Gracias por registrarte."
    }
    ```
    """,
    response_description="Confirmación del envío con detalles del resultado"
)
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


@router.post(
    "/webhook",
    summary="Webhook de eventos de email",
    description="""Recibe y procesa eventos de email desde Azure Event Grid.
    
    Este webhook maneja automáticamente diferentes tipos de eventos relacionados
    con emails, incluyendo la validación inicial de suscripción y el procesamiento
    de emails entrantes.
    
    **Tipos de eventos soportados:**
    - `SubscriptionValidation`: Validación inicial del webhook con Azure Event Grid
    - `InboundEmailReceived`: Emails recibidos en las direcciones configuradas
    - `EmailDeliveryReportReceived`: Reportes de entrega, rebotes y fallos
    
    **Funcionalidades:**
    - Validación automática de suscripción Azure Event Grid
    - Procesamiento de emails entrantes con análisis MIME completo
    - Extracción de contenido HTML y texto plano
    - Manejo de adjuntos (logging por ahora)
    - Reportes de entrega y métricas
    
    **Seguridad:**
    - Validación de headers de Azure Event Grid
    - Manejo seguro de errores sin exposición de detalles internos
    - Logging detallado para monitoreo y debugging
    
    **Nota:** Este endpoint debe ser configurado como el destino del webhook
    en Azure Event Grid para recibir eventos de email automáticamente.
    """,
    response_model=WebhookEventResponse,
    response_description="Respuesta de procesamiento del evento (validationResponse para suscripción, ok/error para eventos)"
)
async def email_webhook(events: List[Dict[str, Any]], req: Request) -> WebhookEventResponse:
    """
    Webhook para recibir eventos de email desde Azure Event Grid.

    Maneja:
    - Validación de suscripción de Azure Event Grid
    - Procesamiento de emails entrantes
    - Reportes de entrega/rebote

    Args:
        events: Lista de eventos de Azure Event Grid
        req: Request object de FastAPI con headers

    Returns:
        WebhookEventResponse: Respuesta estructurada según el tipo de evento
    """
    try:
        # 1) Obtener headers
        aeg_type = req.headers.get("aeg-event-type")
        processed_at = datetime.utcnow().isoformat() + "Z"

        logger.info(f"Recibido evento de tipo: {aeg_type}")
        logger.info(f"Número de eventos: {len(events)}")

        # 2) Validación de suscripción de Azure Event Grid
        if aeg_type == "SubscriptionValidation":
            if events and "data" in events[0] and "validationCode" in events[0]["data"]:
                validation_code = events[0]["data"]["validationCode"]
                logger.info("Validando suscripción de Azure Event Grid")
                return WebhookEventResponse(validationResponse=validation_code)
            else:
                logger.error("Evento de validación sin código")
                return WebhookEventResponse(
                    ok=False,
                    message="Evento de validación inválido",
                    event_type="SubscriptionValidation",
                    processed_at=processed_at
                )

        # 3) Procesamiento de eventos normales
        if aeg_type == "Notification":
            events_processed = 0
            for ev in events:
                event_type = ev.get("eventType", "")
                data = ev.get("data", {})

                # Procesamiento de correos entrantes
                if event_type.endswith("InboundEmailReceived"):
                    await _process_inbound_email(data)
                    events_processed += 1

                # Procesamiento de reportes de entrega/rebote (opcional)
                elif event_type.endswith("EmailDeliveryReportReceived"):
                    await _process_delivery_report(data)
                    events_processed += 1

            return WebhookEventResponse(
                ok=True,
                message=f"Procesados {events_processed} evento(s) exitosamente",
                event_type="Notification",
                processed_at=processed_at
            )

        # 4) Tipo de evento no reconocido
        logger.warning(f"Tipo de evento no reconocido: {aeg_type}")
        return WebhookEventResponse(
            ok=False,
            message=f"Tipo de evento no reconocido: {aeg_type}",
            event_type=aeg_type or "Unknown",
            processed_at=processed_at
        )

    except Exception as e:
        logger.error(f"Error procesando evento de email: {str(e)}")
        # No lanzamos excepción para evitar reintentos innecesarios desde Azure
        return WebhookEventResponse(
            ok=False,
            message="Error interno procesando evento",
            event_type="Error",
            processed_at=datetime.utcnow().isoformat() + "Z"
        )


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
