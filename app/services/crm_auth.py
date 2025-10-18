"""
Servicio de autenticación para Dynamics 365 CRM.
Maneja la obtención y caché de tokens de acceso para la API de Dynamics 365.
"""

import time
import aiohttp
import logging
from typing import Dict, Any
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)


class CRMAuthService:
    """
    Servicio de autenticación para Dynamics 365 usando client credentials flow.
    
    Gestiona la obtención automática de tokens de Azure AD y su caché en memoria
    para evitar solicitudes innecesarias al endpoint de autenticación.
    """
    
    def __init__(self):
        """Inicializa el servicio de autenticación CRM."""
        # Cache simple de token en memoria
        self._token_cache: Dict[str, Any] = {
            "access_token": None,
            "expires_at": 0,  # epoch seconds
        }
        
        # Configuración de Azure AD desde variables de entorno
        self.tenant_id = getattr(settings, 'crm_tenant_id', None)
        self.client_id = getattr(settings, 'crm_client_id', None)
        self.client_secret = getattr(settings, 'crm_client_secret', None)
        self.d365_base_url = getattr(settings, 'crm_d365_base_url', None)
        
        if not all([self.tenant_id, self.client_id, self.client_secret, self.d365_base_url]):
            logger.warning("⚠️ Configuración de CRM incompleta. Algunos endpoints no funcionarán.")
        
        # URLs de autenticación
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.oauth_scope = f"{self.d365_base_url}/.default" if self.d365_base_url else None
    
    @property
    def is_configured(self) -> bool:
        """Verifica si el servicio está completamente configurado."""
        return all([self.tenant_id, self.client_id, self.client_secret, self.d365_base_url])
    
    async def get_access_token(self) -> str:
        """
        Obtiene un token de acceso válido para Dynamics 365.
        
        Utiliza el caché interno para evitar solicitudes innecesarias.
        El token se renueva automáticamente 30 segundos antes de expirar.
        
        Returns:
            str: Token de acceso válido para usar con la API de Dynamics 365
            
        Raises:
            HTTPException: Si no se puede obtener el token o la configuración es inválida
        """
        if not self.is_configured:
            raise HTTPException(
                status_code=500, 
                detail="Configuración de CRM incompleta. Verifique las variables de entorno CRM_*"
            )
        
        now = int(time.time())
        
        # Verificar si tenemos un token válido (con 30 segundos de buffer)
        if self._token_cache["access_token"] and self._token_cache["expires_at"] - 30 > now:
            return self._token_cache["access_token"]

        # Solicitar nuevo token
        
        form_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": self.oauth_scope,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=form_data) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"❌ Error obteniendo token: HTTP {resp.status} - {error_text}")
                        raise HTTPException(
                            status_code=resp.status, 
                            detail=f"Error de autenticación CRM: {error_text}"
                        )
                    
                    data = await resp.json()

            access_token = data.get("access_token")
            expires_in = int(data.get("expires_in", 3599))
            
            if not access_token:
                raise HTTPException(
                    status_code=500, 
                    detail="Token de acceso no recibido en la respuesta de Azure AD"
                )
            
            # Actualizar caché
            self._token_cache["access_token"] = access_token
            self._token_cache["expires_at"] = int(time.time()) + expires_in
            
            return access_token
            
        except aiohttp.ClientError as e:
            logger.error(f"❌ Error de conexión al obtener token: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error de conexión con Azure AD: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Error inesperado al obtener token: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error interno al obtener token: {str(e)}"
            )
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        Obtiene información del token en caché para diagnósticos.
        
        Returns:
            Dict con información del estado del token
        """
        now = int(time.time())
        return {
            "has_token": bool(self._token_cache["access_token"]),
            "expires_at": self._token_cache["expires_at"],
            "is_expired": self._token_cache["expires_at"] <= now,
            "expires_in_seconds": max(0, self._token_cache["expires_at"] - now),
            "is_configured": self.is_configured,
            "tenant_id": self.tenant_id[:8] + "..." if self.tenant_id else None,
            "d365_base_url": self.d365_base_url
        }
    
    def clear_token_cache(self):
        """Limpia el caché de token (útil para testing o troubleshooting)."""
        self._token_cache["access_token"] = None
        self._token_cache["expires_at"] = 0


# Instancia global del servicio de autenticación
crm_auth_service = CRMAuthService()