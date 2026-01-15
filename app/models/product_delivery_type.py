"""
Modelos Pydantic para tipos de entrega de productos.
Define las estructuras de datos para requests y responses de tipos de entrega asociados a productos.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal


class DeliveryTypeItem(BaseModel):
    """
    Modelo que representa un tipo de entrega asociado a un producto.
    """
    
    idDeliveryType: int = Field(
        description="ID del tipo de entrega",
        gt=0,
        examples=[1, 2, 3]
    )
    
    active: bool = Field(
        description="Indica si el tipo de entrega está activo para este producto",
        examples=[True, False]
    )
    
    price: Decimal = Field(
        description="Precio asociado al tipo de entrega",
        ge=0,
        decimal_places=4,
        examples=[13.1313, 68.6868, 0.0000]
    )
    
    idProductDeliveryType: int = Field(
        description="ID de la relación producto-tipo de entrega",
        gt=0,
        examples=[67, 68, 100]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idDeliveryType": 1,
                "active": True,
                "price": 13.1313,
                "idProductDeliveryType": 67
            }
        }


class ProductDeliveryTypeUpdateRequest(BaseModel):
    """
    Modelo para request de actualización de tipos de entrega de producto.
    """
    
    deliveryType: List[DeliveryTypeItem] = Field(
        description="Lista de tipos de entrega con sus configuraciones",
        min_length=1
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "deliveryType": [
                    {
                        "idDeliveryType": 1,
                        "active": True,
                        "price": 13.1313,
                        "idProductDeliveryType": 67
                    },
                    {
                        "idDeliveryType": 2,
                        "active": False,
                        "price": 68.6868,
                        "idProductDeliveryType": 68
                    }
                ]
            }
        }


class ProductDeliveryTypeResponse(BaseModel):
    """
    Modelo para response de actualización de tipos de entrega de producto.
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
