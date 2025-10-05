"""
Configuración de la aplicación híbrida FastAPI + Ionic Angular.
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuraciones de la aplicación cargadas desde variables de entorno."""
    
    # Configuración del servidor
    port: int = 8001
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment_name: str
    
    # Configuración de deployment
    deploy_host: Optional[str] = None
    deploy_user: Optional[str] = None
    deploy_base_path: Optional[str] = None
    
    # Configuración de Microsoft Azure AD (opcional para autenticación)
    azure_client_id: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Permitir campos extra en caso de que se agreguen nuevas variables
        extra = "ignore"


# Instancia global de configuración
settings = Settings()
