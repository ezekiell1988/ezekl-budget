"""
Servicio de autenticación para SharePoint Online usando OAuth2.
Gestiona tokens de acceso de Azure AD para Microsoft Graph API.
"""

import logging
import aiohttp
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SharePointAuthService:
    """
    Servicio de autenticación para SharePoint Online usando client credentials flow.
    
    Gestiona la obtención automática de tokens de Azure AD y su caché en memoria
    para evitar solicitudes innecesarias al endpoint de autenticación.
    """
    
    def __init__(self):
        """Inicializa el servicio de autenticación SharePoint."""
        from app.core.config import settings
        
        # Cache simple de token en memoria
        self._token_cache: Dict[str, Any] = {
            "access_token": None,
            "expires_at": 0,  # epoch seconds
        }
        
        # Configuración de Azure AD desde variables de entorno
        # Primero intenta usar variables específicas de SharePoint, sino usa las generales
        self.tenant_id = getattr(settings, 'sharepoint_tenant_id', None) or getattr(settings, 'azure_tenant_id', None)
        self.client_id = getattr(settings, 'sharepoint_client_id', None) or getattr(settings, 'azure_client_id', None)
        self.client_secret = getattr(settings, 'sharepoint_client_secret', None) or getattr(settings, 'azure_client_secret', None)
        
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            logger.warning("⚠️ Configuración de SharePoint incompleta. Algunos endpoints no funcionarán.")
        
        # URLs de autenticación
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        # Scope para Microsoft Graph API (SharePoint Online)
        self.oauth_scope = "https://graph.microsoft.com/.default"
    
    @property
    def is_configured(self) -> bool:
        """Verifica si el servicio está completamente configurado."""
        return all([self.tenant_id, self.client_id, self.client_secret])
    
    async def get_access_token(self) -> str:
        """
        Obtiene un token de acceso válido de Azure AD.
        Usa caché interno para evitar solicitudes innecesarias.
        
        Returns:
            str: Access token válido
            
        Raises:
            Exception: Si falla la autenticación con Azure AD
        """
        # Verificar configuración
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no está configurado. Verifica variables de entorno.")
        
        # Verificar si hay token en caché y no ha expirado
        now = datetime.utcnow().timestamp()
        
        if self._token_cache["access_token"] and self._token_cache["expires_at"] > now:
            expires_in = int(self._token_cache["expires_at"] - now)
            logger.debug(f"🔑 Usando token de SharePoint desde caché (expira en {expires_in}s)")
            return self._token_cache["access_token"]
        
        # Obtener nuevo token
        logger.info("🔄 Obteniendo nuevo token de acceso para SharePoint desde Azure AD...")
        
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.oauth_scope
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=token_data) as response:
                if response.status != 200:
                    error_detail = await response.text()
                    logger.error(f"❌ Error obteniendo token de SharePoint: {response.status} - {error_detail}")
                    raise Exception(f"Error de autenticación con Azure AD: {response.status}")
                
                token_response = await response.json()
                access_token = token_response.get("access_token")
                expires_in = token_response.get("expires_in", 3600)
            
            # Almacenar en caché con 5 minutos de margen antes de expiración
            expires_at = (datetime.utcnow() + timedelta(seconds=expires_in - 300)).timestamp()
            
            self._token_cache["access_token"] = access_token
            self._token_cache["expires_at"] = expires_at
            
            logger.info(f"✅ Token de SharePoint obtenido exitosamente (válido por {expires_in}s)")
            
            return access_token
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el token en caché.
        
        Returns:
            dict: Información del token (expires_at, expires_in_seconds, is_valid)
        """
        now = datetime.utcnow().timestamp()
        expires_at = datetime.fromtimestamp(self._token_cache["expires_at"]).isoformat() if self._token_cache["expires_at"] else None
        expires_in = int(self._token_cache["expires_at"] - now) if self._token_cache["expires_at"] > now else 0
        
        return {
            "has_token": bool(self._token_cache["access_token"]),
            "expires_at": expires_at,
            "expires_in_seconds": expires_in,
            "is_valid": self._token_cache["expires_at"] > now if self._token_cache["access_token"] else False
        }
    
    def clear_token_cache(self):
        """Limpia el caché de token (útil para testing o troubleshooting)."""
        logger.info("🗑️ Limpiando caché de token de SharePoint")
        self._token_cache = {
            "access_token": None,
            "expires_at": 0,
        }


# Instancia global del servicio
sharepoint_auth_service = SharePointAuthService()
