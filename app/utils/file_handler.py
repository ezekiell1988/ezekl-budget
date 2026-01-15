"""
Utilidades para manejo de archivos multimedia.
Funciones para procesar, guardar y eliminar archivos físicos.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)


def get_media_base_dir() -> Path:
    """Obtiene el directorio base para archivos multimedia desde settings."""
    # Si es ruta absoluta, usarla directamente
    media_dir = Path(settings.media_file_base_dir)
    if media_dir.is_absolute():
        return media_dir
    
    # Si es ruta relativa, usar desde el directorio del proyecto
    project_root = Path(__file__).parent.parent.parent
    return project_root / settings.media_file_base_dir


def ensure_media_directory_exists() -> None:
    """
    Verifica que el directorio de archivos multimedia existe.
    Si no existe, lo crea.
    """
    try:
        media_dir = get_media_base_dir()
        if not media_dir.exists():
            media_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio de medios creado: {media_dir}")
        else:
            logger.debug(f"Directorio de medios existe: {media_dir}")
    except Exception as e:
        logger.error(f"Error al crear directorio de medios: {str(e)}")
        raise


def get_file_info(file: UploadFile) -> dict:
    """
    Extrae información del archivo subido.
    
    Args:
        file: Archivo subido por el usuario
        
    Returns:
        Diccionario con información del archivo (mimetype, extension, mediaType)
    """
    # Obtener extensión del nombre del archivo
    filename = file.filename or ""
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ""
    
    # Determinar tipo de media basado en mimetype
    mimetype = file.content_type or "application/octet-stream"
    
    media_type = "other"
    if mimetype.startswith("image/"):
        media_type = "image"
    elif mimetype.startswith("video/"):
        media_type = "video"
    elif mimetype.startswith("audio/"):
        media_type = "audio"
    elif mimetype.startswith("application/pdf"):
        media_type = "document"
    
    return {
        "mimetype": mimetype,
        "extension": extension,
        "mediaType": media_type
    }


async def save_media_file(file: UploadFile, filename_from_db: str) -> str:
    """
    Guarda el archivo físicamente en el directorio de medios.
    
    Args:
        file: Archivo subido por el usuario
        filename_from_db: Nombre del archivo retornado por la base de datos
        
    Returns:
        Ruta completa donde se guardó el archivo
        
    Raises:
        Exception: Si hay error al guardar el archivo
    """
    try:
        # Asegurar que el directorio existe
        ensure_media_directory_exists()
        
        # Construir ruta completa del archivo
        media_dir = get_media_base_dir()
        file_path = media_dir / filename_from_db
        
        # Guardar el archivo
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Archivo guardado: {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Error al guardar archivo {filename_from_db}: {str(e)}")
        raise


def delete_media_file(filename: str) -> bool:
    """
    Elimina un archivo físico del directorio de medios.
    
    Args:
        filename: Nombre del archivo a eliminar (puede incluir subcarpetas)
        
    Returns:
        True si se eliminó exitosamente, False si no existía
        
    Raises:
        Exception: Si hay error al eliminar el archivo
    """
    try:
        # Construir ruta completa del archivo
        # El filename puede venir como "uploads/1_20260115123456.jpg"
        # Extraer solo el nombre del archivo
        file_basename = filename.split('/')[-1] if '/' in filename else filename
        media_dir = get_media_base_dir()
        file_path = media_dir / file_basename
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Archivo eliminado: {file_path}")
            return True
        else:
            logger.warning(f"Archivo no existe para eliminar: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error al eliminar archivo {filename}: {str(e)}")
        raise


async def get_file_size(file: UploadFile) -> int:
    """
    Obtiene el tamaño del archivo en bytes.
    
    Args:
        file: Archivo subido por el usuario
        
    Returns:
        Tamaño del archivo en bytes
    """
    try:
        # Leer el contenido para obtener el tamaño
        content = await file.read()
        size = len(content)
        
        # Resetear el puntero del archivo para poder leerlo nuevamente
        await file.seek(0)
        
        return size
    except Exception as e:
        logger.error(f"Error al obtener tamaño del archivo: {str(e)}")
        raise
