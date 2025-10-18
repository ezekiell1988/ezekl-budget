"""
Servicio de IA para WhatsApp usando Azure OpenAI.
Proporciona respuestas inteligentes automáticas a mensajes de WhatsApp.
"""

import logging
from typing import Optional, Dict, List
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
        
    @property
    def client(self) -> AsyncAzureOpenAI:
        """Cliente de Azure OpenAI con lazy loading."""
        if self._client is None:
            from app.core.config import settings
            self._client = AsyncAzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint
            )
            logger.info("✅ Cliente de Azure OpenAI inicializado para WhatsApp")
            logger.info(f"🔧 API Version: {settings.azure_openai_api_version}")
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
        contact_name: Optional[str] = None
    ) -> str:
        """
        Genera una respuesta inteligente usando Azure OpenAI.
        
        Args:
            user_message: Mensaje del usuario
            phone_number: Número de teléfono del usuario
            contact_name: Nombre del contacto (opcional)
            
        Returns:
            Respuesta generada por la IA
            
        Raises:
            Exception: Si ocurre un error generando la respuesta
        """
        try:
            # Agregar mensaje del usuario al historial
            self._add_to_history(phone_number, "user", user_message)
            
            # Construir mensajes para la API
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Agregar el historial de conversación
            messages.extend(self._get_conversation_history(phone_number))
            
            logger.info(f"🤖 Generando respuesta de IA para {contact_name or phone_number}")
            logger.debug(f"📝 Mensaje del usuario: {user_message}")
            
            # Obtener el deployment name de la configuración
            from app.core.config import settings
            deployment_name = settings.azure_openai_chat_deployment_name
            
            logger.debug(f"🔧 Usando deployment: {deployment_name}")
            
            # Llamar a Azure OpenAI
            # Nota: GPT-5 tiene restricciones en parámetros (temperature debe ser 1.0, no soporta frequency/presence penalty)
            response = await self.client.chat.completions.create(
                model=deployment_name,  # Usar el deployment de chat configurado en .env
                messages=messages,
                max_completion_tokens=self.max_response_tokens,  # GPT-5 usa max_completion_tokens
                # temperature, top_p, frequency_penalty, presence_penalty no soportados en GPT-5
            )
            
            # Extraer la respuesta
            ai_response = response.choices[0].message.content.strip()
            
            # Validar que la respuesta no esté vacía
            if not ai_response:
                logger.warning(f"⚠️ Respuesta de IA vacía, usando mensaje por defecto")
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
        contact_name: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Procesa un mensaje y envía una respuesta automática por WhatsApp.
        
        Args:
            user_message: Mensaje del usuario
            phone_number: Número de teléfono del usuario
            contact_name: Nombre del contacto (opcional)
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Generar respuesta de IA
            ai_response = await self.generate_response(
                user_message=user_message,
                phone_number=phone_number,
                contact_name=contact_name
            )
            
            # Enviar respuesta por WhatsApp
            logger.info(f"📤 Enviando respuesta de IA a {contact_name or phone_number}")
            
            whatsapp_response = await whatsapp_service.send_text_message(
                to=phone_number,
                body=ai_response
            )
            
            logger.info(f"✅ Respuesta de IA enviada exitosamente")
            
            return {
                "success": True,
                "ai_response": ai_response,
                "whatsapp_message_id": whatsapp_response.messages[0]['id'] if whatsapp_response.messages else None
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
