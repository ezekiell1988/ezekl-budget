"""
Modelos Pydantic para archivos multimedia.
Define las estructuras de datos para responses de archivos multimedia independientes.
"""

from pydantic import BaseModel, Field


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
