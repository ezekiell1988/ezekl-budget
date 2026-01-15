"""
Modelos Pydantic para archivos multimedia de productos.
Define las estructuras de datos para responses de archivos multimedia asociados a productos.
"""

from pydantic import BaseModel, Field
from typing import List


class MediaFileResult(BaseModel):
    """
    Modelo que representa el resultado de un archivo multimedia creado.
    """
    
    idProductMediaFile: int = Field(
        description="ID de la relación producto-archivo",
        examples=[1, 2, 100]
    )
    
    idMediaFile: int = Field(
        description="ID del archivo multimedia",
        examples=[1, 2, 100]
    )
    
    nameMediaFile: str = Field(
        description="Nombre del archivo generado",
        examples=["1_20260115123456.jpg"]
    )
    
    pathMediaFile: str = Field(
        description="Ruta del archivo en el servidor",
        examples=["uploads/1_20260115123456.jpg"]
    )
    
    urlMediaFile: str = Field(
        description="URL pública del archivo",
        examples=["https://img.ezekl.com/1_20260115123456.jpg"]
    )


class ProductMediaFileAddResponse(BaseModel):
    """
    Modelo para response de agregar archivos multimedia a producto.
    """
    
    idProductMediaFile: int = Field(
        description="ID de la última relación producto-archivo creada",
        examples=[1, 2, 100]
    )
    
    mediaFiles: List[MediaFileResult] = Field(
        description="Lista de archivos multimedia creados"
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
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


class MediaFileDeleteResult(BaseModel):
    """
    Modelo que representa el resultado de un archivo multimedia eliminado.
    """
    
    idMediaFile: int = Field(
        description="ID del archivo multimedia eliminado",
        examples=[1, 2, 100]
    )
    
    idProductMediaFile: int = Field(
        description="ID de la relación producto-archivo eliminada",
        examples=[1, 2, 100]
    )


class ProductMediaFileDeleteRequest(BaseModel):
    """
    Modelo para request de eliminar archivos multimedia de un producto.
    """
    
    idMediaFiles: List[int] = Field(
        description="Lista de IDs de archivos multimedia a eliminar",
        min_length=1
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idMediaFiles": [1, 2]
            }
        }


class ProductMediaFileDeleteResponse(BaseModel):
    """
    Modelo para response de eliminar archivos multimedia de producto.
    """
    
    mediaFiles: List[MediaFileDeleteResult] = Field(
        description="Lista de archivos multimedia eliminados"
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "mediaFiles": [
                    {
                        "idMediaFile": 1,
                        "idProductMediaFile": 1
                    }
                ]
            }
        }
