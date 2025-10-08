"""
Configuración de la aplicación híbrida FastAPI + Ionic Angular.
"""

import os
import socket
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
    
    # Azure Communication Services Configuration
    azure_communication_endpoint: str
    azure_communication_key: str
    azure_communication_sender_address: str
    
    # Configuración de deployment
    deploy_host: Optional[str] = None
    deploy_user: Optional[str] = None
    deploy_base_path: Optional[str] = None
    
    # Configuración de Microsoft Azure AD (opcional para autenticación)
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    
    # Configuración de autenticación JWE (debe ser exactamente 32 bytes)
    jwe_secret_key: str = "ezekl-budget-2024-jwe-secret-32b"  # Exactamente 32 bytes
    
    # Configuración del entorno
    environment: str = "development"  # development, production
    
    # URL base de la aplicación (frontend y backend en el mismo dominio)
    url_base: Optional[str] = None
    
    # Configuración de Base de Datos SQL Server
    db_host: str
    db_port: int = 1433
    db_name: str
    db_user: str
    db_password: str
    db_driver: str = "ODBC Driver 18 for SQL Server"
    db_trust_cert: str = "yes"
    
    @property
    def is_production(self) -> bool:
        """Detecta si la aplicación está corriendo en producción basado en ENVIRONMENT."""
        return self.environment.lower() == "production"
    
    @property
    def effective_url_base(self) -> str:
        """Retorna la URL base de la aplicación (frontend y backend en el mismo dominio)."""
        if self.url_base:
            return self.url_base
        
        # Detección automática por ambiente
        if self.is_production:
            return "https://budget.ezekl.com"
        else:
            return "http://localhost:8001"
    
    @property
    def effective_db_host(self) -> str:
        """Retorna el host efectivo de BD basado en el ambiente."""
        if self.is_production:
            return "localhost"
        else:
            return self.db_host
    
    @property
    def db_connection_string(self) -> str:
        """Genera la cadena de conexión para SQL Server."""
        return (
            f"DRIVER={{{self.db_driver}}};"
            f"SERVER={self.effective_db_host},{self.db_port};"
            f"DATABASE={self.db_name};"
            f"UID={self.db_user};"
            f"PWD={self.db_password};"
            f"TrustServerCertificate={self.db_trust_cert};"
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Permitir campos extra en caso de que se agreguen nuevas variables
        extra = "ignore"


# Instancia global de configuración
settings = Settings()