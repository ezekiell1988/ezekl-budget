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
    azure_openai_chat_deployment_name: str = "gpt-5-pro"  # Deployment para chat (WhatsApp, etc.)
    azure_openai_audio_deployment_name: str = "gpt-4o-transcribe"  # Deployment para transcripción de audio
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_audio_api_version: str = "2025-03-01-preview"  # API version para audio transcription
    
    # Azure Communication Services Configuration
    azure_communication_endpoint: str
    azure_communication_key: str
    azure_communication_sender_address: str
    
    # Configuración de Microsoft Azure AD (opcional para autenticación)
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    
    # Microsoft OAuth Endpoints (para autenticación web y WhatsApp)
    microsoft_authorization_endpoint: Optional[str] = None
    microsoft_token_endpoint: Optional[str] = None
    microsoft_redirect_uri: Optional[str] = None
    
    # Configuración de Dynamics 365 CRM
    crm_tenant_id: Optional[str] = None
    crm_client_id: Optional[str] = None
    crm_client_secret: Optional[str] = None
    crm_d365_base_url: Optional[str] = None
    crm_api_version: str = "v9.0"
    
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
    
    # Configuración de WhatsApp Business API
    whatsapp_access_token: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_verify_token: str = "mi_token_secreto_whatsapp_2024"
    whatsapp_api_version: str = "v24.0"
    
    # Configuración de Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_decode_responses: bool = True
    
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
    def effective_microsoft_authorization_endpoint(self) -> str:
        """Retorna el endpoint de autorización de Microsoft OAuth."""
        if self.microsoft_authorization_endpoint:
            return self.microsoft_authorization_endpoint
        
        # Generar automáticamente si se tiene tenant_id
        if self.azure_tenant_id:
            return f"https://login.microsoftonline.com/{self.azure_tenant_id}/oauth2/v2.0/authorize"
        
        return "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    
    @property
    def effective_microsoft_token_endpoint(self) -> str:
        """Retorna el endpoint de token de Microsoft OAuth."""
        if self.microsoft_token_endpoint:
            return self.microsoft_token_endpoint
        
        # Generar automáticamente si se tiene tenant_id
        if self.azure_tenant_id:
            return f"https://login.microsoftonline.com/{self.azure_tenant_id}/oauth2/v2.0/token"
        
        return "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    @property
    def effective_microsoft_redirect_uri(self) -> str:
        """Retorna el redirect URI de Microsoft OAuth."""
        if self.microsoft_redirect_uri:
            return self.microsoft_redirect_uri
        
        # Generar automáticamente basado en la URL base
        # IMPORTANTE: Esta URL debe coincidir exactamente con la registrada en Entra ID
        return f"{self.effective_url_base}/api/auth/microsoft/callback"
    
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