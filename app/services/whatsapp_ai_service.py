"""
Servicio de IA para WhatsApp usando Azure OpenAI.
Proporciona respuestas inteligentes automáticas a mensajes de WhatsApp.
Soporta procesamiento multimodal: texto, imágenes y audios.
"""

import logging
import base64
from typing import Optional, Dict, List, Tuple
from openai import AsyncAzureOpenAI

from app.core.config import settings
from app.services.whatsapp_service import whatsapp_service

logger = logging.getLogger(__name__)


class WhatsAppAIService:
    """
    Servicio para generar respuestas automáticas de IA a mensajes de WhatsApp.
    
    Utiliza Azure OpenAI para generar respuestas contextuales e inteligentes
    basadas en el historial de conversación y el contexto del negocio.
    """
    
    def __init__(self):
        """Inicializa el servicio de IA para WhatsApp."""
        self._client: Optional[AsyncAzureOpenAI] = None
        self._conversation_history: Dict[str, List[Dict[str, str]]] = {}
        
        # Configuración del sistema
        self.system_prompt = """Eres un asistente virtual de Ezekl Budget, una aplicación de gestión financiera y presupuestos.

Tu función es:
- Responder consultas sobre la aplicación y sus funcionalidades
- Ayudar con dudas sobre presupuestos, cuentas y finanzas personales
- Proporcionar información de contacto y soporte
- Ser amable, profesional y conciso en tus respuestas

Características de tus respuestas:
- Máximo 500 caracteres (WhatsApp tiene límites)
- Usa emojis ocasionalmente para hacer la conversación más amigable
- Si no sabes algo, sé honesto y ofrece contactar con soporte humano
- Mantén un tono profesional pero cercano

Información importante:
- Sitio web: https://ezeklbudget.com
- Email de soporte: soporte@ezeklbudget.com
- Horario de atención: Lunes a Viernes 9:00 AM - 6:00 PM"""

        self.max_history_messages = 10  # Máximo de mensajes a recordar por conversación
        self.max_response_tokens = 500  # Tokens máximos para respuesta (GPT-5 necesita más margen)
    
    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """
        Codifica una imagen en base64 para enviarla a OpenAI.
        
        Args:
            image_bytes: Contenido de la imagen en bytes
            
        Returns:
            Imagen codificada en base64
        """
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _encode_audio_to_base64(self, audio_bytes: bytes) -> str:
        """
        Codifica un audio en base64 para enviarla a OpenAI.
        
        Args:
            audio_bytes: Contenido del audio en bytes
            
        Returns:
            Audio codificado en base64
        """
        return base64.b64encode(audio_bytes).decode('utf-8')
        
    @property
    def client(self) -> AsyncAzureOpenAI:
        """Cliente de Azure OpenAI con lazy loading y timeout configurado."""
        if self._client is None:
            from app.core.config import settings
            import httpx
            
            # AsyncAzureOpenAI requiere un httpx.AsyncClient específicamente
            # No podemos usar nuestro HTTPClient (basado en aiohttp) directamente
            # Pero configuramos timeout extendido (60 segundos para multimodal)
            http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0)
            )
            
            self._client = AsyncAzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint,
                http_client=http_client  # Cliente HTTP custom con timeout aumentado
            )
            logger.info("✅ Cliente de Azure OpenAI inicializado para WhatsApp")
            logger.info(f"🔧 API Version: {settings.azure_openai_api_version}")
            logger.info(f"⏱️  Timeout configurado: 60s (connect: 10s)")
            logger.info(f"🚀 Deployment: {settings.azure_openai_chat_deployment_name}")
        return self._client
    
    def _get_conversation_history(self, phone_number: str) -> List[Dict[str, str]]:
        """
        Obtiene el historial de conversación para un número de teléfono.
        
        Args:
            phone_number: Número de teléfono del usuario
            
        Returns:
            Lista de mensajes del historial
        """
        if phone_number not in self._conversation_history:
            self._conversation_history[phone_number] = []
        return self._conversation_history[phone_number]
    
    def _add_to_history(
        self,
        phone_number: str,
        role: str,
        content: str
    ):
        """
        Agrega un mensaje al historial de conversación.
        
        Args:
            phone_number: Número de teléfono del usuario
            role: Rol del mensaje ('user' o 'assistant')
            content: Contenido del mensaje
        """
        history = self._get_conversation_history(phone_number)
        history.append({"role": role, "content": content})
        
        # Limitar el historial al máximo configurado
        if len(history) > self.max_history_messages:
            # Mantener el mensaje del sistema y eliminar los más antiguos
            self._conversation_history[phone_number] = history[-self.max_history_messages:]
    
    def clear_history(self, phone_number: str):
        """
        Limpia el historial de conversación de un usuario.
        
        Args:
            phone_number: Número de teléfono del usuario
        """
        if phone_number in self._conversation_history:
            del self._conversation_history[phone_number]
            logger.info(f"🗑️ Historial limpiado para {phone_number}")
    
    async def generate_response(
        self,
        user_message: str,
        phone_number: str,
        contact_name: Optional[str] = None,
        image_data: Optional[bytes] = None,
        audio_data: Optional[bytes] = None,
        media_type: Optional[str] = None
    ) -> str:
        """
        Genera una respuesta inteligente usando Azure OpenAI.
        Soporta procesamiento multimodal: texto, imágenes y audios.
        
        Args:
            user_message: Mensaje de texto del usuario (puede ser caption o texto solo)
            phone_number: Número de teléfono del usuario
            contact_name: Nombre del contacto (opcional)
            image_data: Datos de imagen en bytes (opcional)
            audio_data: Datos de audio en bytes (opcional)
            media_type: Tipo MIME del media (opcional, ej: 'image/jpeg', 'audio/ogg')
            
        Returns:
            Respuesta generada por la IA
            
        Raises:
            Exception: Si ocurre un error generando la respuesta
        """
        try:
            # Construir el contenido del mensaje del usuario
            user_content = []
            
            # Si hay imagen, agregarla al contenido
            if image_data:
                logger.info(f"🖼️ Procesando imagen ({len(image_data)} bytes)")
                image_base64 = self._encode_image_to_base64(image_data)
                
                # Determinar el formato de la imagen
                image_format = "jpeg"  # default
                if media_type:
                    if "png" in media_type.lower():
                        image_format = "png"
                    elif "webp" in media_type.lower():
                        image_format = "webp"
                
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{image_format};base64,{image_base64}",
                        "detail": "low"  # Reduce consumo de tokens: "low" | "high" | "auto"
                        # "low" usa ~85 tokens por imagen, suficiente para WhatsApp
                    }
                })
            
            # Si hay audio, agregarla al contenido
            if audio_data:
                logger.info(f"🎤 Procesando audio ({len(audio_data)} bytes)")
                audio_base64 = self._encode_audio_to_base64(audio_data)
                
                # Determinar el formato del audio
                audio_format = "ogg"  # default para WhatsApp voice messages
                if media_type:
                    if "mp3" in media_type.lower():
                        audio_format = "mp3"
                    elif "wav" in media_type.lower():
                        audio_format = "wav"
                    elif "m4a" in media_type.lower():
                        audio_format = "m4a"
                
                user_content.append({
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_base64,
                        "format": audio_format
                    }
                })
            
            # Siempre agregar el texto (puede ser el mensaje principal o un caption)
            if user_message:
                user_content.append({
                    "type": "text",
                    "text": user_message
                })
            elif not image_data and not audio_data:
                # Si no hay mensaje ni media, usar un texto por defecto
                user_content.append({
                    "type": "text",
                    "text": "Hola"
                })
            
            # Si user_content tiene un solo elemento de texto, simplificarlo
            if len(user_content) == 1 and user_content[0]["type"] == "text":
                user_message_content = user_content[0]["text"]
            else:
                user_message_content = user_content
            
            # Agregar mensaje del usuario al historial
            self._add_to_history(phone_number, "user", user_message or "[Mensaje multimedia]")
            
            # Construir mensajes para la API
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Agregar el historial de conversación (solo texto)
            history = self._get_conversation_history(phone_number)
            for hist_msg in history[:-1]:  # Excluir el último que acabamos de agregar
                messages.append({
                    "role": hist_msg["role"],
                    "content": hist_msg["content"]
                })
            
            # Agregar el mensaje actual (puede ser multimodal)
            messages.append({
                "role": "user",
                "content": user_message_content
            })
            
            media_info = []
            if image_data:
                media_info.append("imagen")
            if audio_data:
                media_info.append("audio")
            media_str = f" con {' y '.join(media_info)}" if media_info else ""
            
            logger.info(f"🤖 Generando respuesta de IA para {contact_name or phone_number}{media_str}")
            logger.debug(f"📝 Mensaje del usuario: {user_message or '[multimedia]'}")
            
            # Obtener el deployment name de la configuración
            from app.core.config import settings
            deployment_name = settings.azure_openai_chat_deployment_name
            
            logger.debug(f"🔧 Usando deployment: {deployment_name}")
            
            # Llamar a Azure OpenAI
            # Nota: GPT-5 (o1 reasoning model) requiere max_completion_tokens alto
            # Los tokens se dividen entre reasoning_tokens (internos) y completion_tokens (respuesta visible)
            # Con 500 tokens, el modelo usa todo para reasoning y devuelve contenido vacío
            response = await self.client.chat.completions.create(
                model=deployment_name,  # Usar el deployment de chat configurado en .env
                messages=messages,
                max_completion_tokens=8000,  # Aumentado significativamente para modelos o1/GPT-5
                # GPT-5/o1 necesita espacio para reasoning_tokens + completion_tokens
                # temperature, top_p, frequency_penalty, presence_penalty no soportados en GPT-5/o1
            )
            
            # Log de la respuesta completa para debugging
            logger.debug(f"🔍 Respuesta completa de API: {response}")
            logger.debug(f"🔍 Choices: {response.choices}")
            logger.debug(f"🔍 Primer choice: {response.choices[0] if response.choices else 'Sin choices'}")
            
            # Log de uso de tokens (importante para modelos o1/GPT-5 con reasoning)
            if hasattr(response, 'usage'):
                usage = response.usage
                logger.info(f"📊 Token usage - Prompt: {usage.prompt_tokens}, "
                          f"Completion: {usage.completion_tokens}, "
                          f"Total: {usage.total_tokens}")
                
                # Mostrar reasoning tokens si están disponibles (GPT-5/o1)
                if hasattr(usage, 'completion_tokens_details'):
                    details = usage.completion_tokens_details
                    if hasattr(details, 'reasoning_tokens'):
                        logger.info(f"🧠 Reasoning tokens: {details.reasoning_tokens}")
                        logger.info(f"📝 Visible tokens: {usage.completion_tokens - details.reasoning_tokens}")

            
            # Extraer la respuesta
            if not response.choices or len(response.choices) == 0:
                logger.warning(f"⚠️ No hay choices en la respuesta de IA")
                ai_response = ""
            else:
                message_content = response.choices[0].message.content
                logger.debug(f"🔍 Content crudo: '{message_content}' (tipo: {type(message_content)})")
                ai_response = message_content.strip() if message_content else ""
            
            # Validar que la respuesta no esté vacía
            if not ai_response:
                logger.warning(f"⚠️ Respuesta de IA vacía, usando mensaje por defecto")
                logger.warning(f"🔍 Finish reason: {response.choices[0].finish_reason if response.choices else 'N/A'}")
                ai_response = "¡Hola! 👋 Gracias por contactarnos. ¿En qué puedo ayudarte con Ezekl Budget?"
            
            # Agregar respuesta al historial
            self._add_to_history(phone_number, "assistant", ai_response)
            
            logger.info(f"✅ Respuesta generada exitosamente")
            logger.debug(f"💬 Respuesta: {ai_response}")
            
            return ai_response
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"❌ Error generando respuesta de IA: {error_message}", exc_info=True)
            logger.error(f"🔍 Tipo de error: {type(e).__name__}")
            
            # Log adicional para errores comunes
            if "deployment" in error_message.lower() or "model" in error_message.lower():
                logger.error(f"⚠️  PROBLEMA DE DEPLOYMENT: El deployment '{settings.azure_openai_deployment_name}' "
                           f"puede no estar disponible o no ser compatible con Chat Completions")
                logger.error(f"💡 SOLUCIÓN: Verifica que tengas un deployment de GPT-4 o GPT-3.5-Turbo en Azure OpenAI")
            
            # Respuesta de fallback en caso de error
            fallback_response = (
                "Disculpa, estoy teniendo problemas técnicos 😅. "
                "Por favor contacta a nuestro equipo de soporte en soporte@ezeklbudget.com"
            )
            return fallback_response
    
    async def process_and_reply(
        self,
        user_message: str,
        phone_number: str,
        contact_name: Optional[str] = None,
        image_data: Optional[bytes] = None,
        audio_data: Optional[bytes] = None,
        media_type: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Procesa un mensaje (texto, imagen o audio) y envía una respuesta automática por WhatsApp.
        
        Args:
            user_message: Mensaje de texto del usuario (puede ser caption)
            phone_number: Número de teléfono del usuario
            contact_name: Nombre del contacto (opcional)
            image_data: Datos de imagen en bytes (opcional)
            audio_data: Datos de audio en bytes (opcional)
            media_type: Tipo MIME del media (opcional)
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Generar respuesta de IA (puede procesar texto, imagen o audio)
            ai_response = await self.generate_response(
                user_message=user_message,
                phone_number=phone_number,
                contact_name=contact_name,
                image_data=image_data,
                audio_data=audio_data,
                media_type=media_type
            )
            
            # Enviar respuesta por WhatsApp
            media_info = []
            if image_data:
                media_info.append("imagen")
            if audio_data:
                media_info.append("audio")
            media_str = f" ({' y '.join(media_info)})" if media_info else ""
            
            logger.info(f"📤 Enviando respuesta de IA a {contact_name or phone_number}{media_str}")
            
            whatsapp_response = await whatsapp_service.send_text_message(
                to=phone_number,
                body=ai_response
            )
            
            logger.info(f"✅ Respuesta de IA enviada exitosamente")
            
            return {
                "success": True,
                "ai_response": ai_response,
                "whatsapp_message_id": whatsapp_response.messages[0]['id'] if whatsapp_response.messages else None,
                "processed_media": {
                    "has_image": bool(image_data),
                    "has_audio": bool(audio_data)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando y respondiendo mensaje: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Obtiene estadísticas del servicio de IA.
        
        Returns:
            Dict con estadísticas
        """
        return {
            "active_conversations": len(self._conversation_history),
            "total_messages": sum(len(history) for history in self._conversation_history.values()),
            "max_history_per_conversation": self.max_history_messages
        }


# Instancia global del servicio
whatsapp_ai_service = WhatsAppAIService()
