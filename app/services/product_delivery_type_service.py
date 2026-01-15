"""
Servicio para gestión de tipos de entrega de productos.
Maneja la lógica de negocio para tipos de entrega asociados a productos.
"""

import logging
import json
from typing import Dict, Any, List
from app.database.connection import execute_sp

# Configurar logging
logger = logging.getLogger(__name__)


async def update_product_delivery_type(
    id_product: int,
    id_company: int,
    delivery_types: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Actualiza los tipos de entrega de un producto.
    
    Args:
        id_product: ID del producto a actualizar
        id_company: ID de la compañía
        delivery_types: Lista de tipos de entrega con sus configuraciones
        
    Returns:
        Diccionario con el resultado de la operación
        
    Raises:
        ValueError: Si el producto no existe o hay error en validación
        Exception: Si hay error en la base de datos
    """
    try:
        # Preparar JSON para el stored procedure
        sp_json = {
            "idCompany": id_company,
            "idProduct": id_product,
            "deliveryType": delivery_types
        }
        
        logger.info(f"Actualizando tipos de entrega del producto {id_product}")
        logger.debug(f"Datos: {sp_json}")
        
        # Ejecutar stored procedure
        result = await execute_sp("spProductDeliveryTypeEdit", sp_json)
        
        if not result:
            logger.error("No se recibió respuesta del stored procedure")
            raise Exception("Error al actualizar tipos de entrega del producto")
        
        logger.info(f"Tipos de entrega del producto {id_product} actualizados exitosamente")
        return result
        
    except Exception as e:
        logger.error(f"Error al actualizar tipos de entrega del producto: {str(e)}")
        raise
