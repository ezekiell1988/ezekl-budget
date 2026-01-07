"""
Endpoints para el servicio de IA.
Proporciona endpoints REST para interactuar con el servicio de IA multimodal.
"""

import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from typing import Optional, Union, Annotated

from app.models.ai import ChatRequest, ChatResponse
from app.services.ai_service import ai_service

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de IA
router = APIRouter(prefix="/ai", tags=["IA"])


# ============== ENDPOINTS DE IA ==============


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat con IA (texto simple)",
    description="""Genera una respuesta de IA basada en un mensaje de texto.
    
    ✅ **Endpoint público - No requiere autenticación.**
    
    Este endpoint procesa mensajes de texto simples y genera respuestas inteligentes
    usando Azure OpenAI. Mantiene el historial de conversación por usuario.
    
    **Características:**
    - Procesamiento de texto simple
    - Historial de conversación por usuario
    - Respuestas contextuales basadas en el negocio
    
    **Parámetros:**
    - `message`: Mensaje de texto del usuario
    - `user_id`: Identificador único del usuario (puede ser email, ID, teléfono, etc.)
    - `user_name`: Nombre del usuario (opcional)
    """,
    responses={
        200: {
            "description": "Respuesta generada exitosamente",
            "model": ChatResponse,
        },
        500: {"description": "Error del servidor o de la IA"},
    },
)
async def chat_text(
    request: ChatRequest,
):
    """Procesa un mensaje de texto y genera una respuesta de IA."""
    try:
        response = await ai_service.generate_response(
            user_message=request.message,
            phone_number=request.user_id,
            contact_name=request.user_name,
        )
        
        return ChatResponse(
            success=True,
            response=response,
            user_id=request.user_id,
            user_name=request.user_name,
            processed_media={"has_image": False, "has_audio": False},
        )
    except Exception as e:
        logger.error(f"Error procesando chat de texto: {str(e)}", exc_info=True)
        return ChatResponse(
            success=False,
            response="",
            user_id=request.user_id,
            user_name=request.user_name,
            processed_media={"has_image": False, "has_audio": False},
            error=str(e),
        )


@router.post(
    "/chat/multimodal",
    response_model=ChatResponse,
    summary="Chat con IA (multimodal)",
    description="""Genera una respuesta de IA con soporte multimodal: texto, imagen y/o audio.
    
    ✅ **Endpoint público - No requiere autenticación.**
    
    Este endpoint procesa mensajes que pueden incluir:
    - Texto simple
    - Imagen (JPEG, PNG, WebP)
    - Audio (OGG, MP3, WAV, M4A)
    - Combinaciones de texto + imagen o texto + audio
    
    **Características:**
    - Procesamiento de imágenes con análisis visual
    - Transcripción de audios a texto (usando Whisper de Azure OpenAI)
    - Historial de conversación por usuario
    - Respuestas contextuales basadas en multimedia
    
    **Parámetros:**
    - `message`: Mensaje de texto del usuario (opcional si hay imagen o audio)
    - `user_id`: Identificador único del usuario
    - `user_name`: Nombre del usuario (opcional)
    - `image`: Archivo de imagen (opcional)
    - `audio`: Archivo de audio (opcional)
    
    **Formatos soportados:**
    - Imagen: JPEG, PNG, WebP (máx. 5MB)
    - Audio: OGG, MP3, WAV, M4A (máx. 25MB)
    
    **Nota:** Puedes enviar texto + imagen o texto + audio, pero no imagen + audio simultáneamente.
    """,
    responses={
        200: {
            "description": "Respuesta generada exitosamente",
            "model": ChatResponse,
        },
        400: {"description": "Request inválido - Parámetros incorrectos"},
        500: {"description": "Error del servidor o de la IA"},
    },
)
async def chat_multimodal(
    user_id: Annotated[str, Form()],
    message: Annotated[str, Form()] = "",
    user_name: Annotated[str, Form()] = "",
    image: Annotated[Union[UploadFile, str, None], File()] = None,
    audio: Annotated[Union[UploadFile, str, None], File()] = None,
):
    """Procesa un mensaje multimodal (texto, imagen y/o audio) y genera una respuesta de IA."""
    try:
        image_data = None
        audio_data = None
        media_type = None
        
        # Convertir strings vacíos a None
        message = message if message and message.strip() else None
        user_name = user_name if user_name and user_name.strip() else None
        
        # Convertir strings vacíos en archivos a None
        if isinstance(image, str):
            image = None
        if isinstance(audio, str):
            audio = None
        
        # Validar que al menos uno de los campos esté presente
        if not message and not image and not audio:
            raise HTTPException(
                status_code=400,
                detail="Debes proporcionar al menos un mensaje de texto, imagen o audio"
            )
        
        # Procesar imagen si está presente y es válida
        # Usar hasattr y comprobar directamente el tipo en string para debug
        if image is not None:
            if hasattr(image, 'filename') and hasattr(image, 'read'):
                if image.filename:
                    # Validar tipo de contenido
                    if not image.content_type or not image.content_type.startswith("image/"):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Tipo de archivo inválido para imagen: {image.content_type}"
                        )
                    
                    # Leer contenido de la imagen
                    image_data = await image.read()
                    media_type = image.content_type
                else:
                    logger.warning(f"⚠️ Image tiene filename vacío")
            else:
                logger.warning(f"⚠️ Image no tiene métodos de UploadFile")
        
        # Procesar audio si está presente y es válido
        if audio is not None:
            if hasattr(audio, 'filename') and hasattr(audio, 'read'):
                if audio.filename:
                    # Validar tipo de contenido
                    if not audio.content_type or not audio.content_type.startswith("audio/"):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Tipo de archivo inválido para audio: {audio.content_type}"
                        )
                    
                    # Leer contenido del audio
                    audio_data = await audio.read()
                    media_type = audio.content_type
                else:
                    logger.warning(f"⚠️ Audio tiene filename vacío")
            else:
                logger.warning(f"⚠️ Audio no tiene métodos de UploadFile")
        
        # Generar respuesta de IA
        response = await ai_service.generate_response(
            user_message=message,
            phone_number=user_id,
            contact_name=user_name,
            image_data=image_data,
            audio_data=audio_data,
            media_type=media_type,
        )
        
        return ChatResponse(
            success=True,
            response=response,
            user_id=user_id,
            user_name=user_name,
            processed_media={
                "has_image": bool(image_data),
                "has_audio": bool(audio_data),
            },
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando chat multimodal: {str(e)}", exc_info=True)
        return ChatResponse(
            success=False,
            response="",
            user_id=user_id,
            user_name=user_name or "",
            processed_media={
                "has_image": bool(image_data),
                "has_audio": bool(audio_data),
            },
            error=str(e),
        )


@router.delete(
    "/history/{user_id}",
    summary="Limpiar historial de conversación",
    description="""Limpia el historial de conversación de un usuario.
    
    ✅ **Endpoint público - No requiere autenticación.**
    
    Útil para:
    - Reiniciar una conversación
    - Liberar memoria
    - Resolver problemas de contexto
    - Protección de datos (GDPR)
    """,
    responses={
        200: {"description": "Historial limpiado exitosamente"},
    },
)
async def clear_history(
    user_id: str,
):
    """Limpia el historial de conversación de un usuario."""
    try:
        ai_service.clear_history(user_id)
        return {
            "success": True,
            "message": f"Historial limpiado para usuario: {user_id}"
        }
    except Exception as e:
        logger.error(f"Error limpiando historial: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/statistics",
    summary="Estadísticas del servicio de IA",
    description="""Obtiene estadísticas del servicio de IA.
    
    ✅ **Endpoint público - No requiere autenticación.**
    
    Muestra:
    - Conversaciones activas
    - Total de mensajes procesados
    - Configuración del servicio
    """,
    responses={
        200: {"description": "Estadísticas obtenidas exitosamente"},
    },
)
async def get_statistics():
    """Obtiene estadísticas del servicio de IA."""
    try:
        return ai_service.get_statistics()
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/status",
    summary="Estado del servicio de IA",
    description="Verifica que el servicio de IA está activo y configurado correctamente",
)
async def ai_status():
    """Verifica el estado del servicio de IA."""
    try:
        from app.core.config import settings
        
        stats = ai_service.get_statistics()
        
        return {
            "status": "active",
            "service": "Azure OpenAI",
            "deployment": settings.azure_openai_chat_deployment_name,
            "features": {
                "text_processing": True,
                "image_processing": True,
                "audio_transcription": True,
                "conversation_history": True,
            },
            "statistics": stats,
        }
    except Exception as e:
        logger.error(f"Error verificando estado del servicio: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
        }
