"""
Modelos Pydantic para cuentas contables.
Define las estructuras de datos para requests y responses de cuentas contables.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class AccountingAccount(BaseModel):
    """
    Modelo que representa una cuenta contable individual.
    """
    
    idAccountingAccount: int = Field(
        description="ID único de la cuenta contable",
        examples=[1, 2, 100]
    )
    
    codeAccountingAccount: str = Field(
        description="Código de la cuenta contable",
        max_length=50,
        examples=["1001", "2001", "4001"]
    )
    
    nameAccountingAccount: str = Field(
        description="Nombre descriptivo de la cuenta contable",
        max_length=255,
        examples=["Efectivo en Caja", "Cuentas por Cobrar", "Ingresos por Ventas"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idAccountingAccount": 1,
                "codeAccountingAccount": "1001",
                "nameAccountingAccount": "Efectivo en Caja"
            }
        }


class AccountingAccountRequest(BaseModel):
    """
    Modelo para request de obtención de cuentas contables paginadas.
    Corresponde al parámetro JSON del stored procedure spAccountingAccount.
    """
    
    search: Optional[str] = Field(
        default=None,
        description="Término de búsqueda para filtrar por nombre de cuenta",
        max_length=50,
        examples=["efectivo", "caja", "ventas"]
    )
    
    sort: Optional[Literal[
        "idAccountingAccount_asc",
        "codeAccountingAccount_asc", 
        "codeAccountingAccount_desc",
        "nameAccountingAccount_asc",
        "nameAccountingAccount_desc"
    ]] = Field(
        default="codeAccountingAccount_asc",
        description="Campo y dirección de ordenamiento"
    )
    
    page: Optional[int] = Field(
        default=1,
        ge=1,
        description="Número de página (inicia en 1)",
        examples=[1, 2, 5]
    )
    
    itemPerPage: Optional[int] = Field(
        default=10,
        ge=1,
        le=100,
        description="Número de elementos por página (máximo 100)",
        examples=[10, 25, 50]
    )
    
    noQuery: Optional[bool] = Field(
        default=False,
        description="Si es True, no ejecuta la consulta (solo para pruebas)"
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "search": "caja",
                "sort": "nameAccountingAccount_asc",
                "page": 1,
                "itemPerPage": 20
            }
        }


class AccountingAccountResponse(BaseModel):
    """
    Modelo de respuesta para cuentas contables paginadas.
    Corresponde a la estructura JSON devuelta por el stored procedure.
    """
    
    total: int = Field(
        description="Total de registros que coinciden con el filtro",
        examples=[0, 50, 250]
    )
    
    data: List[AccountingAccount] = Field(
        description="Lista de cuentas contables para la página actual",
        examples=[[
            {
                "idAccountingAccount": 1,
                "codeAccountingAccount": "1001",
                "nameAccountingAccount": "Efectivo en Caja"
            },
            {
                "idAccountingAccount": 2,
                "codeAccountingAccount": "1002", 
                "nameAccountingAccount": "Banco Cuenta Corriente"
            }
        ]]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "total": 2,
                "data": [
                    {
                        "idAccountingAccount": 1,
                        "codeAccountingAccount": "1001",
                        "nameAccountingAccount": "Efectivo en Caja"
                    },
                    {
                        "idAccountingAccount": 2,
                        "codeAccountingAccount": "1002",
                        "nameAccountingAccount": "Banco Cuenta Corriente"
                    }
                ]
            }
        }


class AccountingAccountErrorResponse(BaseModel):
    """
    Modelo de respuesta para errores en endpoints de cuentas contables.
    """
    
    detail: str = Field(
        description="Descripción detallada del error",
        examples=["Error de base de datos", "Parámetros inválidos"]
    )
    
    error_code: Optional[str] = Field(
        default=None,
        description="Código de error específico para manejo programático",
        examples=["DB_CONNECTION_ERROR", "INVALID_PARAMETERS"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "detail": "Error al conectar con la base de datos",
                "error_code": "DB_CONNECTION_ERROR"
            }
        }
