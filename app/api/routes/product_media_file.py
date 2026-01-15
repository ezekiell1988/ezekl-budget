"""
Endpoints para gestión de archivos multimedia de productos.
Proporciona funcionalidad para agregar y eliminar archivos multimedia asociados a productos.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Path, File, UploadFile
from typing import List
from app.utils.auth import get_current_user
from app.models.auth import CurrentUser
from app.models.product_media_file import (
    ProductMediaFileAddResponse,
    ProductMediaFileDeleteRequest,
    ProductMediaFileDeleteResponse
)
from app.services.product_media_file_service import (
    add_single_product_media_file,
    add_product_media_files,
    delete_product_media_files
)
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de archivos multimedia de productos
router = APIRouter(prefix="/product-media-file", tags=["Archivos Multimedia de Productos"])


@router.post(
    "/{idProduct}",
    response_model=ProductMediaFileAddResponse,
    summary="Subir un archivo multimedia a producto",
    description="""Sube un archivo multimedia y lo asocia a un producto específico.
    
    Este endpoint permite subir un archivo y asociarlo a un producto:
    
    **Características:**
    - Acepta un archivo (imagen, video, audio, documento)
    - Extrae automáticamente mimetype, extensión y tamaño
    - Genera nombre único con timestamp
    - Guarda el archivo físicamente en mediaFile/
    - Asigna prioridad automática al archivo
    - Valida pertenencia del producto a la compañía
    - Retorna URL pública para acceder al archivo
    
    **Parámetros:**
    - **idProduct** (path): ID del producto al que se asociará el archivo
    
    **Form Data:**
    - **file**: Archivo a subir (multipart/form-data)
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Respuesta exitosa (200):**
    ```json
    {
        "idProductMediaFile": 1,
        "mediaFiles": [
            {
                "idProductMediaFile": 1,
                "idMediaFile": 1,
                "nameMediaFile": "1_20260115123456.jpg",
                "pathMediaFile": "uploads/1_20260115123456.jpg",
                "urlMediaFile": "https://img.ezekl.com/1_20260115123456.jpg"
            }
        ]
    }
    ```
    
    **Errores posibles:**
    - **401**: Token inválido o expirado
    - **404**: Producto no encontrado o no pertenece a la compañía
    - **500**: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Archivo multimedia subido y asociado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "idProductMediaFile": 1,
                        "mediaFiles": [
                            {
                                "idProductMediaFile": 1,
                                "idMediaFile": 1,
                                "nameMediaFile": "1_20260115123456.jpg",
                                "pathMediaFile": "uploads/1_20260115123456.jpg",
                                "urlMediaFile": "https://img.ezekl.com/1_20260115123456.jpg"
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "No autorizado - Token inválido o expirado"
        },
        404: {
            "description": "Producto no encontrado"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def upload_single_file(
    idProduct: int = Path(
        ...,
        description="ID del producto al que se asociará el archivo",
        gt=0,
        example=1
    ),
    file: UploadFile = File(..., description="Archivo a subir"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Sube un archivo multimedia y lo asocia a un producto específico.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Validar que se recibió un archivo
        if not file:
            raise HTTPException(status_code=400, detail="No se recibió ningún archivo")
        
        # Agregar archivo multimedia
        result = await add_single_product_media_file(
            id_product=idProduct,
            id_company=id_company,
            file=file
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al subir archivo multimedia: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir archivo multimedia al producto: {str(e)}"
        )


@router.post(
    "/{idProduct}/multiple",
    response_model=ProductMediaFileAddResponse,
    summary="Subir múltiples archivos multimedia a producto",
    description="""Sube varios archivos multimedia y los asocia a un producto específico.
    
    Este endpoint permite subir múltiples archivos de una vez:
    
    **Características:**
    - Acepta múltiples archivos en una sola petición
    - Procesa cada archivo individualmente
    - Extrae automáticamente mimetype, extensión y tamaño de cada uno
    - Genera nombres únicos con timestamp
    - Guarda los archivos físicamente en mediaFile/
    - Asigna prioridad automática a cada archivo
    - Valida pertenencia del producto a la compañía
    - Retorna URLs públicas para todos los archivos
    
    **Parámetros:**
    - **idProduct** (path): ID del producto al que se asociarán los archivos
    
    **Form Data:**
    - **files**: Lista de archivos a subir (multipart/form-data)
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Respuesta exitosa (200):**
    ```json
    {
        "idProductMediaFile": 2,
        "mediaFiles": [
            {
                "idProductMediaFile": 1,
                "idMediaFile": 1,
                "nameMediaFile": "1_20260115123456.jpg",
                "pathMediaFile": "uploads/1_20260115123456.jpg",
                "urlMediaFile": "https://img.ezekl.com/1_20260115123456.jpg"
            },
            {
                "idProductMediaFile": 2,
                "idMediaFile": 2,
                "nameMediaFile": "2_20260115123457.png",
                "pathMediaFile": "uploads/2_20260115123457.png",
                "urlMediaFile": "https://img.ezekl.com/2_20260115123457.png"
            }
        ]
    }
    ```
    
    **Errores posibles:**
    - **401**: Token inválido o expirado
    - **404**: Producto no encontrado o no pertenece a la compañía
    - **500**: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Archivos multimedia subidos y asociados exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "idProductMediaFile": 2,
                        "mediaFiles": [
                            {
                                "idProductMediaFile": 1,
                                "idMediaFile": 1,
                                "nameMediaFile": "1_20260115123456.jpg",
                                "pathMediaFile": "uploads/1_20260115123456.jpg",
                                "urlMediaFile": "https://img.ezekl.com/1_20260115123456.jpg"
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "No autorizado - Token inválido o expirado"
        },
        404: {
            "description": "Producto no encontrado"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def upload_multiple_files(
    idProduct: int = Path(
        ...,
        description="ID del producto al que se asociarán los archivos",
        gt=0,
        example=1
    ),
    files: List[UploadFile] = File(..., description="Lista de archivos a subir"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Sube múltiples archivos multimedia y los asocia a un producto específico.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Validar que se recibieron archivos
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="No se recibieron archivos")
        
        # Agregar archivos multimedia
        result = await add_product_media_files(
            id_product=idProduct,
            id_company=id_company,
            files=files
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al subir archivos multimedia: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir archivos multimedia al producto: {str(e)}"
        )


@router.delete(
    "/{idProduct}",
    response_model=ProductMediaFileDeleteResponse,
    summary="Eliminar archivos multimedia de producto",
    description="""Elimina uno o más archivos multimedia de un producto específico.
    
    Este endpoint permite eliminar archivos multimedia asociados a un producto:
    
    **Características:**
    - Elimina registros de archivos multimedia de la base de datos
    - Elimina relaciones producto-archivo
    - Elimina archivos físicos del servidor
    - Valida pertenencia del producto a la compañía
    - Solo elimina archivos físicos si no están siendo usados por otros productos
    
    **Parámetros:**
    - **idProduct** (path): ID del producto del que se eliminarán los archivos
    
    **Body:**
    - **idMediaFiles**: Array de IDs de archivos multimedia a eliminar
    
    **Validaciones:**
    - El producto debe existir y pertenecer a la compañía
    - Debe enviarse al menos un ID de archivo
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Respuesta exitosa (200):**
    ```json
    {
        "mediaFiles": [
            {
                "idMediaFile": 1,
                "idProductMediaFile": 1,
                "pathMediaFile": "uploads/1_20260115123456.jpg"
            }
        ]
    }
    ```
    
    **Errores posibles:**
    - **401**: Token inválido o expirado
    - **404**: Producto no encontrado o no pertenece a la compañía
    - **500**: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Archivos multimedia eliminados exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "mediaFiles": [
                            {
                                "idMediaFile": 1,
                                "idProductMediaFile": 1,
                                "pathMediaFile": "uploads/1_20260115123456.jpg"
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "No autorizado - Token inválido o expirado"
        },
        404: {
            "description": "Producto no encontrado"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def delete_media_files(
    idProduct: int = Path(
        ...,
        description="ID del producto del que se eliminarán los archivos",
        gt=0,
        example=1
    ),
    request: ProductMediaFileDeleteRequest = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Elimina archivos multimedia de un producto específico.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Eliminar archivos multimedia
        result = await delete_product_media_files(
            id_product=idProduct,
            id_company=id_company,
            id_media_files=request.idMediaFiles
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al eliminar archivos multimedia: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar archivos multimedia del producto: {str(e)}"
        )
