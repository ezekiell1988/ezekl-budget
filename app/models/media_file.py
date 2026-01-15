"""
Modelos Pydantic para archivos multimedia.
Define las estructuras de datos para responses de archivos multimedia independientes.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MediaFile(BaseModel):
    """
    Modelo que representa un archivo multimedia individual.
    """
    
    idMediaFile: int = Field(
        description="ID único del archivo multimedia",
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
    
    sizeMediaFile: int = Field(
        description="Tamaño del archivo en bytes",
        examples=[1024, 2048, 1048576]
    )
    
    mimetype: str = Field(
        description="MIME type del archivo",
        examples=["image/jpeg", "video/mp4", "application/pdf"]
    )
    
    mediaType: str = Field(
        description="Tipo general del archivo (image, video, audio, document)",
        examples=["image", "video", "audio", "document"]
    )
    
    createAt: datetime = Field(
        description="Fecha y hora de creación del archivo",
        examples=["2026-01-15T12:34:56"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idMediaFile": 1,
                "nameMediaFile": "1_20260115123456.jpg",
                "pathMediaFile": "uploads/1_20260115123456.jpg",
                "sizeMediaFile": 1048576,
                "mimetype": "image/jpeg",
                "mediaType": "image",
                "createAt": "2026-01-15T12:34:56"
            }
        }


class MediaFileListResponse(BaseModel):
    """
    Modelo para response de listado de archivos multimedia.
    """
    
    total: int = Field(
        description="Número total de archivos multimedia",
        examples=[10, 50, 100]
    )
    
    data: List[MediaFile] = Field(
        description="Lista de archivos multimedia",
        default=[]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
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


class MediaFileCreateResponse(BaseModel):
    """
    Modelo para response de creación de archivo multimedia.
    """
    
    idMediaFile: int = Field(
        description="ID del archivo multimedia creado",
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

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idMediaFile": 1,
                "nameMediaFile": "1_20260115123456.jpg",
                "pathMediaFile": "uploads/1_20260115123456.jpg",
                "urlMediaFile": "https://img.ezekl.com/1_20260115123456.jpg"
            }
        }


class MediaFileDeleteResponse(BaseModel):
    """
    Modelo para response de eliminación de archivo multimedia.
    """
    
    idMediaFile: int = Field(
        description="ID del archivo multimedia eliminado",
        examples=[1, 2, 100]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idMediaFile": 1
            }
        }


class MediaTypeTotal(BaseModel):
    """
    Modelo para totales por tipo de medio.
    """
    
    mediaType: str = Field(
        description="Tipo de medio",
        examples=["image", "video", "audio", "document"]
    )
    
    quantity: int = Field(
        description="Cantidad de archivos de este tipo",
        examples=[10, 25, 100]
    )
    
    totalSize: int = Field(
        description="Tamaño total en bytes de este tipo",
        examples=[1048576, 10485760]
    )


class YearTotal(BaseModel):
    """
    Modelo para totales por año.
    """
    
    year: int = Field(
        description="Año",
        examples=[2024, 2025, 2026]
    )
    
    quantity: int = Field(
        description="Cantidad de archivos en este año",
        examples=[10, 25, 100]
    )
    
    totalSize: int = Field(
        description="Tamaño total en bytes en este año",
        examples=[1048576, 10485760]
    )


class MediaFileTotalResponse(BaseModel):
    """
    Modelo para response de totales de archivos multimedia.
    """
    
    quantity: int = Field(
        description="Cantidad total de archivos",
        examples=[50, 100, 500]
    )
    
    totalSize: int = Field(
        description="Tamaño total en bytes",
        examples=[10485760, 104857600]
    )
    
    mediaType: List[MediaTypeTotal] = Field(
        description="Totales agrupados por tipo de medio",
        default=[]
    )
    
    byYear: List[YearTotal] = Field(
        description="Totales agrupados por año",
        default=[]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
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
                    },
                    {
                        "year": 2024,
                        "quantity": 10,
                        "totalSize": 2097152
                    }
                ]
            }
        }

