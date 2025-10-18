"""
Modelos Pydantic para el servicio de IA.
Define las estructuras de datos para requests y responses del servicio de IA.
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Modelo para solicitud de chat con IA (texto simple)."""
    message: str = Field(..., description="Mensaje de texto del usuario")
    user_id: str = Field(..., description="Identificador único del usuario")
    user_name: Optional[str] = Field(None, description="Nombre del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "¿Cómo puedo crear un presupuesto?",
                "user_id": "user123",
                "user_name": "Juan Pérez"
            }
        }


class ChatResponse(BaseModel):
    """Modelo para respuesta de chat con IA."""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    response: str = Field(..., description="Respuesta generada por la IA")
    user_id: str = Field(..., description="Identificador del usuario")
    user_name: Optional[str] = Field(None, description="Nombre del usuario")
    processed_media: Dict[str, bool] = Field(
        ...,
        description="Información sobre el procesamiento de medios"
    )
    error: Optional[str] = Field(None, description="Mensaje de error si la operación falló")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "response": "Para crear un presupuesto en Ezekl Budget, primero debes...",
                "user_id": "user123",
                "user_name": "Juan Pérez",
                "processed_media": {
                    "has_image": False,
                    "has_audio": False
                },
                "error": None
            }
        }


class HistoryClearResponse(BaseModel):
    """Modelo para respuesta de limpieza de historial."""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje de confirmación")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Historial limpiado para usuario: user123"
            }
        }


class AIStatisticsResponse(BaseModel):
    """Modelo para respuesta de estadísticas del servicio de IA."""
    active_conversations: int = Field(..., description="Número de conversaciones activas")
    total_messages: int = Field(..., description="Total de mensajes procesados")
    max_history_per_conversation: int = Field(
        ...,
        description="Máximo de mensajes guardados por conversación"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "active_conversations": 5,
                "total_messages": 127,
                "max_history_per_conversation": 10
            }
        }


class AIStatusResponse(BaseModel):
    """Modelo para respuesta de estado del servicio de IA."""
    status: str = Field(..., description="Estado del servicio")
    service: str = Field(..., description="Nombre del servicio de IA")
    deployment: str = Field(..., description="Deployment de Azure OpenAI utilizado")
    features: Dict[str, bool] = Field(..., description="Características disponibles")
    statistics: AIStatisticsResponse = Field(..., description="Estadísticas del servicio")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "active",
                "service": "Azure OpenAI",
                "deployment": "gpt-5",
                "features": {
                    "text_processing": True,
                    "image_processing": True,
                    "audio_transcription": True,
                    "conversation_history": True
                },
                "statistics": {
                    "active_conversations": 5,
                    "total_messages": 127,
                    "max_history_per_conversation": 10
                }
            }
        }
