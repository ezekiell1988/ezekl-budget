"""
Cliente genérico de Redis para manejo de cache y sesiones.
Proporciona una capa de abstracción reutilizable para operaciones con Redis.
"""

import json
import logging
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Cliente genérico de Redis para operaciones de cache y persistencia temporal.
    
    Proporciona métodos de alto nivel para:
    - Operaciones básicas (get, set, delete, exists)
    - Manejo de expiración automática
    - Serialización/deserialización automática de JSON
    - Gestión de conexión y reconexión
    """
    
    def __init__(self):
        """Inicializa el cliente de Redis."""
        self.redis_client: Optional[redis.Redis] = None
        self._initialized = False
        
    async def initialize(self):
        """
        Inicializa la conexión a Redis.
        
        Raises:
            Exception: Si no se puede conectar a Redis
        """
        if self._initialized:
            return
            
        try:
            self.redis_client = await redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=settings.redis_decode_responses,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            
            # Verificar conexión
            await self.redis_client.ping()
            self._initialized = True
            logger.info("✅ Redis conectado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error conectando a Redis: {str(e)}")
            self.redis_client = None
            self._initialized = False
            raise
    
    async def close(self):
        """Cierra la conexión a Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self._initialized = False
            logger.info("Redis connection closed")
    
    @property
    def is_connected(self) -> bool:
        """
        Verifica si Redis está conectado.
        
        Returns:
            True si la conexión está activa, False si no
        """
        return self._initialized and self.redis_client is not None
    
    def _check_connection(self):
        """
        Verifica la conexión antes de realizar operaciones.
        
        Raises:
            Exception: Si Redis no está conectado
        """
        if not self.is_connected:
            raise Exception("Redis no está conectado. Llame a initialize() primero.")
    
    # ============== MÉTODOS BÁSICOS DE CACHE ==============
    
    async def set(
        self,
        key: str,
        value: Any,
        expires_in_seconds: Optional[int] = None
    ) -> bool:
        """
        Guarda un valor en cache con expiración opcional.
        
        Args:
            key: Clave para identificar el valor
            value: Valor a guardar (será serializado a JSON si no es string)
            expires_in_seconds: Tiempo de expiración en segundos (opcional)
            
        Returns:
            True si se guardó exitosamente
            
        Example:
            await redis_client.set("user:123", {"name": "Juan"}, expires_in_seconds=3600)
        """
        self._check_connection()
        
        # Serializar a JSON si no es string
        value_str = json.dumps(value) if not isinstance(value, str) else value
        
        if expires_in_seconds:
            await self.redis_client.setex(key, expires_in_seconds, value_str)
        else:
            await self.redis_client.set(key, value_str)
        
        return True
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del cache.
        
        Args:
            key: Clave del valor a obtener
            
        Returns:
            Valor deserializado si existe, None si no existe
            
        Example:
            user_data = await redis_client.get("user:123")
        """
        self._check_connection()
        
        value_str = await self.redis_client.get(key)
        if not value_str:
            return None
        
        # Intentar deserializar JSON, si falla retornar string
        try:
            return json.loads(value_str)
        except json.JSONDecodeError:
            return value_str
    
    async def delete(self, key: str) -> bool:
        """
        Elimina un valor del cache.
        
        Args:
            key: Clave del valor a eliminar
            
        Returns:
            True si se eliminó, False si no existía
            
        Example:
            deleted = await redis_client.delete("user:123")
        """
        self._check_connection()
        
        result = await self.redis_client.delete(key)
        return result > 0
    
    async def exists(self, key: str) -> bool:
        """
        Verifica si existe una clave en cache.
        
        Args:
            key: Clave a verificar
            
        Returns:
            True si existe, False si no
            
        Example:
            if await redis_client.exists("user:123"):
                print("Usuario en cache")
        """
        self._check_connection()
        
        result = await self.redis_client.exists(key)
        return result > 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Establece o actualiza el tiempo de expiración de una clave.
        
        Args:
            key: Clave a la que se le establecerá expiración
            seconds: Segundos hasta la expiración
            
        Returns:
            True si se estableció la expiración, False si la clave no existe
            
        Example:
            await redis_client.expire("user:123", 3600)  # Expira en 1 hora
        """
        self._check_connection()
        
        result = await self.redis_client.expire(key, seconds)
        return result > 0
    
    async def ttl(self, key: str) -> int:
        """
        Obtiene el tiempo restante hasta la expiración de una clave.
        
        Args:
            key: Clave a consultar
            
        Returns:
            Segundos restantes hasta expiración, -1 si no tiene expiración, -2 si no existe
            
        Example:
            remaining = await redis_client.ttl("user:123")
        """
        self._check_connection()
        
        return await self.redis_client.ttl(key)
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Incrementa un valor numérico en cache.
        
        Args:
            key: Clave del contador
            amount: Cantidad a incrementar (default: 1)
            
        Returns:
            Nuevo valor después del incremento
            
        Example:
            visits = await redis_client.increment("page_visits")
        """
        self._check_connection()
        
        return await self.redis_client.incrby(key, amount)
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        """
        Decrementa un valor numérico en cache.
        
        Args:
            key: Clave del contador
            amount: Cantidad a decrementar (default: 1)
            
        Returns:
            Nuevo valor después del decremento
            
        Example:
            remaining = await redis_client.decrement("tokens_remaining")
        """
        self._check_connection()
        
        return await self.redis_client.decrby(key, amount)
    
    # ============== MÉTODOS AVANZADOS ==============
    
    async def get_many(self, *keys: str) -> list[Optional[Any]]:
        """
        Obtiene múltiples valores en una sola operación.
        
        Args:
            *keys: Claves a obtener
            
        Returns:
            Lista de valores en el mismo orden que las claves
            
        Example:
            values = await redis_client.get_many("user:1", "user:2", "user:3")
        """
        self._check_connection()
        
        if not keys:
            return []
        
        values = await self.redis_client.mget(*keys)
        
        # Deserializar cada valor
        result = []
        for value_str in values:
            if value_str is None:
                result.append(None)
            else:
                try:
                    result.append(json.loads(value_str))
                except json.JSONDecodeError:
                    result.append(value_str)
        
        return result
    
    async def set_many(self, mapping: dict[str, Any]) -> bool:
        """
        Guarda múltiples valores en una sola operación.
        
        Args:
            mapping: Diccionario de clave-valor a guardar
            
        Returns:
            True si se guardaron exitosamente
            
        Example:
            await redis_client.set_many({
                "user:1": {"name": "Juan"},
                "user:2": {"name": "María"}
            })
        """
        self._check_connection()
        
        if not mapping:
            return True
        
        # Serializar todos los valores
        serialized = {
            key: json.dumps(value) if not isinstance(value, str) else value
            for key, value in mapping.items()
        }
        
        await self.redis_client.mset(serialized)
        return True
    
    async def delete_many(self, *keys: str) -> int:
        """
        Elimina múltiples claves en una sola operación.
        
        Args:
            *keys: Claves a eliminar
            
        Returns:
            Número de claves eliminadas
            
        Example:
            deleted = await redis_client.delete_many("user:1", "user:2")
        """
        self._check_connection()
        
        if not keys:
            return 0
        
        return await self.redis_client.delete(*keys)
    
    async def keys(self, pattern: str) -> list[str]:
        """
        Busca claves que coincidan con un patrón.
        
        Args:
            pattern: Patrón de búsqueda (usar * como wildcard)
            
        Returns:
            Lista de claves que coinciden con el patrón
            
        Warning:
            Este método puede ser lento en producción con muchas claves.
            Usar con precaución.
            
        Example:
            user_keys = await redis_client.keys("user:*")
        """
        self._check_connection()
        
        return await self.redis_client.keys(pattern)


# Instancia global del cliente de Redis
redis_client = RedisClient()
