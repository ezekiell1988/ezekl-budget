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
    
    # Configuración de deployment
    deploy_host: Optional[str] = None
    deploy_user: Optional[str] = None
    deploy_base_path: Optional[str] = None
    
    # Configuración de Microsoft Azure AD (opcional para autenticación)
    azure_client_id: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    
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
        """Detecta si la aplicación está corriendo en el servidor de producción."""
        # Método 1: Verificar si estamos en el servidor Azure por hostname
        hostname = socket.gethostname()
        if "demo-linux" in hostname.lower():
            return True
            
        # Método 2: Verificar por variable de entorno
        if os.getenv("ENVIRONMENT") == "production":
            return True
            
        # Método 3: Verificar si SQL Server está disponible localmente
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 1433))
            sock.close()
            if result == 0:  # Puerto está abierto localmente
                return True
        except:
            pass
            
        return False
    
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
