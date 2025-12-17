"""
Servicio centralizado para gestión de emails usando SMTP.
Este módulo proporciona funcionalidad reutilizable para el envío de emails
desde cualquier parte de la aplicación.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from app.core.config import settings
from app.models.requests import EmailSendRequest
from app.models.responses import EmailSendResponse

# Configurar logging
logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio para gestión de emails usando SMTP.
    
    Proporciona métodos para enviar emails de forma asíncrona con configuración
    flexible de remitente, múltiples destinatarios y soporte para contenido
    HTML y texto plano.
    """
    
    def __init__(self):
        """Inicializa el servicio de email con la configuración SMTP."""
        pass
    
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
        Envía un email usando SMTP.
        
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
            sender_address = from_address or settings.smtp_from
            
            # Crear mensaje MIME
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_address
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject
            
            # Agregar CC si existe
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Agregar Reply-To si existe
            if reply_to:
                msg['Reply-To'] = reply_to
            
            # Agregar contenido (primero texto plano, luego HTML)
            if text_content:
                msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            if html_content:
                msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # Preparar lista de todos los destinatarios
            all_recipients = to.copy()
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
            
            # Conectar y enviar email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
                server.set_debuglevel(0)
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg, to_addrs=all_recipients)
            
            logger.info(f"✅ Email enviado a {', '.join(to)} | Subject: {subject}")
            
            return EmailSendResponse(
                success=True,
                message=f"Email enviado exitosamente a {len(all_recipients)} destinatario(s)"
            )
            
        except ValueError as ve:
            logger.error(f"Error de validación enviando email: {str(ve)}")
            return EmailSendResponse(
                success=False,
                message=f"Error de validación: {str(ve)}"
            )
        
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "Error de autenticación SMTP. Verifica usuario y contraseña."
            logger.error(f"❌ {error_msg}: {str(e)}")
            return EmailSendResponse(
                success=False,
                message=error_msg
            )
            
        except smtplib.SMTPException as e:
            error_msg = f"Error SMTP: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return EmailSendResponse(
                success=False,
                message=error_msg
            )
            
        except Exception as e:
            error_msg = f"Error inesperado enviando email: {str(e)}"
            logger.error(f"❌ {error_msg}")
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