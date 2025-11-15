"""
Modelos Pydantic para cuentas contables.
Define las estructuras de datos para requests y responses de cuentas contables.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union


class AccountingAccount(BaseModel):
    """
    Modelo que representa una cuenta contable individual con estructura jerárquica.
    """
    
    idAccountingAccount: int = Field(
        description="ID único de la cuenta contable",
        examples=[1, 2, 100]
    )
    
    idAccountingAccountFather: Optional[int] = Field(
        default=None,
        description="ID de la cuenta contable padre (None para cuentas raíz)",
        examples=[1, 2, None]
    )
    
    codeAccountingAccount: str = Field(
        description="Código de la cuenta contable",
        max_length=50,
        examples=["001", "001-001", "001-001-001"]
    )
    
    nameAccountingAccount: str = Field(
        description="Nombre descriptivo de la cuenta contable",
        max_length=255,
        examples=["Activo", "Caja General", "Caja General 2"]
    )
    
    active: bool = Field(
        description="Indica si la cuenta está activa",
        examples=[True, False]
    )
    
    children: Optional[List['AccountingAccount']] = Field(
        default=None,
        description="Lista de cuentas contables hijas (estructura recursiva)"
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idAccountingAccount": 1,
                "idAccountingAccountFather": None,
                "codeAccountingAccount": "001",
                "nameAccountingAccount": "Activo",
                "active": True,
                "children": [
                    {
                        "idAccountingAccount": 8,
                        "idAccountingAccountFather": 1,
                        "codeAccountingAccount": "001-001",
                        "nameAccountingAccount": "Caja General",
                        "active": True,
                        "children": []
                    }
                ]
            }
        }


# Necesario para referencias recursivas
AccountingAccount.model_rebuild()


class AccountingAccountRequest(BaseModel):
    """
    Modelo para request de obtención de cuentas contables paginadas.
    Corresponde al parámetro JSON del stored procedure spAccountingAccountGet.
    """
    
    search: Optional[str] = Field(
        default=None,
        description="Término de búsqueda para filtrar por nombre de cuenta",
        max_length=50,
        examples=["efectivo", "caja", "ventas"]
    )
    
    sort: Optional[Literal[
        "idAccountingAccount_asc",
        "idAccountingAccountFather_asc",
        "idAccountingAccountFather_desc", 
        "codeAccountingAccount_asc", 
        "codeAccountingAccount_desc",
        "nameAccountingAccount_asc",
        "nameAccountingAccount_desc"
    ]] = Field(
        default="nameAccountingAccount_asc",
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
    
    includeInactive: Optional[bool] = Field(
        default=False,
        description="Si es True, incluye cuentas inactivas en los resultados"
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
                "itemPerPage": 20,
                "includeInactive": False
            }
        }


class AccountingAccountResponse(BaseModel):
    """
    Modelo de respuesta para cuentas contables paginadas con estructura jerárquica.
    Corresponde a la estructura JSON devuelta por el stored procedure.
    """
    
    total: int = Field(
        description="Total de registros que coinciden con el filtro",
        examples=[0, 6, 250]
    )
    
    data: List[AccountingAccount] = Field(
        description="Lista de cuentas contables con estructura jerárquica",
        examples=[[
            {
                "idAccountingAccount": 1,
                "idAccountingAccountFather": None,
                "codeAccountingAccount": "001",
                "nameAccountingAccount": "Activo",
                "active": True,
                "children": [
                    {
                        "idAccountingAccount": 8,
                        "idAccountingAccountFather": 1,
                        "codeAccountingAccount": "001-001",
                        "nameAccountingAccount": "Caja General",
                        "active": True,
                        "children": [
                            {
                                "idAccountingAccount": 9,
                                "idAccountingAccountFather": 8,
                                "codeAccountingAccount": "001-001-001",
                                "nameAccountingAccount": "Caja General 2",
                                "active": True,
                                "children": [
                                    {
                                        "idAccountingAccount": 10,
                                        "idAccountingAccountFather": 9,
                                        "codeAccountingAccount": "001-001-001-001",
                                        "nameAccountingAccount": "Caja General 3",
                                        "active": True,
                                        "children": None
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "idAccountingAccount": 3,
                "idAccountingAccountFather": None,
                "codeAccountingAccount": "003",
                "nameAccountingAccount": "Capital",
                "active": True,
                "children": None
            }
        ]]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "total": 6,
                "data": [
                    {
                        "idAccountingAccount": 1,
                        "idAccountingAccountFather": None,
                        "codeAccountingAccount": "001",
                        "nameAccountingAccount": "Activo",
                        "active": True,
                        "children": [
                            {
                                "idAccountingAccount": 8,
                                "idAccountingAccountFather": 1,
                                "codeAccountingAccount": "001-001",
                                "nameAccountingAccount": "Caja General",
                                "active": True,
                                "children": []
                            }
                        ]
                    },
                    {
                        "idAccountingAccount": 2,
                        "idAccountingAccountFather": None,
                        "codeAccountingAccount": "002",
                        "nameAccountingAccount": "Pasivo",
                        "active": True,
                        "children": None
                    }
                ]
            }
        }


class AccountingAccountCreateRequest(BaseModel):
    """
    Modelo para request de creación de cuenta contable.
    """
    
    idAccountingAccountFather: Optional[int] = Field(
        default=None,
        description="ID de la cuenta contable padre (None para cuentas raíz)",
        examples=[1, 2, None]
    )
    
    codeAccountingAccount: str = Field(
        description="Código de la cuenta contable",
        max_length=50,
        examples=["001-001-001", "002-001"]
    )
    
    nameAccountingAccount: str = Field(
        description="Nombre descriptivo de la cuenta contable",
        max_length=255,
        examples=["Caja Chica", "Banco Nacional"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idAccountingAccountFather": 8,
                "codeAccountingAccount": "001-001-002",
                "nameAccountingAccount": "Caja Chica"
            }
        }


class AccountingAccountUpdateRequest(BaseModel):
    """
    Modelo para request de actualización de cuenta contable.
    """
    
    idAccountingAccountFather: Optional[int] = Field(
        default=None,
        description="ID de la cuenta contable padre (opcional para actualización parcial)",
        examples=[1, 2, None]
    )
    
    codeAccountingAccount: Optional[str] = Field(
        default=None,
        description="Código de la cuenta contable (opcional para actualización parcial)",
        max_length=50,
        examples=["001-001-001", "002-001"]
    )
    
    nameAccountingAccount: Optional[str] = Field(
        default=None,
        description="Nombre descriptivo de la cuenta contable (opcional para actualización parcial)",
        max_length=255,
        examples=["Caja Principal", "Banco Central"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "nameAccountingAccount": "Caja Principal Actualizada"
            }
        }


class AccountingAccountCreateResponse(BaseModel):
    """
    Modelo de respuesta para creación de cuenta contable.
    """
    
    idAccountingAccount: int = Field(
        description="ID de la cuenta contable creada",
        examples=[1, 25, 100]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idAccountingAccount": 25
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
