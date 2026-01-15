"""
Endpoints para gestión de archivos multimedia.
Proporciona funcionalidad CRUD para archivos multimedia independientes.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Path, File, UploadFile, Query
from fastapi.responses import FileResponse
from pathlib import Path as PathLib
from typing import Optional
from app.utils.auth import get_current_user
from app.models.auth import CurrentUser
from app.models.media_file import (
    MediaFileCreateResponse,
    MediaFileDeleteResponse,
    MediaFileListResponse,
    MediaFileTotalResponse
)
from app.services.media_file_service import (
    create_media_file,
    delete_media_file_service,
    get_media_file_path,
    get_media_files,
    get_media_files_total
)
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de archivos multimedia
router = APIRouter(prefix="/media-file", tags=["Archivos Multimedia"])


@router.get(
    "/total.json",
    response_model=MediaFileTotalResponse,
    summary="Obtener totales de archivos multimedia",
    description="""Obtiene estadísticas y totales de archivos multimedia.
    
    Este endpoint proporciona información agregada sobre los archivos multimedia:
    
    **Características:**
    - Total general de archivos y tamaño
    - Totales agrupados por tipo de medio (image, video, audio, document)
    - Totales agrupados por año de creación
    - Solo archivos de la compañía autenticada
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Respuesta exitosa (200):**
    ```json
    {
        "quantity": 50,
        "totalSize": 10485760,
        "mediaType": [
            {
                "mediaType": "image",
                "quantity": 30,
                "totalSize": 6291456
            },
            {
                "mediaType": "document",
                "quantity": 20,
                "totalSize": 4194304
            }
        ],
        "byYear": [
            {
                "year": 2026,
                "quantity": 15,
                "totalSize": 3145728
            },
            {
                "year": 2025,
                "quantity": 25,
                "totalSize": 5242880
            }
        ]
    }
    ```
    
    **Errores posibles:**
    - **401**: Token inválido o expirado
    - **500**: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Totales de archivos multimedia",
            "content": {
                "application/json": {
                    "example": {
                        "quantity": 50,
                        "totalSize": 10485760,
                        "mediaType": [
                            {
                                "mediaType": "image",
                                "quantity": 30,
                                "totalSize": 6291456
                            },
                            {
                                "mediaType": "document",
                                "quantity": 20,
                                "totalSize": 4194304
                            }
                        ],
                        "byYear": [
                            {
                                "year": 2026,
                                "quantity": 15,
                                "totalSize": 3145728
                            },
                            {
                                "year": 2025,
                                "quantity": 25,
                                "totalSize": 5242880
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "No autorizado - Token inválido o expirado"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def get_totals(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene totales de archivos multimedia agrupados por tipo y año.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Obtener totales
        result = await get_media_files_total(id_company=id_company)
        
        return result
        
    except Exception as e:
        logger.error(f"Error al obtener totales de archivos multimedia: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener totales de archivos multimedia: {str(e)}"
        )


@router.get(
    ".json",
    response_model=MediaFileListResponse,
    summary="Listar archivos multimedia",
    description="""Obtiene lista de archivos multimedia con paginación y filtros.
    
    Este endpoint permite consultar archivos multimedia registrados:
    
    **Características:**
    - Paginación de resultados
    - Búsqueda por nombre o mimetype
    - Filtrado por tipo de medio
    - Ordenamiento personalizable
    - Solo archivos de la compañía autenticada
    
    **Query Parameters:**
    - **search** (opcional): Texto a buscar en nombre o mimetype
    - **sort** (opcional): Campo y dirección de ordenamiento (default: createAt_desc)
      - Valores válidos: idMediaFile_asc, idMediaFile_desc, nameMediaFile_asc, 
        nameMediaFile_desc, createAt_asc, createAt_desc
    - **page** (opcional): Número de página (default: 1)
    - **itemPerPage** (opcional): Elementos por página (default: 10)
    - **mediaType** (opcional): Filtro por tipo (image, video, audio, document)
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Respuesta exitosa (200):**
    ```json
    {
        "total": 2,
        "data": [
            {
                "idMediaFile": 1,
                "nameMediaFile": "1_20260115123456.jpg",
                "pathMediaFile": "uploads/1_20260115123456.jpg",
                "sizeMediaFile": 1048576,
                "mimetype": "image/jpeg",
                "mediaType": "image",
                "createAt": "2026-01-15T12:34:56"
            }
        ]
    }
    ```
    
    **Errores posibles:**
    - **401**: Token inválido o expirado
    - **500**: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Lista de archivos multimedia",
            "content": {
                "application/json": {
                    "example": {
                        "total": 2,
                        "data": [
                            {
                                "idMediaFile": 1,
                                "nameMediaFile": "1_20260115123456.jpg",
                                "pathMediaFile": "uploads/1_20260115123456.jpg",
                                "sizeMediaFile": 1048576,
                                "mimetype": "image/jpeg",
                                "mediaType": "image",
                                "createAt": "2026-01-15T12:34:56"
                            },
                            {
                                "idMediaFile": 2,
                                "nameMediaFile": "2_20260115123500.pdf",
                                "pathMediaFile": "uploads/2_20260115123500.pdf",
                                "sizeMediaFile": 2097152,
                                "mimetype": "application/pdf",
                                "mediaType": "document",
                                "createAt": "2026-01-15T12:35:00"
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "No autorizado - Token inválido o expirado"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def list_files(
    search: Optional[str] = Query(
        None,
        description="Texto a buscar en nombre o mimetype",
        example="jpg"
    ),
    sort: str = Query(
        "createAt_desc",
        description="Campo y dirección de ordenamiento",
        pattern="^(idMediaFile|nameMediaFile|createAt)_(asc|desc)$",
        example="createAt_desc"
    ),
    page: int = Query(
        1,
        description="Número de página",
        ge=1,
        example=1
    ),
    itemPerPage: int = Query(
        10,
        description="Elementos por página",
        ge=1,
        le=100,
        example=10
    ),
    mediaType: Optional[str] = Query(
        None,
        description="Filtro por tipo de medio",
        pattern="^(image|video|audio|document)$",
        example="image"
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene lista de archivos multimedia con paginación.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Obtener archivos multimedia
        result = await get_media_files(
            id_company=id_company,
            search=search,
            sort=sort,
            page=page,
            item_per_page=itemPerPage,
            media_type=mediaType
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error al obtener archivos multimedia: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener archivos multimedia: {str(e)}"
        )


@router.post(
    "/",
    response_model=MediaFileCreateResponse,
    summary="Subir archivo multimedia",
    description="""Sube un archivo multimedia al sistema.
    
    Este endpoint permite subir un archivo y registrarlo en la base de datos:
    
    **Características:**
    - Acepta cualquier tipo de archivo (imagen, video, audio, documento)
    - Extrae automáticamente mimetype, extensión y tamaño
    - Genera nombre único con timestamp
    - Guarda el archivo físicamente en mediaFile/
    - Crea registro en base de datos
    - Asocia el archivo a la compañía
    
    **Form Data:**
    - **file**: Archivo a subir (multipart/form-data)
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Respuesta exitosa (200):**
    ```json
    {
        "idMediaFile": 1,
        "nameMediaFile": "1_20260115123456.jpg",
        "pathMediaFile": "uploads/1_20260115123456.jpg",
        "urlMediaFile": "https://img.ezekl.com/1_20260115123456.jpg"
    }
    ```
    
    **Errores posibles:**
    - **401**: Token inválido o expirado
    - **500**: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Archivo multimedia subido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "idMediaFile": 1,
                        "nameMediaFile": "1_20260115123456.jpg",
                        "pathMediaFile": "uploads/1_20260115123456.jpg",
                        "urlMediaFile": "https://img.ezekl.com/1_20260115123456.jpg"
                    }
                }
            }
        },
        401: {
            "description": "No autorizado - Token inválido o expirado"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def upload_file(
    file: UploadFile = File(..., description="Archivo a subir"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Sube un archivo multimedia al sistema.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Validar que se recibió un archivo
        if not file:
            raise HTTPException(status_code=400, detail="No se recibió ningún archivo")
        
        # Crear archivo multimedia
        result = await create_media_file(
            id_company=id_company,
            file=file
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error al subir archivo multimedia: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir archivo multimedia: {str(e)}"
        )


@router.get(
    "/{idMediaFile}",
    summary="Obtener archivo multimedia",
    description="""Obtiene y sirve un archivo multimedia específico.
    
    Este endpoint permite acceder a archivos multimedia almacenados:
    
    **Características:**
    - Requiere autenticación válida
    - Valida pertenencia del archivo a la compañía
    - Sirve el archivo físico directamente
    - Detecta automáticamente el tipo de contenido
    - Utilizado por stored procedures para generar URLs
    
    **Parámetros:**
    - **idMediaFile** (path): ID del archivo multimedia a obtener
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Respuesta exitosa (200):**
    - Archivo multimedia (imagen, video, audio, documento)
    - Content-Type según el tipo de archivo
    
    **Errores posibles:**
    - **401**: Token inválido o expirado
    - **404**: Archivo no encontrado o no pertenece a la compañía
    - **500**: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Archivo multimedia",
            "content": {
                "image/*": {},
                "video/*": {},
                "audio/*": {},
                "application/*": {}
            }
        },
        401: {
            "description": "No autorizado - Token inválido o expirado"
        },
        404: {
            "description": "Archivo no encontrado"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def get_file(
    idMediaFile: int = Path(
        ...,
        description="ID del archivo multimedia a obtener",
        gt=0,
        example=1
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene y sirve un archivo multimedia específico.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Obtener ruta del archivo desde el servicio
        file_path = await get_media_file_path(
            id_company=id_company,
            id_media_file=idMediaFile
        )
        
        # Verificar que el archivo existe
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Archivo físico no encontrado"
            )
        
        # Servir el archivo
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type="application/octet-stream"
        )
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener archivo multimedia: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener archivo multimedia: {str(e)}"
        )


@router.delete(
    "/{idMediaFile}",
    response_model=MediaFileDeleteResponse,
    summary="Eliminar archivo multimedia",
    description="""Elimina un archivo multimedia del sistema.
    
    Este endpoint permite eliminar un archivo multimedia:
    
    **Características:**
    - Elimina registro del archivo multimedia de la base de datos
    - Elimina asociaciones con la compañía (cascada)
    - Elimina archivo físico del servidor
    - Valida pertenencia del archivo a la compañía
    
    **Parámetros:**
    - **idMediaFile** (path): ID del archivo multimedia a eliminar
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Respuesta exitosa (200):**
    ```json
    {
        "idMediaFile": 1
    }
    ```
    
    **Errores posibles:**
    - **401**: Token inválido o expirado
    - **404**: Archivo multimedia no encontrado o no pertenece a la compañía
    - **500**: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Archivo multimedia eliminado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "idMediaFile": 1
                    }
                }
            }
        },
        401: {
            "description": "No autorizado - Token inválido o expirado"
        },
        404: {
            "description": "Archivo multimedia no encontrado"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def delete_file(
    idMediaFile: int = Path(
        ...,
        description="ID del archivo multimedia a eliminar",
        gt=0,
        example=1
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Elimina un archivo multimedia específico.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Eliminar archivo multimedia
        result = await delete_media_file_service(
            id_company=id_company,
            id_media_file=idMediaFile
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al eliminar archivo multimedia: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar archivo multimedia: {str(e)}"
        )
