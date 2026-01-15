"""
Modelos Pydantic para configuración de productos.
Define las estructuras de datos para requests y responses de configuración de productos.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ProductConfigurationUpdateRequest(BaseModel):
    """
    Modelo para request de actualización de configuración de producto.
    """
    
    isMainCategory: Optional[bool] = Field(
        default=None,
        description="Indica si el producto es una categoría principal",
        examples=[True, False]
    )
    
    isCategory: Optional[bool] = Field(
        default=None,
        description="Indica si el producto es una categoría",
        examples=[True, False]
    )
    
    isProduct: Optional[bool] = Field(
        default=None,
        description="Indica si es un producto",
        examples=[True, False]
    )
    
    isIngredient: Optional[bool] = Field(
        default=None,
        description="Indica si es un ingrediente",
        examples=[True, False]
    )
    
    isAdditional: Optional[bool] = Field(
        default=None,
        description="Indica si es un adicional",
        examples=[True, False]
    )
    
    isCombo: Optional[bool] = Field(
        default=None,
        description="Indica si es un combo",
        examples=[True, False]
    )
    
    isUniqueSelection: Optional[bool] = Field(
        default=None,
        description="Indica si requiere selección única",
        examples=[True, False]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "isMainCategory": False,
                "isCategory": True,
                "isProduct": False,
                "isIngredient": False,
                "isAdditional": False,
                "isCombo": False,
                "isUniqueSelection": False
            }
        }


class ProductConfigurationResponse(BaseModel):
    """
    Modelo para response de actualización de configuración de producto.
    """
    
    idProduct: int = Field(
        description="ID del producto actualizado",
        examples=[1, 2, 100]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idProduct": 34
            }
        }
