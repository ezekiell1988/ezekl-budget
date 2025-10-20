"""
Servicio para integración con WhatsApp Business API.
Proporciona métodos para enviar mensajes de texto, imágenes, videos, documentos, 
ubicaciones, contactos, mensajes interactivos y autenticación de usuarios.
"""

import aiohttp
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException

from app.core.config import settings
from app.core.http_request import HTTPClient
from app.core.redis import redis_client
from app.models.whatsapp import (
    WhatsAppMessageSendRequest,
    WhatsAppMessageSendResponse,
    
)

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Servicio principal para integración con WhatsApp Business API.
    
    Proporciona métodos de alto nivel para enviar diferentes tipos de mensajes:
    - Mensajes de texto
    - Imágenes
    - Videos
    - Documentos
    - Audios
    - Ubicaciones
    - Contactos
    - Plantillas aprobadas
    - Mensajes interactivos con botones
    """
    
    def __init__(self):
        """Inicializa el servicio de WhatsApp."""
        self.access_token = settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.api_version = settings.whatsapp_api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        
        # Cliente HTTP con headers por defecto
        self.http_client = HTTPClient(
            base_url=self.base_url,
            default_headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            } if self.access_token else {}
        )
        
        if self.access_token and self.phone_number_id:
            pass  # Logger eliminado
        else:
            logger.warning("⚠️ Servicio de WhatsApp no configurado completamente")
    
    @property
    def is_configured(self) -> bool:
        """Verifica si el servicio está configurado correctamente."""
        return bool(self.access_token and self.phone_number_id)
    
    def _check_configuration(self):
        """Verifica la configuración antes de realizar operaciones."""
        if not self.is_configured:
            raise HTTPException(
                status_code=500,
                detail="WhatsApp no está configurado. Verifica WHATSAPP_ACCESS_TOKEN y WHATSAPP_PHONE_NUMBER_ID en .env"
            )
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Realiza una petición HTTP a la API de WhatsApp Business.
        
        Args:
            method: Método HTTP (GET, POST)
            endpoint: Endpoint relativo (ej: "messages")
            data: Datos JSON para el body
            params: Parámetros de query string
            
        Returns:
            Dict con la respuesta JSON de la API
            
        Raises:
            HTTPException: Si la petición falla
        """
        self._check_configuration()
        
        try:
            # Usar los métodos de conveniencia que manejan la sesión correctamente
            if method == "POST":
                # Para POST con JSON, necesitamos manejar la sesión directamente
                full_url = f"{self.base_url}/{endpoint}"
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(full_url, json=data, headers=headers, params=params) as response:
                        response_data = await response.json()
                        
                        # Verificar si hay errores
                        if response.status >= 400:
                            error_info = response_data.get("error", {})
                            error_message = error_info.get("message", "Error desconocido")
                            error_code = error_info.get("code", "UNKNOWN")
                            
                            logger.error(f"❌ Error de WhatsApp API: [{error_code}] {error_message}")
                            logger.error(f"Response completo: {response_data}")
                            
                            raise HTTPException(
                                status_code=response.status,
                                detail=f"Error de WhatsApp API: {error_message}"
                            )
                        
                        return response_data
                        
            elif method == "GET":
                response_data = await self.http_client.get_json(f"{endpoint}", params=params)
                return response_data
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
                        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error de conexión con WhatsApp API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error de conexión con WhatsApp API: {str(e)}"
            )
    
    async def send_message(self, message_request: WhatsAppMessageSendRequest) -> WhatsAppMessageSendResponse:
        """
        Envía un mensaje de WhatsApp.
        
        Args:
            message_request: Request con los datos del mensaje
            
        Returns:
            WhatsAppMessageSendResponse con la información del mensaje enviado
            
        Raises:
            HTTPException: Si hay error al enviar el mensaje
        """
        
        # Convertir el request a dict para enviarlo a la API
        message_data = message_request.model_dump(exclude_none=True)
        
        response = await self._make_request("POST", "messages", data=message_data)
        
        
        return WhatsAppMessageSendResponse(**response)
    
    async def send_text_message(self, to: str, body: str, preview_url: bool = False) -> WhatsAppMessageSendResponse:
        """
        Envía un mensaje de texto simple.
        
        Args:
            to: Número de teléfono del destinatario (formato internacional con código de país)
            body: Contenido del mensaje
            preview_url: Si es True, muestra preview de URLs en el mensaje
            
        Returns:
            WhatsAppMessageSendResponse con la información del mensaje enviado
            
        Example:
            await whatsapp_service.send_text_message(
                to="5491112345678",
                body="Hola, ¿cómo estás?"
            )
        """
        message_request = WhatsAppMessageSendRequest(
            to=to,
            type="text",
            text={
                "body": body,
                "preview_url": preview_url
            }
        )
        
        return await self.send_message(message_request)
    
    async def send_image(
        self, 
        to: str, 
        image_url: Optional[str] = None,
        image_id: Optional[str] = None,
        caption: Optional[str] = None
    ) -> WhatsAppMessageSendResponse:
        """
        Envía una imagen.
        
        Args:
            to: Número de teléfono del destinatario
            image_url: URL pública de la imagen (debe ser accesible por WhatsApp)
            image_id: ID de imagen previamente subida a WhatsApp
            caption: Caption opcional para la imagen
            
        Returns:
            WhatsAppMessageSendResponse
            
        Note:
            Debes proporcionar image_url O image_id, no ambos.
        """
        if not image_url and not image_id:
            raise HTTPException(
                status_code=400,
                detail="Debes proporcionar image_url o image_id"
            )
        
        image_data = {}
        if image_url:
            image_data["link"] = image_url
        if image_id:
            image_data["id"] = image_id
        if caption:
            image_data["caption"] = caption
        
        message_request = WhatsAppMessageSendRequest(
            to=to,
            type="image",
            image=image_data
        )
        
        return await self.send_message(message_request)
    
    async def send_video(
        self,
        to: str,
        video_url: Optional[str] = None,
        video_id: Optional[str] = None,
        caption: Optional[str] = None
    ) -> WhatsAppMessageSendResponse:
        """
        Envía un video.
        
        Args:
            to: Número de teléfono del destinatario
            video_url: URL pública del video
            video_id: ID de video previamente subido
            caption: Caption opcional
            
        Returns:
            WhatsAppMessageSendResponse
        """
        if not video_url and not video_id:
            raise HTTPException(
                status_code=400,
                detail="Debes proporcionar video_url o video_id"
            )
        
        video_data = {}
        if video_url:
            video_data["link"] = video_url
        if video_id:
            video_data["id"] = video_id
        if caption:
            video_data["caption"] = caption
        
        message_request = WhatsAppMessageSendRequest(
            to=to,
            type="video",
            video=video_data
        )
        
        return await self.send_message(message_request)
    
    async def send_document(
        self,
        to: str,
        document_url: Optional[str] = None,
        document_id: Optional[str] = None,
        filename: Optional[str] = None,
        caption: Optional[str] = None
    ) -> WhatsAppMessageSendResponse:
        """
        Envía un documento (PDF, Word, Excel, etc.).
        
        Args:
            to: Número de teléfono del destinatario
            document_url: URL pública del documento
            document_id: ID de documento previamente subido
            filename: Nombre del archivo
            caption: Caption opcional
            
        Returns:
            WhatsAppMessageSendResponse
        """
        if not document_url and not document_id:
            raise HTTPException(
                status_code=400,
                detail="Debes proporcionar document_url o document_id"
            )
        
        document_data = {}
        if document_url:
            document_data["link"] = document_url
        if document_id:
            document_data["id"] = document_id
        if filename:
            document_data["filename"] = filename
        if caption:
            document_data["caption"] = caption
        
        message_request = WhatsAppMessageSendRequest(
            to=to,
            type="document",
            document=document_data
        )
        
        return await self.send_message(message_request)
    
    async def send_audio(
        self,
        to: str,
        audio_url: Optional[str] = None,
        audio_id: Optional[str] = None
    ) -> WhatsAppMessageSendResponse:
        """
        Envía un archivo de audio.
        
        Args:
            to: Número de teléfono del destinatario
            audio_url: URL pública del audio
            audio_id: ID de audio previamente subido
            
        Returns:
            WhatsAppMessageSendResponse
        """
        if not audio_url and not audio_id:
            raise HTTPException(
                status_code=400,
                detail="Debes proporcionar audio_url o audio_id"
            )
        
        audio_data = {}
        if audio_url:
            audio_data["link"] = audio_url
        if audio_id:
            audio_data["id"] = audio_id
        
        message_request = WhatsAppMessageSendRequest(
            to=to,
            type="audio",
            audio=audio_data
        )
        
        return await self.send_message(message_request)
    
    async def send_location(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None
    ) -> WhatsAppMessageSendResponse:
        """
        Envía una ubicación.
        
        Args:
            to: Número de teléfono del destinatario
            latitude: Latitud
            longitude: Longitud
            name: Nombre del lugar
            address: Dirección
            
        Returns:
            WhatsAppMessageSendResponse
        """
        location_data = {
            "latitude": latitude,
            "longitude": longitude
        }
        if name:
            location_data["name"] = name
        if address:
            location_data["address"] = address
        
        message_request = WhatsAppMessageSendRequest(
            to=to,
            type="location",
            location=location_data
        )
        
        return await self.send_message(message_request)
    
    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "es",
        components: Optional[list] = None
    ) -> WhatsAppMessageSendResponse:
        """
        Envía un mensaje usando una plantilla aprobada.
        
        Args:
            to: Número de teléfono del destinatario
            template_name: Nombre de la plantilla aprobada
            language_code: Código de idioma (default: "es")
            components: Lista de componentes con parámetros
            
        Returns:
            WhatsAppMessageSendResponse
            
        Example:
            await whatsapp_service.send_template(
                to="5491112345678",
                template_name="hello_world",
                language_code="es"
            )
        """
        template_data = {
            "name": template_name,
            "language": {"code": language_code}
        }
        if components:
            template_data["components"] = components
        
        message_request = WhatsAppMessageSendRequest(
            to=to,
            type="template",
            template=template_data
        )
        
        return await self.send_message(message_request)
    
    async def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: list,
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None
    ) -> WhatsAppMessageSendResponse:
        """
        Envía un mensaje interactivo con botones (máximo 3 botones).
        
        Args:
            to: Número de teléfono del destinatario
            body_text: Texto principal del mensaje
            buttons: Lista de botones [{"id": "btn1", "title": "Opción 1"}, ...]
            header_text: Texto del header (opcional)
            footer_text: Texto del footer (opcional)
            
        Returns:
            WhatsAppMessageSendResponse
            
        Example:
            await whatsapp_service.send_interactive_buttons(
                to="5491112345678",
                body_text="¿Qué deseas hacer?",
                buttons=[
                    {"id": "btn1", "title": "Ver productos"},
                    {"id": "btn2", "title": "Contactar soporte"}
                ],
                footer_text="Selecciona una opción"
            )
        """
        if len(buttons) > 3:
            raise HTTPException(
                status_code=400,
                detail="WhatsApp permite máximo 3 botones por mensaje"
            )
        
        interactive_data = {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": btn["id"], "title": btn["title"]}
                    }
                    for btn in buttons
                ]
            }
        }
        
        if header_text:
            interactive_data["header"] = {"type": "text", "text": header_text}
        if footer_text:
            interactive_data["footer"] = {"text": footer_text}
        
        message_request = WhatsAppMessageSendRequest(
            to=to,
            type="interactive",
            interactive=interactive_data
        )
        
        return await self.send_message(message_request)
    
    async def get_media_url(self, media_id: str) -> str:
        """
        Obtiene la URL de descarga de un archivo de media.
        
        Args:
            media_id: ID del media en WhatsApp
            
        Returns:
            URL de descarga del media
            
        Raises:
            HTTPException: Si ocurre un error obteniendo la URL
        """
        self._check_configuration()
        
        url = f"https://graph.facebook.com/{self.api_version}/{media_id}"
        
        try:
            # Usar HTTPClient con headers de autorización
            http_client = HTTPClient(
                default_headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            )
            
            # Usar get_json para obtener la respuesta parseada directamente
            data = await http_client.get_json(url)
            
            media_url = data.get("url")
            
            if not media_url:
                raise HTTPException(
                    status_code=500,
                    detail="No se pudo obtener la URL del media"
                )
            
            return media_url
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error de red obteniendo URL de media: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error de red obteniendo URL de media: {str(e)}"
            )
    
    async def download_media(self, media_url: str) -> bytes:
        """
        Descarga el contenido de un archivo de media.
        
        Args:
            media_url: URL de descarga del media
            
        Returns:
            Contenido del archivo en bytes
            
        Raises:
            HTTPException: Si ocurre un error descargando el archivo
        """
        self._check_configuration()
        
        try:
            # Usar HTTPClient con headers de autorización
            http_client = HTTPClient(
                default_headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            )
            
            # Usar get_bytes para obtener el contenido directamente
            content = await http_client.get_bytes(media_url)
            
            return content
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error de red descargando media: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error de red descargando media: {str(e)}"
            )
    
    async def get_media_content(self, media_id: str) -> bytes:
        """
        Obtiene el contenido de un archivo de media.
        
        Este método combina get_media_url y download_media para simplificar
        la descarga de archivos de media en un solo paso.
        
        Args:
            media_id: ID del media en WhatsApp
            
        Returns:
            Contenido del archivo en bytes
            
        Raises:
            HTTPException: Si ocurre un error obteniendo o descargando el media
        """
        
        # Primero obtener la URL de descarga
        media_url = await self.get_media_url(media_id)
        
        # Luego descargar el contenido
        content = await self.download_media(media_url)
        
        return content
    
    async def mark_message_as_read(self, message_id: str) -> bool:
        """
        Marca un mensaje como leído (doble check azul en WhatsApp).
        
        Args:
            message_id: ID del mensaje a marcar como leído
            
        Returns:
            bool: True si se marcó exitosamente, False en caso contrario
            
        Example:
            await whatsapp_service.mark_message_as_read("wamid.XXX...")
        """
        try:
            
            message_data = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            response = await self._make_request("POST", "messages", data=message_data)
            
            if response.get("success"):
                return True
            else:
                logger.warning(f"⚠️ No se pudo marcar mensaje como leído: {response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error marcando mensaje como leído: {str(e)}")
            return False
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado del servicio de WhatsApp.
        
        Returns:
            Dict con el estado y configuración del servicio
        """
        return {
            "service": "WhatsApp Business API",
            "configured": self.is_configured,
            "api_version": self.api_version,
            "phone_number_id_set": bool(self.phone_number_id),
            "access_token_set": bool(self.access_token),
            "base_url": self.base_url,
            "supported_message_types": [
                "text",
                "image",
                "video",
                "document",
                "audio",
                "location",
                "contacts",
                "template",
                "interactive"
            ]
        }
    
    # ============== MÉTODOS DE AUTENTICACIÓN DE WHATSAPP ==============
    
    async def create_auth_token(self, phone_number: str, bot_phone_number: Optional[str] = None, expires_in_seconds: int = 300) -> str:
        """
        Crea un token único para autenticación de WhatsApp.
        
        Args:
            phone_number: Número de teléfono del usuario
            bot_phone_number: Número de teléfono del bot (opcional)
            expires_in_seconds: Tiempo de expiración en segundos (default: 5 minutos)
            
        Returns:
            Token único generado
        """
        # Inicializar Redis si no está conectado
        if not redis_client.is_connected:
            await redis_client.initialize()
        
        token = secrets.token_urlsafe(32)
        
        key = f"whatsapp_auth_token:{token}"
        data = {
            "phone_number": phone_number,
            "bot_phone_number": bot_phone_number,
            "created_at": datetime.now().isoformat(),
            "expires_in": expires_in_seconds
        }
        
        await redis_client.set(key, data, expires_in_seconds=expires_in_seconds)
        
        logger.info(f"🔑 Token de autenticación creado para {phone_number}: {token[:10]}...")
        return token
    
    async def get_phone_from_auth_token(self, token: str) -> Optional[tuple[str, Optional[str]]]:
        """
        Obtiene el número de teléfono y número del bot asociados a un token de autenticación.
        
        Args:
            token: Token de autenticación
            
        Returns:
            Tupla (phone_number, bot_phone_number) si el token es válido, None si no existe o expiró
        """
        # Inicializar Redis si no está conectado
        if not redis_client.is_connected:
            await redis_client.initialize()
        
        key = f"whatsapp_auth_token:{token}"
        data = await redis_client.get(key)
        
        if not data:
            logger.warning(f"⚠️  Token no encontrado o expirado: {token[:10]}...")
            return None
        
        phone_number = data.get("phone_number")
        bot_phone_number = data.get("bot_phone_number")
        logger.info(f"✅ Token válido para {phone_number}")
        return (phone_number, bot_phone_number)
    
    async def delete_auth_token(self, token: str) -> bool:
        """
        Elimina un token de autenticación (consumido o cancelado).
        
        Args:
            token: Token a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        # Inicializar Redis si no está conectado
        if not redis_client.is_connected:
            await redis_client.initialize()
        
        key = f"whatsapp_auth_token:{token}"
        result = await redis_client.delete(key)
        
        if result:
            logger.info(f"🗑️  Token eliminado: {token[:10]}...")
        
        return result
    
    async def save_whatsapp_auth(
        self,
        phone_number: str,
        user_data: Dict[str, Any],
        expires_in_seconds: int = 86400  # 24 horas por defecto
    ) -> bool:
        """
        Guarda la autenticación de un usuario de WhatsApp usando el servicio unificado.
        
        Args:
            phone_number: Número de teléfono del usuario
            user_data: Datos del usuario autenticado (codeLogin, email, name, etc.)
            expires_in_seconds: Tiempo de expiración (default: 24 horas)
            
        Returns:
            True si se guardó exitosamente
        """
        from app.services.auth_service import auth_service
        
        return await auth_service.save_session(
            user_id=phone_number,
            user_data=user_data,
            session_type="whatsapp",
            expires_in_seconds=expires_in_seconds
        )
    
    async def get_whatsapp_auth(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de autenticación de un usuario de WhatsApp.
        
        Args:
            phone_number: Número de teléfono del usuario
            
        Returns:
            Datos del usuario si está autenticado, None si no está autenticado o expiró
        """
        from app.services.auth_service import auth_service
        
        return await auth_service.get_session(
            user_id=phone_number,
            session_type="whatsapp"
        )
    
    async def is_whatsapp_authenticated(self, phone_number: str) -> bool:
        """
        Verifica si un usuario de WhatsApp está autenticado.
        
        Args:
            phone_number: Número de teléfono del usuario
            
        Returns:
            True si está autenticado, False si no
        """
        from app.services.auth_service import auth_service
        
        return await auth_service.is_authenticated(
            user_id=phone_number,
            session_type="whatsapp"
        )
    
    async def delete_whatsapp_auth(self, phone_number: str) -> bool:
        """
        Elimina la autenticación de un usuario de WhatsApp (logout).
        
        Args:
            phone_number: Número de teléfono del usuario
            
        Returns:
            True si se eliminó, False si no existía
        """
        from app.services.auth_service import auth_service
        
        return await auth_service.delete_session(
            user_id=phone_number,
            session_type="whatsapp"
        )
    
    async def extend_whatsapp_auth(
        self,
        phone_number: str,
        expires_in_seconds: int = 86400  # 24 horas
    ) -> bool:
        """
        Extiende el tiempo de autenticación de un usuario de WhatsApp.
        
        Args:
            phone_number: Número de teléfono del usuario
            expires_in_seconds: Nuevo tiempo de expiración
            
        Returns:
            True si se extendió exitosamente, False si no estaba autenticado
        """
        from app.services.auth_service import auth_service
        
        return await auth_service.extend_session(
            user_id=phone_number,
            session_type="whatsapp",
            expires_in_seconds=expires_in_seconds
        )


# Instancia global del servicio de WhatsApp
whatsapp_service = WhatsAppService()
