"""
Servicio para gestión de archivos multimedia de productos.
Maneja la lógica de negocio para archivos multimedia asociados a productos.
"""

import logging
from typing import Dict, Any, List
from fastapi import UploadFile
from app.database.connection import execute_sp
from app.utils.file_handler import (
    get_file_info,
    get_file_size,
    save_media_file,
    delete_media_file
)

# Configurar logging
logger = logging.getLogger(__name__)


async def add_product_media_files(
    id_product: int,
    id_company: int,
    files: List[UploadFile]
) -> Dict[str, Any]:
    """
    Agrega archivos multimedia a un producto.
    
    Args:
        id_product: ID del producto
        id_company: ID de la compañía
        files: Lista de archivos subidos por el usuario
        
    Returns:
        Diccionario con el resultado de la operación
        
    Raises:
        ValueError: Si el producto no existe o hay error en validación
        Exception: Si hay error en la base de datos
    """
    try:
        # Procesar cada archivo para obtener su información
        media_files_data = []
        for file in files:
            file_info = get_file_info(file)
            file_size = await get_file_size(file)
            
            media_files_data.append({
                "sizeMediaFile": file_size,
                "mimetype": file_info["mimetype"],
                "mediaType": file_info["mediaType"],
                "extension": file_info["extension"]
            })
        
        # Preparar JSON para el stored procedure
        sp_json = {
            "idCompany": id_company,
            "idProduct": id_product,
            "mediaFiles": media_files_data
        }
        
        logger.info(f"Agregando {len(files)} archivos multimedia al producto {id_product}")
        logger.debug(f"Datos: {sp_json}")
        
        # Ejecutar stored procedure
        result = await execute_sp("spProductMediaFileAdd", sp_json)
        
        if not result:
            logger.error("No se recibió respuesta del stored procedure")
            raise Exception("Error al agregar archivos multimedia al producto")
        
        # Guardar archivos físicamente con los nombres de la BD
        media_files_result = result.get('mediaFiles', [])
        for i, file in enumerate(files):
            if i < len(media_files_result):
                name_from_db = media_files_result[i].get('nameMediaFile')
                if name_from_db:
                    await save_media_file(file, name_from_db)
        
        logger.info(f"Archivos multimedia agregados exitosamente al producto {id_product}")
        return result
        
    except Exception as e:
        logger.error(f"Error al agregar archivos multimedia al producto: {str(e)}")
        raise


async def add_single_product_media_file(
    id_product: int,
    id_company: int,
    file: UploadFile
) -> Dict[str, Any]:
    """
    Agrega un solo archivo multimedia a un producto.
    
    Args:
        id_product: ID del producto
        id_company: ID de la compañía
        file: Archivo subido por el usuario
        
    Returns:
        Diccionario con el resultado de la operación
        
    Raises:
        ValueError: Si el producto no existe o hay error en validación
        Exception: Si hay error en la base de datos
    """
    return await add_product_media_files(id_product, id_company, [file])


async def delete_product_media_files(
    id_product: int,
    id_company: int,
    id_media_files: List[int]
) -> Dict[str, Any]:
    """
    Elimina archivos multimedia de un producto.
    
    Args:
        id_product: ID del producto
        id_company: ID de la compañía
        id_media_files: Lista de IDs de archivos multimedia a eliminar
        
    Returns:
        Diccionario con el resultado de la operación (incluye paths para eliminar físicamente)
        
    Raises:
        ValueError: Si el producto no existe o hay error en validación
        Exception: Si hay error en la base de datos
    """
    try:
        # Preparar JSON para el stored procedure
        sp_json = {
            "idCompany": id_company,
            "idProduct": id_product,
            "idMediaFiles": id_media_files
        }
        
        logger.info(f"Eliminando {len(id_media_files)} archivos multimedia del producto {id_product}")
        logger.debug(f"Datos: {sp_json}")
        
        # Ejecutar stored procedure
        result = await execute_sp("spProductMediaFileDel", sp_json)
        
        if not result:
            logger.error("No se recibió respuesta del stored procedure")
            raise Exception("Error al eliminar archivos multimedia del producto")
        
        # Eliminar archivos físicos
        media_files_result = result.get('mediaFiles', [])
        for media_file in media_files_result:
            path_from_db = media_file.get('pathMediaFile')
            if path_from_db:
                delete_media_file(path_from_db)
        
        logger.info(f"Archivos multimedia eliminados exitosamente del producto {id_product}")
        return result
        
    except Exception as e:
        logger.error(f"Error al eliminar archivos multimedia del producto: {str(e)}")
        raise
