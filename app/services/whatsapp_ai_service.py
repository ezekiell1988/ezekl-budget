"""
Servicio de IA para WhatsApp usando Azure OpenAI.
Proporciona respuestas inteligentes automáticas a mensajes de WhatsApp.
Soporta procesamiento multimodal: texto, imágenes, audios y PDFs.
"""

import base64
import logging
from typing import Optional, Dict, List
from openai import AsyncAzureOpenAI

from app.core.config import settings
from app.core.http_request import HTTPClient
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
    
    async def _transcribe_audio(self, audio_bytes: bytes, source_format: str = "ogg") -> Optional[str]:
        """
        Transcribe audio a texto usando Azure OpenAI Audio Transcription API (gpt-4o-transcribe).
        Usa HTTPClient.post_multipart para enviar audio en formato multipart/form-data.
        
        Args:
            audio_bytes: Audio en bytes (puede ser OGG, WAV, MP3, etc.)
            source_format: Formato del audio (ogg, wav, mp3, etc.)
            
        Returns:
            Texto transcrito o None si falla
        """
        try:
            
            # Construir la URL de la API de transcripción
            # Formato: {endpoint}/openai/deployments/{deployment}/audio/transcriptions?api-version={version}
            url = (
                f"{settings.azure_openai_endpoint.rstrip('/')}/openai/deployments/"
                f"{settings.azure_openai_audio_deployment_name}/audio/transcriptions"
                f"?api-version={settings.azure_openai_audio_api_version}"
            )
            
            # Headers para la petición
            headers = {
                "api-key": settings.azure_openai_api_key,
            }
            
            
            # Preparar archivo y campos para multipart/form-data
            files = {
                'file': (f'audio.{source_format}', audio_bytes, f'audio/{source_format}')
            }
            fields = {
                'model': settings.azure_openai_audio_deployment_name,
                'response_format': 'text'
            }
            
            # Crear cliente HTTP con timeout de 60 segundos
            http_client = HTTPClient(timeout=60)
            
            # Hacer la petición POST multipart usando HTTPClient
            response = await http_client.post_multipart(
                url,
                files=files,
                fields=fields,
                headers=headers
            )
            
            # Log del status
            
            if response.status == 200:
                # La respuesta es texto plano con la transcripción
                transcription = await response.text()
                transcription = transcription.strip()
                
                if transcription:
                    return transcription
                else:
                    logger.warning("⚠️ Transcripción vacía recibida")
                    return None
            else:
                # Log del error
                error_text = await response.text()
                logger.error(f"❌ Error en transcripción {response.status}: {error_text}")
                return None
                    
        except Exception as e:
            logger.error(f"❌ Error transcribiendo audio: {str(e)}", exc_info=True)
            return None
        
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
    
    async def generate_response(
        self,
        user_message: str,
        phone_number: str,
        contact_name: Optional[str] = None,
        image_data: Optional[bytes] = None,
        audio_data: Optional[bytes] = None,
        pdf_data: Optional[bytes] = None,
        media_type: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Genera una respuesta inteligente usando Azure OpenAI.
        Soporta procesamiento multimodal: texto, imágenes, audios y PDFs.
        
        Args:
            user_message: Mensaje de texto del usuario (puede ser caption o texto solo)
            phone_number: Número de teléfono del usuario
            contact_name: Nombre del contacto (opcional)
            image_data: Datos de imagen en bytes (opcional)
            audio_data: Datos de audio en bytes (opcional)
            pdf_data: Datos de PDF en bytes (opcional)
            media_type: Tipo MIME del media (opcional, ej: 'image/jpeg', 'audio/ogg')
            filename: Nombre del archivo (para PDFs)
            
        Returns:
            Respuesta generada por la IA
            
        Raises:
            Exception: Si ocurre un error generando la respuesta
        """
        try:
            # Construir el contenido del mensaje del usuario
            user_content = []
            
            # Si hay PDF, codificarlo en base64 y enviarlo directamente al modelo
            if pdf_data:
                logger.info(f"📄 Procesando PDF: {filename or 'documento.pdf'} ({len(pdf_data)} bytes)")
                pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
                pdf_filename = filename or "documento.pdf"
                
                # Agregar el PDF como contenido (similar a una imagen)
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:application/pdf;base64,{pdf_base64}"
                    }
                })
                
                # Agregar el texto del usuario si existe
                if user_message:
                    user_content.append({
                        "type": "text",
                        "text": user_message
                    })
                else:
                    # Si no hay mensaje, pedir al modelo que analice el PDF
                    user_content.append({
                        "type": "text",
                        "text": f"Analiza este documento PDF '{pdf_filename}' y proporciona un resumen breve de su contenido."
                    })
            
            # Si hay imagen, agregarla al contenido
            if image_data:
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
            
            # Si hay audio, transcribirlo y reemplazar/complementar el user_message
            # La transcripción se trata como si fuera el mensaje original del usuario
            # (sin prefijos como "[Audio transcrito]:" para que GPT-5 lo procese naturalmente)
            if audio_data:
                
                # Determinar el formato del audio original
                source_format = "ogg"  # default para WhatsApp voice messages
                if media_type:
                    if "mp3" in media_type.lower():
                        source_format = "mp3"
                    elif "wav" in media_type.lower():
                        source_format = "wav"
                    elif "m4a" in media_type.lower():
                        source_format = "m4a"
                    elif "ogg" in media_type.lower() or "opus" in media_type.lower():
                        source_format = "ogg"
                
                # Transcribir directamente con Azure OpenAI (acepta OGG y otros formatos)
                transcription = await self._transcribe_audio(audio_data, source_format)
                
                if transcription:
                    # Usar la transcripción directamente como el mensaje del usuario
                    # Sin prefijos ni indicadores - GPT-5 lo procesa como texto normal
                    if user_message:
                        # Si ya hay mensaje de texto (caption), combinarlo con la transcripción
                        user_message = f"{user_message}\n\n{transcription}"
                    else:
                        # Si solo hay audio, usar la transcripción directamente
                        user_message = transcription
                else:
                    logger.warning("⚠️ No se pudo transcribir el audio")
                    if not user_message:
                        # Solo si falla la transcripción y no hay texto alternativo
                        user_message = "No pude procesar el audio. ¿Podrías escribirme tu mensaje?"
            
            # Siempre agregar el texto (puede ser el mensaje principal o un caption)
            # EXCEPTO si ya se agregó como parte del PDF o imagen
            if user_message and not pdf_data and not image_data:
                user_content.append({
                    "type": "text",
                    "text": user_message
                })
            elif not user_content:
                # Si no hay contenido en absoluto, usar un texto por defecto
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
            
            
            # Obtener el deployment name de la configuración
            from app.core.config import settings
            deployment_name = settings.azure_openai_chat_deployment_name
            
            
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
            
            # Log de uso de tokens (importante para modelos o1/GPT-5 con reasoning)
            if hasattr(response, 'usage'):
                usage = response.usage
                
                # Mostrar reasoning tokens si están disponibles (GPT-5/o1)
                if hasattr(usage, 'completion_tokens_details'):
                    details = usage.completion_tokens_details
                    if hasattr(details, 'reasoning_tokens'):
                        pass  # Logger eliminado

            
            # Extraer la respuesta
            if not response.choices or len(response.choices) == 0:
                logger.warning(f"⚠️ No hay choices en la respuesta de IA")
                ai_response = ""
            else:
                message_content = response.choices[0].message.content
                ai_response = message_content.strip() if message_content else ""
            
            # Validar que la respuesta no esté vacía
            if not ai_response:
                logger.warning(f"⚠️ Respuesta de IA vacía, usando mensaje por defecto")
                logger.warning(f"🔍 Finish reason: {response.choices[0].finish_reason if response.choices else 'N/A'}")
                ai_response = "¡Hola! 👋 Gracias por contactarnos. ¿En qué puedo ayudarte con Ezekl Budget?"
            
            # Agregar respuesta al historial
            self._add_to_history(phone_number, "assistant", ai_response)
            
            
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
        pdf_data: Optional[bytes] = None,
        media_type: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Procesa un mensaje (texto, imagen, audio o PDF) y envía una respuesta automática por WhatsApp.
        
        Args:
            user_message: Mensaje de texto del usuario (puede ser caption)
            phone_number: Número de teléfono del usuario
            contact_name: Nombre del contacto (opcional)
            image_data: Datos de imagen en bytes (opcional)
            audio_data: Datos de audio en bytes (opcional)
            pdf_data: Datos de PDF en bytes (opcional)
            media_type: Tipo MIME del media (opcional)
            filename: Nombre del archivo (para PDFs)
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Generar respuesta de IA (puede procesar texto, imagen, audio o PDF)
            ai_response = await self.generate_response(
                user_message=user_message,
                phone_number=phone_number,
                contact_name=contact_name,
                image_data=image_data,
                audio_data=audio_data,
                pdf_data=pdf_data,
                media_type=media_type,
                filename=filename
            )
            
            # Enviar respuesta por WhatsApp
            media_info = []
            if image_data:
                media_info.append("imagen")
            if audio_data:
                media_info.append("audio")
            if pdf_data:
                media_info.append(f"PDF ({filename or 'documento.pdf'})")
            media_str = f" ({' y '.join(media_info)})" if media_info else ""
            
            
            whatsapp_response = await whatsapp_service.send_text_message(
                to=phone_number,
                body=ai_response
            )
            
            
            return {
                "success": True,
                "ai_response": ai_response,
                "whatsapp_message_id": whatsapp_response.messages[0]['id'] if whatsapp_response.messages else None,
                "processed_media": {
                    "has_image": bool(image_data),
                    "has_audio": bool(audio_data),
                    "has_pdf": bool(pdf_data)
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
