"""
Modelos Pydantic para productos.
Define las estructuras de datos para requests y responses de productos.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class Product(BaseModel):
    """
    Modelo que representa un producto individual con estructura jerárquica.
    """
    
    idProduct: int = Field(
        description="ID único del producto",
        examples=[1, 2, 100]
    )
    
    nameProduct: str = Field(
        description="Nombre del producto",
        max_length=200,
        examples=["Gastos generales", "Alimentación", "TV"]
    )
    
    descriptionProduct: str = Field(
        description="Descripción del producto",
        max_length=500,
        examples=["Gastos generales (no identificados) en familia", "Alimentación Padres"]
    )
    
    childrens: Optional[List['Product']] = Field(
        default=None,
        description="Lista de productos hijos (estructura jerárquica)"
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idProduct": 1,
                "nameProduct": "Gastos generales",
                "descriptionProduct": "Gastos generales (no identificados) en familia",
                "childrens": [
                    {
                        "idProduct": 2,
                        "nameProduct": "Alimentación",
                        "descriptionProduct": "Alimentación",
                        "childrens": None
                    }
                ]
            }
        }


class ProductCreateRequest(BaseModel):
    """
    Modelo para request de creación de producto.
    """
    
    idProductFather: Optional[int] = Field(
        default=None,
        description="ID del producto padre (null para productos raíz)",
        examples=[1, 2, None]
    )
    
    nameProduct: str = Field(
        description="Nombre del producto",
        max_length=200,
        examples=["Gastos generales", "Alimentación"]
    )
    
    descriptionProduct: str = Field(
        description="Descripción del producto",
        max_length=500,
        examples=["Gastos generales en familia"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idProductFather": None,
                "nameProduct": "Gastos generales",
                "descriptionProduct": "Gastos generales (no identificados) en familia"
            }
        }


class ProductUpdateRequest(BaseModel):
    """
    Modelo para request de actualización de producto.
    """
    
    idProductFather: Optional[int] = Field(
        default=None,
        description="ID del producto padre (opcional para actualización parcial)",
        examples=[1, 2, None]
    )
    
    nameProduct: Optional[str] = Field(
        default=None,
        description="Nombre del producto (opcional para actualización parcial)",
        max_length=200,
        examples=["Gastos generales", "Alimentación"]
    )
    
    descriptionProduct: Optional[str] = Field(
        default=None,
        description="Descripción del producto (opcional para actualización parcial)",
        max_length=500,
        examples=["Gastos generales en familia"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "nameProduct": "Gastos generales actualizado",
                "descriptionProduct": "Nueva descripción"
            }
        }


class ProductCreateResponse(BaseModel):
    """
    Modelo para response de creación exitosa de producto.
    """
    
    idProduct: int = Field(
        description="ID del producto creado",
        examples=[1, 2, 100]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idProduct": 1
            }
        }


class ProductListResponse(BaseModel):
    """
    Modelo para response de listado de productos.
    """
    
    total: int = Field(
        description="Total de productos raíz",
        examples=[10, 25, 100]
    )
    
    data: List[Product] = Field(
        description="Lista de productos con estructura jerárquica"
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "total": 2,
                "data": [
                    {
                        "idProduct": 1,
                        "nameProduct": "Gastos generales",
                        "descriptionProduct": "Gastos generales (no identificados) en familia",
                        "childrens": [
                            {
                                "idProduct": 2,
                                "nameProduct": "Alimentación",
                                "descriptionProduct": "Alimentación",
                                "childrens": None
                            }
                        ]
                    }
                ]
            }
        }


class ProductErrorResponse(BaseModel):
    """
    Modelo para respuestas de error.
    """
    
    detail: str = Field(
        description="Mensaje de error detallado",
        examples=["Producto no encontrado", "Error al crear producto"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "detail": "Producto no encontrado"
            }
        }
