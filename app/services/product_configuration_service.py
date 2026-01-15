"""
Servicio para gestión de configuración de productos.
Maneja la lógica de negocio para configuración de productos.
"""

import logging
import json
from typing import Dict, Any
from app.database.connection import execute_sp

# Configurar logging
logger = logging.getLogger(__name__)


async def update_product_configuration(
    id_product: int,
    id_company: int,
    configuration_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Actualiza la configuración de un producto.
    
    Args:
        id_product: ID del producto a actualizar
        id_company: ID de la compañía
        configuration_data: Datos de configuración del producto
        
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
            **configuration_data
        }
        
        logger.info(f"Actualizando configuración del producto {id_product}")
        logger.debug(f"Datos: {sp_json}")
        
        # Ejecutar stored procedure
        result = await execute_sp("spProductConfigurationEdit", sp_json)
        
        if not result:
            logger.error("No se recibió respuesta del stored procedure")
            raise Exception("Error al actualizar configuración del producto")
        
        logger.info(f"Configuración del producto {id_product} actualizada exitosamente")
        return result
        
    except Exception as e:
        logger.error(f"Error al actualizar configuración del producto: {str(e)}")
        raise
