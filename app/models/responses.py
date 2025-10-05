"""
Modelos Pydantic para responses de la API.
"""

from pydantic import BaseModel


class CredentialsResponse(BaseModel):
    """Modelo de respuesta para las credenciales."""
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    message: str