"""
Modelos Pydantic para compañías.
Define las estructuras de datos para requests y responses de compañías.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class Company(BaseModel):
    """
    Modelo que representa una compañía individual.
    """
    
    idCompany: int = Field(
        description="ID único de la compañía",
        examples=[1, 2, 100]
    )
    
    codeCompany: str = Field(
        description="Código único de la compañía (puede usarse como cédula empresarial)",
        max_length=20,
        examples=["COMP-001", "ITQS", "3-101-123456"]
    )
    
    nameCompany: str = Field(
        description="Nombre de la compañía",
        max_length=100,
        examples=["IT Quest Solutions", "Empresa ABC", "Corporación XYZ"]
    )
    
    descriptionCompany: str = Field(
        description="Descripción de la compañía",
        max_length=500,
        examples=["Empresa de tecnología", "Consultoría empresarial"]
    )
    
    active: bool = Field(
        description="Estado de la compañía (activa/inactiva)",
        examples=[True, False]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idCompany": 1,
                "codeCompany": "3-101-123456",
                "nameCompany": "IT Quest Solutions",
                "descriptionCompany": "Empresa de desarrollo de software",
                "active": True
            }
        }


class CompanyCreateRequest(BaseModel):
    """
    Modelo para request de creación de compañía.
    """
    
    codeCompany: str = Field(
        description="Código único de la compañía (puede usarse como cédula empresarial)",
        max_length=20,
        examples=["COMP-001", "ITQS", "3-101-123456"]
    )
    
    nameCompany: str = Field(
        description="Nombre de la compañía",
        max_length=100,
        examples=["IT Quest Solutions", "Empresa ABC"]
    )
    
    descriptionCompany: str = Field(
        description="Descripción de la compañía",
        max_length=500,
        examples=["Empresa de tecnología y desarrollo"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "codeCompany": "3-101-123456",
                "nameCompany": "IT Quest Solutions",
                "descriptionCompany": "Empresa de desarrollo de software y consultoría tecnológica"
            }
        }


class CompanyUpdateRequest(BaseModel):
    """
    Modelo para request de actualización de compañía.
    """
    
    codeCompany: Optional[str] = Field(
        default=None,
        description="Código único de la compañía (puede usarse como cédula empresarial - opcional para actualización parcial)",
        max_length=20,
        examples=["COMP-001", "ITQS", "3-101-123456"]
    )
    
    nameCompany: Optional[str] = Field(
        default=None,
        description="Nombre de la compañía (opcional para actualización parcial)",
        max_length=100,
        examples=["IT Quest Solutions", "Empresa ABC"]
    )
    
    descriptionCompany: Optional[str] = Field(
        default=None,
        description="Descripción de la compañía (opcional para actualización parcial)",
        max_length=500,
        examples=["Empresa de tecnología y desarrollo"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "nameCompany": "IT Quest Solutions S.A.",
                "descriptionCompany": "Empresa de desarrollo de software y consultoría tecnológica avanzada"
            }
        }


class CompanyCreateResponse(BaseModel):
    """
    Modelo de respuesta para creación de compañía.
    """
    
    idCompany: int = Field(
        description="ID de la compañía creada",
        examples=[1, 25, 100]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idCompany": 1
            }
        }


class CompanyListRequest(BaseModel):
    """
    Modelo para request de listado de compañías paginadas.
    """
    
    search: Optional[str] = Field(
        default=None,
        description="Término de búsqueda para filtrar por nombre o código/cédula de compañía",
        max_length=50,
        examples=["ITQS", "tecnología", "3-101-123456"]
    )
    
    sort: Optional[Literal[
        "idCompany_asc",
        "codeCompany_asc", 
        "codeCompany_desc",
        "nameCompany_asc",
        "nameCompany_desc"
    ]] = Field(
        default="nameCompany_asc",
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
        description="Si incluir compañías inactivas en el resultado"
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "search": "3-101-123456",
                "sort": "nameCompany_asc",
                "page": 1,
                "itemPerPage": 20,
                "includeInactive": False
            }
        }


class CompanyListResponse(BaseModel):
    """
    Modelo de respuesta para listado de compañías paginadas.
    """
    
    total: int = Field(
        description="Total de registros que coinciden con el filtro",
        examples=[0, 15, 100]
    )
    
    data: List[Company] = Field(
        description="Lista de compañías para la página actual"
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "total": 2,
                "data": [
                    {
                        "idCompany": 1,
                        "codeCompany": "3-101-123456",
                        "nameCompany": "IT Quest Solutions",
                        "descriptionCompany": "Empresa de desarrollo de software",
                        "active": True
                    },
                    {
                        "idCompany": 2,
                        "codeCompany": "3-102-789012",
                        "nameCompany": "Empresa ABC",
                        "descriptionCompany": "Consultoría empresarial",
                        "active": True
                    }
                ]
            }
        }


class CompanyErrorResponse(BaseModel):
    """
    Modelo de respuesta para errores en endpoints de compañías.
    """
    
    detail: str = Field(
        description="Descripción detallada del error",
        examples=["Error de base de datos", "Compañía no encontrada", "Parámetros inválidos"]
    )
    
    error_code: Optional[str] = Field(
        default=None,
        description="Código de error específico para manejo programático",
        examples=["DB_CONNECTION_ERROR", "COMPANY_NOT_FOUND", "INVALID_PARAMETERS"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "detail": "Compañía no encontrada",
                "error_code": "COMPANY_NOT_FOUND"
            }
        }