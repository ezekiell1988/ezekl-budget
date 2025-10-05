"""
Servicio centralizado para gestión de emails usando Azure Communication Services.
Este módulo proporciona funcionalidad reutilizable para el envío de emails
desde cualquier parte de la aplicación.
"""

from azure.communication.email import EmailClient
from typing import List, Optional
import logging
from app.core.config import settings
from app.models.requests import EmailSendRequest
from app.models.responses import EmailSendResponse

# Configurar logging
logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio para gestión de emails usando Azure Communication Services.
    
    Proporciona métodos para enviar emails de forma asíncrona con configuración
    flexible de remitente, múltiples destinatarios y soporte para contenido
    HTML y texto plano.
    """
    
    def __init__(self):
        """Inicializa el servicio de email con la configuración de Azure."""
        self._client = None
    
    @property
    def client(self) -> EmailClient:
        """
        Cliente de Azure Communication Services con lazy loading.
        
        Returns:
            EmailClient: Cliente configurado para envío de emails
        """
        if self._client is None:
            connection_string = (
                f"endpoint={settings.azure_communication_endpoint};"
                f"accesskey={settings.azure_communication_key}"
            )
            self._client = EmailClient.from_connection_string(connection_string)
        return self._client
    
    async def send_email(
        self,
        to: List[str],
        subject: str,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        from_address: Optional[str] = None
    ) -> EmailSendResponse:
        """
        Envía un email usando Azure Communication Services.
        
        Args:
            to: Lista de direcciones de destinatarios
            subject: Asunto del email
            html_content: Contenido HTML opcional
            text_content: Contenido de texto plano opcional
            cc: Lista de direcciones para copia (CC)
            bcc: Lista de direcciones para copia oculta (BCC)
            reply_to: Dirección para respuestas
            from_address: Dirección del remitente (opcional, usa la por defecto si no se proporciona)
            
        Returns:
            EmailSendResponse: Resultado del envío con status y mensaje
            
        Raises:
            ValueError: Si no se proporciona ningún tipo de contenido
            Exception: Si ocurre un error durante el envío
        """
        try:
            # Validar que al menos uno de los contenidos esté presente
            if not html_content and not text_content:
                raise ValueError("Se debe proporcionar al menos html_content o text_content")
            
            # Determinar el remitente
            sender_address = from_address or settings.azure_communication_sender_address
            
            # Construir el mensaje de email según el formato de Azure
            message = {
                "senderAddress": sender_address,
                "recipients": {
                    "to": [{"address": str(email)} for email in to]
                },
                "content": {
                    "subject": subject,
                }
            }
            
            # Agregar contenido HTML y/o texto
            if text_content:
                message["content"]["plainText"] = text_content
            if html_content:
                message["content"]["html"] = html_content
            
            logger.info(f"Enviando email a {to} con asunto: {subject}")
            
            # Enviar el email
            poller = self.client.begin_send(message)
            result = poller.result()
            
            logger.info(f"Email enviado exitosamente a: {', '.join(to)}")
            
            return EmailSendResponse(
                success=True,
                message="Email enviado exitosamente"
            )
            
        except ValueError as ve:
            # Error de validación - devolver como error de aplicación
            logger.error(f"Error de validación enviando email: {str(ve)}")
            return EmailSendResponse(
                success=False,
                message=f"Error de validación: {str(ve)}"
            )
            
        except Exception as e:
            # Error general durante el envío
            error_msg = f"Error enviando email: {str(e)}"
            logger.error(error_msg)
            
            return EmailSendResponse(
                success=False,
                message=error_msg
            )
    
    async def send_email_from_request(self, request: EmailSendRequest) -> EmailSendResponse:
        """
        Envía un email usando un objeto EmailSendRequest.
        
        Args:
            request: Objeto con los datos del email a enviar
            
        Returns:
            EmailSendResponse: Resultado del envío
        """
        return await self.send_email(
            to=[str(email) for email in request.to],
            subject=request.subject,
            html_content=request.html_content,
            text_content=request.text_content,
            cc=[str(email) for email in request.cc] if request.cc else None,
            bcc=[str(email) for email in request.bcc] if request.bcc else None,
            reply_to=str(request.reply_to) if request.reply_to else None
        )


# Instancia global del servicio para uso en la aplicación
email_service = EmailService()


# Funciones de conveniencia para uso directo
async def send_email(
    to: List[str],
    subject: str,
    html_content: Optional[str] = None,
    text_content: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    reply_to: Optional[str] = None,
    from_address: Optional[str] = None
) -> EmailSendResponse:
    """
    Función de conveniencia para enviar emails.
    
    Args:
        to: Lista de direcciones de destinatarios
        subject: Asunto del email
        html_content: Contenido HTML opcional
        text_content: Contenido de texto plano opcional
        cc: Lista de direcciones para copia (CC)
        bcc: Lista de direcciones para copia oculta (BCC)
        reply_to: Dirección para respuestas
        from_address: Dirección del remitente opcional
        
    Returns:
        EmailSendResponse: Resultado del envío
    """
    return await email_service.send_email(
        to=to,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        cc=cc,
        bcc=bcc,
        reply_to=reply_to,
        from_address=from_address
    )


async def send_notification_email(
    to: List[str],
    subject: str,
    message: str,
    is_html: bool = False,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
) -> EmailSendResponse:
    """
    Función de conveniencia para enviar emails de notificación simples.
    
    Args:
        to: Lista de destinatarios
        subject: Asunto del email
        message: Contenido del mensaje
        is_html: Si True, trata el mensaje como HTML; si False, como texto plano
        cc: Lista de destinatarios en copia (opcional)
        bcc: Lista de destinatarios en copia oculta (opcional)
        
    Returns:
        EmailSendResponse: Resultado del envío
    """
    if is_html:
        return await send_email(to=to, subject=subject, html_content=message, cc=cc, bcc=bcc)
    else:
        return await send_email(to=to, subject=subject, text_content=message, cc=cc, bcc=bcc)