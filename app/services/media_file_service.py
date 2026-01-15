"""
Servicio para gestión de archivos multimedia.
Maneja la lógica de negocio para archivos multimedia independientes.
"""

import logging
from pathlib import Path
from typing import Dict, Any
from fastapi import UploadFile
from app.database.connection import execute_sp
from app.utils.file_handler import (
    get_file_info,
    get_file_size,
    save_media_file,
    delete_media_file,
    get_media_base_dir
)

# Configurar logging
logger = logging.getLogger(__name__)


async def create_media_file(
    id_company: int,
    file: UploadFile
) -> Dict[str, Any]:
    """
    Crea un archivo multimedia desde un archivo subido.
    
    Args:
        id_company: ID de la compañía
        file: Archivo subido por el usuario
        
    Returns:
        Diccionario con el resultado de la operación
        
    Raises:
        Exception: Si hay error en la base de datos o al guardar el archivo
    """
    try:
        # Extraer información del archivo
        file_info = get_file_info(file)
        file_size = await get_file_size(file)
        
        # Preparar JSON para el stored procedure
        sp_json = {
            "idCompany": id_company,
            "sizeMediaFile": file_size,
            "mimetype": file_info["mimetype"],
            "mediaType": file_info["mediaType"],
            "extension": file_info["extension"]
        }
        
        logger.info(f"Creando archivo multimedia: {file.filename}")
        logger.debug(f"Datos: {sp_json}")
        
        # Ejecutar stored procedure
        result = await execute_sp("spMediaFileAdd", sp_json)
        
        if not result:
            logger.error("No se recibió respuesta del stored procedure")
            raise Exception("Error al crear archivo multimedia")
        
        # Guardar archivo físicamente con el nombre de la BD
        name_from_db = result.get('nameMediaFile')
        if not name_from_db:
            raise Exception("No se recibió nombre de archivo de la BD")
        
        await save_media_file(file, name_from_db)
        
        logger.info(f"Archivo multimedia creado exitosamente con ID {result.get('idMediaFile')}")
        return result
        
    except Exception as e:
        logger.error(f"Error al crear archivo multimedia: {str(e)}")
        raise


async def delete_media_file_service(
    id_company: int,
    id_media_file: int
) -> Dict[str, Any]:
    """
    Elimina un archivo multimedia.
    
    Args:
        id_company: ID de la compañía
        id_media_file: ID del archivo multimedia a eliminar
        
    Returns:
        Diccionario con el resultado de la operación (incluye path para eliminar físicamente)
        
    Raises:
        ValueError: Si el archivo no existe o no pertenece a la compañía
        Exception: Si hay error en la base de datos
    """
    try:
        # Preparar JSON para el stored procedure
        sp_json = {
            "idCompany": id_company,
            "idMediaFile": id_media_file
        }
        
        logger.info(f"Eliminando archivo multimedia {id_media_file}")
        logger.debug(f"Datos: {sp_json}")
        
        # Ejecutar stored procedure
        result = await execute_sp("spMediaFileDel", sp_json)
        
        if not result:
            logger.error("No se recibió respuesta del stored procedure")
            raise Exception("Error al eliminar archivo multimedia")
        
        # Eliminar archivo físico
        path_from_db = result.get('pathMediaFile')
        if path_from_db:
            delete_media_file(path_from_db)
        
        logger.info(f"Archivo multimedia {id_media_file} eliminado exitosamente")
        return result
        
    except Exception as e:
        logger.error(f"Error al eliminar archivo multimedia: {str(e)}")
        raise


async def get_media_file_path(
    id_company: int,
    id_media_file: int
) -> Path:
    """
    Obtiene la ruta física de un archivo multimedia.
    
    Args:
        id_company: ID de la compañía
        id_media_file: ID del archivo multimedia
        
    Returns:
        Path: Ruta física completa del archivo
        
    Raises:
        ValueError: Si el archivo no existe o no pertenece a la compañía
        Exception: Si hay error en la base de datos
    """
    try:
        # Preparar JSON para consultar el archivo
        sp_json = {
            "idCompany": id_company,
            "idMediaFile": id_media_file
        }
        
        logger.info(f"Consultando ruta de archivo multimedia {id_media_file}")
        
        # Ejecutar stored procedure para obtener información del archivo
        result = await execute_sp("spMediaFileGetOne", sp_json)
        
        if not result or not result.get('nameMediaFile'):
            raise ValueError(f"Archivo multimedia {id_media_file} no encontrado")
        
        # Construir ruta completa
        media_dir = get_media_base_dir()
        filename = result['nameMediaFile']
        
        # Limpiar prefijo "uploads/" si viene de BD
        if filename.startswith('uploads/'):
            filename = filename.replace('uploads/', '', 1)
        
        file_path = media_dir / filename
        
        logger.info(f"Ruta del archivo: {file_path}")
        return file_path
        
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error al obtener ruta del archivo multimedia: {str(e)}")
        raise
