"""
Módulo de base de datos asíncrono para la aplicación ezekl-budget.
Maneja conexiones a SQL Server y ejecución de stored procedures con JSON usando async/await.
"""

import json
import logging
from typing import Dict, Any, Optional
import aioodbc
import pyodbc  # Para tipos y excepciones
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)


class AsyncDatabaseManager:
    """Administrador asíncrono de conexiones y operaciones de base de datos."""
    
    def __init__(self):
        self.connection_string = settings.db_connection_string
    
    async def get_connection(self) -> aioodbc.Connection:
        """
        Obtiene una nueva conexión asíncrona a la base de datos.
        
        Returns:
            aioodbc.Connection: Conexión asíncrona a la base de datos
            
        Raises:
            Exception: Si no se puede establecer la conexión
        """
        try:
            connection = await aioodbc.connect(dsn=self.connection_string, timeout=30)
            return connection
        except Exception as e:
            logger.error(f"Error al conectar con la base de datos: {str(e)}")
            raise Exception(f"Error de conexión a base de datos: {str(e)}")
    
    async def test_connection(self) -> bool:
        """
        Prueba la conexión asíncrona a la base de datos.
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            async with await self.get_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
                    return True
        except Exception as e:
            logger.error(f"Error en test de conexión asíncrona: {str(e)}")
            return False
    
    async def execute_stored_procedure(self, procedure_name: str, json_param: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta de forma asíncrona un stored procedure que recibe un JSON como parámetro único
        y devuelve un JSON en una columna llamada 'json'.
        
        Args:
            procedure_name (str): Nombre del stored procedure a ejecutar
            json_param (Dict[str, Any]): Parámetros en formato diccionario que se convertirán a JSON
            
        Returns:
            Dict[str, Any]: Respuesta del stored procedure parseada desde JSON
            
        Raises:
            Exception: Si hay error en la ejecución del stored procedure
        """
        try:
            # Convertir el diccionario a JSON string
            json_string = json.dumps(json_param, ensure_ascii=False)
            
            async with await self.get_connection() as conn:
                async with conn.cursor() as cursor:
                    
                    # Ejecutar el stored procedure
                    query = f"EXEC {procedure_name} ?"
                    
                    await cursor.execute(query, json_string)
                    
                    # Para stored procedures que no retornan datos (UPDATE, DELETE, INSERT sin OUTPUT)
                    # intentamos obtener el resultado, pero si no hay, es normal
                    try:
                        row = await cursor.fetchone()
                        
                        # Si no hay resultado, el SP fue exitoso pero no retorna datos
                        if row is None:
                            logger.info(f"SP {procedure_name} ejecutado exitosamente sin datos de retorno")
                            return {"success": True}
                        
                        # La columna debe llamarse 'json'
                        json_result = row.json if hasattr(row, 'json') else row[0]
                        
                        if json_result is None:
                            logger.info(f"El SP {procedure_name} ejecutado exitosamente sin datos de retorno")
                            return {"success": True}
                        
                        # Parsear el JSON de respuesta
                        result = json.loads(json_result)
                        return result
                        
                    except Exception as fetch_error:
                        # Si el error es porque no hay resultados, está bien
                        if "No results" in str(fetch_error) or "Previous SQL was not a query" in str(fetch_error):
                            logger.info(f"SP {procedure_name} ejecutado exitosamente (no retorna datos)")
                            return {"success": True}
                        else:
                            # Si es otro tipo de error, re-lanzarlo
                            raise fetch_error
                    
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON en SP {procedure_name}: {str(e)}")
            raise Exception(f"Error al parsear JSON de respuesta: {str(e)}")
        
        except pyodbc.Error as e:
            logger.error(f"Error de base de datos en SP {procedure_name}: {str(e)}")
            # Si es un RAISERROR, extraer el mensaje
            error_message = str(e)
            if "No se encontró la compañía" in error_message:
                raise Exception(f"Compañía no encontrada: {error_message}")
            elif "duplicate" in error_message.lower() or "unique" in error_message.lower():
                raise Exception(f"Código duplicado: {error_message}")
            else:
                raise Exception(f"Error de base de datos: {error_message}")
        
        except Exception as e:
            logger.error(f"Error inesperado en SP {procedure_name}: {str(e)}")
            raise Exception(f"Error inesperado: {str(e)}")
    
    async def execute_raw_query(self, query: str) -> Optional[Any]:
        """
        Ejecuta de forma asíncrona una consulta SQL raw (solo para casos especiales o testing).
        
        Args:
            query (str): Consulta SQL a ejecutar
            
        Returns:
            Optional[Any]: Resultado de la consulta
            
        Note:
            Este método debe usarse con precaución y preferiblemente solo para testing
        """
        try:
            async with await self.get_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query)
                    
                    # Si es una consulta SELECT, devolver los resultados
                    if query.strip().upper().startswith('SELECT'):
                        return await cursor.fetchall()
                    else:
                        # Para INSERT, UPDATE, DELETE, etc.
                        await conn.commit()
                        return cursor.rowcount
                        
        except Exception as e:
            logger.error(f"Error ejecutando consulta raw asíncrona: {str(e)}")
            raise Exception(f"Error ejecutando consulta: {str(e)}")


# Instancia global del administrador de base de datos asíncrono
async_db_manager = AsyncDatabaseManager()


# Funciones de conveniencia asíncronas
async def test_db_connection() -> bool:
    """Función de conveniencia para probar la conexión a la base de datos de forma asíncrona."""
    return await async_db_manager.test_connection()


async def execute_sp(procedure_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función de conveniencia para ejecutar stored procedures de forma asíncrona.
    
    Args:
        procedure_name (str): Nombre del stored procedure
        parameters (Dict[str, Any]): Parámetros a enviar al stored procedure
        
    Returns:
        Dict[str, Any]: Respuesta del stored procedure
    """
    return await async_db_manager.execute_stored_procedure(procedure_name, parameters)


# Ejemplo de uso:
# result = await execute_sp("spLoginAuth", {"codeLogin": "S", "token": "12345"})