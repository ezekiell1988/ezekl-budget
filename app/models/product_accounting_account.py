"""
Modelos Pydantic para cuentas contables de productos.
Define las estructuras de datos para requests y responses de cuentas contables asociadas a productos.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from decimal import Decimal


class AccountingAccountItem(BaseModel):
    """
    Modelo que representa una cuenta contable asociada a un producto.
    """
    
    idAccountingAccount: int = Field(
        description="ID de la cuenta contable",
        gt=0,
        examples=[1, 2, 100]
    )
    
    effect: int = Field(
        description="Efecto de la cuenta (1 para débito, -1 para crédito)",
        examples=[1, -1]
    )
    
    percent: Decimal = Field(
        description="Porcentaje de distribución (debe sumar 100 por cada efecto)",
        ge=0,
        le=100,
        decimal_places=4,
        examples=[50.0000, 100.0000, 33.3333]
    )
    
    idProductAccountingAccount: Optional[int] = Field(
        default=None,
        description="ID de la relación producto-cuenta (null para nuevas relaciones)",
        examples=[1, 2, None]
    )
    
    @field_validator('effect')
    @classmethod
    def validate_effect(cls, v):
        """Valida que effect sea 1 o -1."""
        if v not in [1, -1]:
            raise ValueError('effect debe ser 1 (débito) o -1 (crédito)')
        return v

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idAccountingAccount": 1,
                "effect": 1,
                "percent": 100.0000,
                "idProductAccountingAccount": None
            }
        }


class ProductAccountingAccountUpdateRequest(BaseModel):
    """
    Modelo para request de actualización de cuentas contables de producto.
    """
    
    accountingAccount: List[AccountingAccountItem] = Field(
        description="Lista de cuentas contables con sus configuraciones (mínimo 2 cuentas requeridas)",
        min_length=2
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "accountingAccount": [
                    {
                        "idAccountingAccount": 1,
                        "effect": 1,
                        "percent": 100.0000,
                        "idProductAccountingAccount": 67
                    },
                    {
                        "idAccountingAccount": 2,
                        "effect": -1,
                        "percent": 100.0000,
                        "idProductAccountingAccount": None
                    }
                ]
            }
        }


class ProductAccountingAccountResponse(BaseModel):
    """
    Modelo para response de actualización de cuentas contables de producto.
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
