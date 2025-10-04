"""
Configuración de la aplicación.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuraciones de la aplicación cargadas desde variables de entorno."""
    
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment_name: str
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global de configuración
settings = Settings()
