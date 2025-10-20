"""
Servicio unificado de autenticación para Web y WhatsApp.
Maneja sesiones de 24 horas en Redis para todos los tipos de autenticación.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.redis import redis_client

logger = logging.getLogger(__name__)


class AuthService:
    """
    Servicio centralizado para gestión de autenticación.
    Soporta múltiples tipos de autenticación: web, whatsapp, etc.
    """
    
    def __init__(self):
        """Inicializa el servicio de autenticación."""
        pass
    
    async def save_session(
        self,
        user_id: str,
        user_data: Dict[str, Any],
        session_type: str = "web",
        expires_in_seconds: int = 86400  # 24 horas por defecto
    ) -> bool:
        """
        Guarda una sesión de usuario en Redis.
        
        Args:
            user_id: Identificador único del usuario (email, phone, etc.)
            user_data: Datos completos del usuario
            session_type: Tipo de sesión ("web", "whatsapp", etc.)
            expires_in_seconds: Tiempo de expiración en segundos (default: 24 horas)
            
        Returns:
            True si se guardó exitosamente
        """
        # Inicializar Redis si no está conectado
        if not redis_client.is_connected:
            await redis_client.initialize()
        
        # Construir clave con el tipo de sesión
        key = f"auth_session:{session_type}:{user_id}"
        
        # Agregar metadata a los datos
        session_data = {
            **user_data,
            "session_type": session_type,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "expires_in": expires_in_seconds
        }
        
        # Guardar en Redis con TTL
        await redis_client.set(key, session_data, expires_in_seconds=expires_in_seconds)
        
        logger.info(f"✅ Sesión guardada para {session_type}:{user_id} (válida por {expires_in_seconds}s)")
        return True
    
    async def get_session(self, user_id: str, session_type: str = "web") -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de sesión de un usuario.
        
        Args:
            user_id: Identificador único del usuario
            session_type: Tipo de sesión ("web", "whatsapp", etc.)
            
        Returns:
            Datos del usuario si la sesión es válida, None si no existe o expiró
        """
        # Inicializar Redis si no está conectado
        if not redis_client.is_connected:
            await redis_client.initialize()
        
        key = f"auth_session:{session_type}:{user_id}"
        data = await redis_client.get(key)
        
        if not data:
            logger.info(f"❌ Sesión no encontrada o expirada: {session_type}:{user_id}")
            return None
        
        logger.info(f"✅ Sesión válida para {session_type}:{user_id}")
        return data
    
    async def is_authenticated(self, user_id: str, session_type: str = "web") -> bool:
        """
        Verifica si un usuario tiene una sesión activa.
        
        Args:
            user_id: Identificador único del usuario
            session_type: Tipo de sesión
            
        Returns:
            True si tiene sesión activa, False si no
        """
        session_data = await self.get_session(user_id, session_type)
        return session_data is not None
    
    async def delete_session(self, user_id: str, session_type: str = "web") -> bool:
        """
        Elimina una sesión de usuario (logout).
        
        Args:
            user_id: Identificador único del usuario
            session_type: Tipo de sesión
            
        Returns:
            True si se eliminó exitosamente
        """
        # Inicializar Redis si no está conectado
        if not redis_client.is_connected:
            await redis_client.initialize()
        
        key = f"auth_session:{session_type}:{user_id}"
        result = await redis_client.delete(key)
        
        if result:
            logger.info(f"✅ Sesión eliminada: {session_type}:{user_id}")
        else:
            logger.warning(f"⚠️  No se encontró sesión para eliminar: {session_type}:{user_id}")
        
        return result
    
    async def extend_session(
        self,
        user_id: str,
        session_type: str = "web",
        expires_in_seconds: int = 86400
    ) -> bool:
        """
        Extiende el tiempo de vida de una sesión existente.
        
        Args:
            user_id: Identificador único del usuario
            session_type: Tipo de sesión
            expires_in_seconds: Nuevo tiempo de expiración en segundos
            
        Returns:
            True si se extendió exitosamente
        """
        # Obtener datos actuales
        session_data = await self.get_session(user_id, session_type)
        
        if not session_data:
            logger.warning(f"⚠️  No se puede extender sesión inexistente: {session_type}:{user_id}")
            return False
        
        # Re-guardar con nuevo TTL
        await self.save_session(user_id, session_data, session_type, expires_in_seconds)
        
        logger.info(f"⏱️  Sesión extendida para {session_type}:{user_id} (+{expires_in_seconds}s)")
        return True
    
    async def get_session_ttl(self, user_id: str, session_type: str = "web") -> Optional[int]:
        """
        Obtiene el tiempo restante de una sesión en segundos.
        
        Args:
            user_id: Identificador único del usuario
            session_type: Tipo de sesión
            
        Returns:
            Segundos restantes, o None si no existe la sesión
        """
        # Inicializar Redis si no está conectado
        if not redis_client.is_connected:
            await redis_client.initialize()
        
        key = f"auth_session:{session_type}:{user_id}"
        ttl = await redis_client.ttl(key)
        
        if ttl and ttl > 0:
            logger.info(f"⏰ TTL de sesión {session_type}:{user_id}: {ttl}s")
            return ttl
        
        return None


# Instancia global del servicio
auth_service = AuthService()
