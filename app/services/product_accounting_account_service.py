"""
Servicio para gestión de cuentas contables de productos.
Maneja la lógica de negocio para cuentas contables asociadas a productos.
"""

import logging
import json
from typing import Dict, Any, List
from app.database.connection import execute_sp

# Configurar logging
logger = logging.getLogger(__name__)


async def update_product_accounting_account(
    id_product: int,
    id_company: int,
    accounting_accounts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Actualiza las cuentas contables de un producto.
    
    Args:
        id_product: ID del producto a actualizar
        id_company: ID de la compañía
        accounting_accounts: Lista de cuentas contables con sus configuraciones
        
    Returns:
        Diccionario con el resultado de la operación
        
    Raises:
        ValueError: Si el producto no existe, hay error en validación o porcentajes no suman 100
        Exception: Si hay error en la base de datos
    """
    try:
        # Preparar JSON para el stored procedure
        sp_json = {
            "idCompany": id_company,
            "idProduct": id_product,
            "accountingAccount": accounting_accounts
        }
        
        logger.info(f"Actualizando cuentas contables del producto {id_product}")
        logger.debug(f"Datos: {sp_json}")
        
        # Ejecutar stored procedure
        result = await execute_sp("spProductAccountingAccountEdit", sp_json)
        
        if not result:
            logger.error("No se recibió respuesta del stored procedure")
            raise Exception("Error al actualizar cuentas contables del producto")
        
        logger.info(f"Cuentas contables del producto {id_product} actualizadas exitosamente")
        return result
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error al actualizar cuentas contables del producto: {error_message}")
        
        # Verificar si es un error de porcentajes
        if "porcentajes" in error_message.lower() and "100" in error_message:
            raise ValueError("Los porcentajes para cada efecto deben sumar exactamente 100")
        
        raise
