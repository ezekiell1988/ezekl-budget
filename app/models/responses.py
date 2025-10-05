"""
Modelos Pydantic para responses de la API.
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional


class CredentialsResponse(BaseModel):
    """Modelo de respuesta para las credenciales."""
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    message: str


class EmailSendRequest(BaseModel):
    """Modelo para request de envío de email."""
    to: List[EmailStr]
    subject: str
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    from_address: Optional[str] = None  # Si no se proporciona, usa el por defecto


class EmailSendResponse(BaseModel):
    """Modelo de respuesta para envío de email."""
    success: bool
    message: str