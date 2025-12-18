"""
Endpoints para gestión de emails recibidos a través de Azure Event Grid.
Maneja la recepción de emails entrantes y reportes de entrega.
"""

from dataclasses import Field
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, List
from datetime import datetime
import email
from email import policy
import logging
import re
from bs4 import BeautifulSoup
from app.core.http_request import get_text
from app.services.email_service import email_service
from app.services.email_queue import queue_email, EmailTask, email_queue
from app.models.requests import EmailSendRequest
from app.models.responses import EmailSendResponse, WebhookEventResponse
from app.database.connection import execute_sp

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de email
router = APIRouter()


@router.post(
    "/send",
    summary="Enviar email",
    description="""Envía un email utilizando SMTP de Microsoft 365 en background.
    
    El email se agrega a una cola de envío y se procesa en segundo plano,
    permitiendo una respuesta inmediata sin esperar el envío completo.
    
    **Parámetros:**
    - to: email del destinatario
    - subject: asunto
    - body: contenido del mensaje (HTML o texto plano)
    
    **Ejemplo de uso:**
    ```json
    {
        "to": "usuario@ejemplo.com",
        "subject": "Bienvenido a Ezekl Budget",
        "body": "<h1>¡Hola!</h1><p>Gracias por registrarte.</p>"
    }
    ```
    """
)
async def send_email(
    to: str = Field(..., description="Email del destinatario", example="ebaltodano@itqscr.com"),
    subject: str = Field(..., description="Asunto del email", example="Bienvenido a Ezekl Budget"),
    body: str = Field(..., description="Contenido del email (HTML o texto plano)", example="<h1>¡Hola!</h1><p>Gracias por registrarte.</p>")
) -> Dict[str, Any]:
    """
    Encola un email para envío en background.
    
    Args:
        to: Email del destinatario
        subject: Asunto del email
        body: Contenido del email (HTML o texto plano)
        
    Returns:
        Dict con success, message, taskId y timestamp
    """
    try:
        # Detectar si es HTML o texto plano
        is_html = body.strip().startswith('<')
        
        # Agregar email a la cola de envío
        task_id = await queue_email(
            to=[to],
            subject=subject,
            message=body,
            is_html=is_html
        )
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"📬 Email encolado para {to} | Task ID: {task_id} | Subject: {subject}")
        
        return {
            "success": True,
            "message": f"Email encolado para envío a {to}",
            "to": to,
            "subject": subject,
            "taskId": task_id,
            "status": "queued",
            "timestamp": timestamp
        }
        
    except Exception as e:
        error_msg = f"Error al encolar email: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post(
    "/webhook",
    summary="Webhook de emails entrantes",
    description="""Recibe emails entrantes y los guarda en la base de datos.
    
    Este webhook procesa emails entrantes, extrae el último mensaje limpio
    (sin la cadena de respuestas) y guarda toda la información en la base de datos.
    
    **Campos esperados:**
    - `messageId`: ID único del mensaje
    - `from`: Remitente del email
    - `to`: Destinatario(s) del email
    - `subject`: Asunto del email
    - `receivedDate`: Fecha de recepción
    - `body`: Contenido HTML completo del email
    - `attachments`: Lista de adjuntos (opcional)
    
    **Funcionalidades:**
    - Extracción automática del último mensaje (sin cadena de respuestas)
    - Guardado en base de datos con timestamp
    - Procesamiento de contenido HTML
    - Logging detallado
    
    **Ejemplo de uso:**
    ```json
    {
        "messageId": "AAMkA...",
        "from": "usuario@ejemplo.com",
        "to": "destino@ejemplo.com",
        "subject": "Asunto del correo",
        "receivedDate": "2025-12-17T18:05:11+00:00",
        "body": "<html>Contenido del email...</html>",
        "attachments": []
    }
    ```
    """
)
async def email_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Webhook para recibir emails entrantes y guardarlos en BD.
    
    Similar a receive_webhook pero específico para emails.
    Extrae el mensaje limpio del body HTML y guarda en la base de datos.

    Args:
        payload: Datos del email entrante

    Returns:
        Dict con success, message, idLog y timestamp
    """
    try:
        # Generar timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Extraer el mensaje limpio del body HTML si existe
        body_html = payload.get("body", "")
        if body_html:
            message_content = _extract_last_message_from_html(body_html)
            # Agregar el campo "message" al payload
            payload["message"] = message_content
        
        # Preparar datos para el stored procedure
        sp_params = {
            "typeLog": "Email Inbound",
            "log": payload
        }
        
        # Ejecutar stored procedure
        result = await execute_sp("spLogAdd", sp_params)
        
        id_log = result.get("idLog")
        from_address = payload.get("from", "N/A")
        subject = payload.get("subject", "N/A")
        message_content = payload.get("message", "")
        
        logger.info(f"✅ Email recibido y guardado en BD con ID: {id_log} | From: {from_address} | Subject: {subject}")
        
        # Enviar copia de confirmación de recepción
        try:
            confirmation_subject = f"✅ Recibido: {subject}"
            confirmation_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #4CAF50;">✅ Email Recibido - Ezekl Budget</h2>
                    <p>Hemos recibido tu email correctamente y ha sido registrado en nuestro sistema.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>Detalles del email recibido:</strong>
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>ID de registro:</strong> {id_log}</li>
                            <li><strong>De:</strong> {from_address}</li>
                            <li><strong>Asunto:</strong> {subject}</li>
                            <li><strong>Fecha:</strong> {timestamp}</li>
                        </ul>
                    </div>
                    
                    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>Mensaje recibido:</strong>
                        <p style="margin: 10px 0; white-space: pre-wrap;">{message_content[:500]}{"..." if len(message_content) > 500 else ""}</p>
                    </div>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        <em>Este es un mensaje automático de confirmación. No es necesario responder.</em>
                    </p>
                </body>
            </html>
            """
            
            # Encolar email de confirmación
            task_id = await queue_email(
                to=[from_address],
                subject=confirmation_subject,
                message=confirmation_body,
                is_html=True
            )
            
            logger.info(f"📧 Confirmación encolada para {from_address} | Task ID: {task_id}")
            
        except Exception as email_error:
            # No fallar el webhook si el envío de confirmación falla
            logger.error(f"⚠️ Error al encolar confirmación de recepción: {str(email_error)}")
        
        return {
            "success": True,
            "message": "Email recibido y guardado en base de datos",
            "idLog": id_log,
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error al procesar email webhook: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar email: {str(e)}"
        )


async def _process_inbound_email(data: Dict[str, Any]) -> int | None:
    """
    Procesa un email entrante desde Azure Event Grid o Microsoft Graph API.

    Args:
        data: Datos del evento de email entrante
        
    Returns:
        ID del log creado en BD o None si falla
    """
    try:
        # Detectar si es formato de Microsoft Graph API (con messageId, body, etc.)
        if "messageId" in data and "body" in data:
            # Formato directo de Microsoft Graph
            message_id = data.get("messageId")
            from_address = data.get("from")
            to_addresses = data.get("to")
            subject = data.get("subject")
            received_date = data.get("receivedDate")
            body_html = data.get("body", "")
            attachments = data.get("attachments", [])
            
            # Extraer solo el último mensaje del HTML (sin cadena de respuestas)
            message_content = _extract_last_message_from_html(body_html)
            
            # Preparar payload para guardar en BD
            email_data = {
                "messageId": message_id,
                "from": from_address,
                "to": to_addresses,
                "subject": subject,
                "receivedDate": received_date,
                "message": message_content,  # Solo el último mensaje limpio
                "body": body_html,  # Body completo para referencia
                "attachments": attachments
            }
            
            # Guardar en base de datos usando spLogAdd
            sp_params = {
                "typeLog": "Email Inbound",
                "log": email_data
            }
            
            result = await execute_sp("spLogAdd", sp_params)
            id_log = result.get('idLog')
            logger.info(f"✅ Email guardado en BD con ID: {id_log} | From: {from_address} | Subject: {subject}")
            return id_log
            
        # Formato de Azure Event Grid con MIME URL
        elif "emailContentUrl" in data:
            mime_url = data.get("emailContentUrl")
            to_addresses = data.get("to", [])
            from_address = data.get("from")
            subject = data.get("subject")

            # Descargar contenido MIME si está disponible
            if mime_url:
                # Usar nuestro cliente HTTP para descargas asíncronas
                mime_content = await get_text(mime_url)

                # Parsear el mensaje MIME
                msg = email.message_from_string(mime_content, policy=policy.default)

                # Extraer cuerpo de texto y HTML
                text_body, html_body = _extract_email_body(msg)
                
                # Extraer solo el último mensaje
                message_content = _extract_last_message_from_html(html_body) if html_body else text_body

                # Preparar payload para guardar en BD
                email_data = {
                    "from": from_address,
                    "to": to_addresses,
                    "subject": subject,
                    "message": message_content,
                    "text_body": text_body,
                    "html_body": html_body
                }
                
                # Procesar adjuntos si existen
                attachments = list(msg.iter_attachments())
                if attachments:
                    email_data["attachments_count"] = len(attachments)
                
                # Guardar en base de datos
                sp_params = {
                    "typeLog": "Email Inbound MIME",
                    "log": email_data
                }
                
                result = await execute_sp("spLogAdd", sp_params)
                id_log = result.get('idLog')
                logger.info(f"✅ Email MIME guardado en BD con ID: {id_log} | From: {from_address}")
                return id_log
            else:
                logger.warning("No se proporcionó URL de contenido MIME")
                return None
        else:
            logger.warning(f"Formato de email no reconocido: {data.keys()}")
            return None
            
    except Exception as e:
        logger.error(f"Error procesando email entrante: {str(e)}")
        return None


async def _process_delivery_report(data: Dict[str, Any]) -> None:
    """
    Procesa un reporte de entrega/rebote de email.

    Args:
        data: Datos del reporte de entrega
    """

    # TODO: Implementar lógica para manejar reportes de entrega
    # - Actualizar estado de emails enviados
    # - Manejar rebotes
    # - Actualizar métricas
    # - Etc.


def _extract_last_message_from_html(html_content: str) -> str:
    """
    Extrae solo el último mensaje de un email HTML, eliminando la cadena de respuestas.
    
    Args:
        html_content: Contenido HTML completo del email
        
    Returns:
        Texto del último mensaje sin la cadena de respuestas
    """
    if not html_content:
        return ""
    
    try:
        # Parsear HTML con BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Buscar el separador de respuestas (común en Outlook y otros clientes)
        # Puede ser <hr>, <div id="divRplyFwdMsg">, etc.
        separators = [
            soup.find('hr'),  # Separador horizontal
            soup.find('div', id='divRplyFwdMsg'),  # Outlook
            soup.find('div', class_='gmail_quote'),  # Gmail
            soup.find('blockquote')  # Quotes generales
        ]
        
        # Encontrar el primer separador válido
        first_separator = None
        for sep in separators:
            if sep:
                first_separator = sep
                break
        
        if first_separator:
            # Eliminar todo después del separador (incluido el separador)
            for element in [first_separator] + list(first_separator.find_all_next()):
                if element.parent:
                    element.extract()
        
        # Obtener el texto limpio
        text = soup.get_text(separator='\n', strip=True)
        
        # Limpiar líneas vacías múltiples
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extrayendo último mensaje del HTML: {str(e)}")
        # Fallback: intentar extraer texto básico
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(strip=True)[:500]  # Limitar a 500 caracteres
        except:
            return "[Error al procesar contenido del email]"


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
