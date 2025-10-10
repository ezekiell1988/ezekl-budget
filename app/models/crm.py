"""
Modelos Pydantic para integración con Dynamics 365 CRM.
Contiene las definiciones de esquemas para casos, cuentas y contactos.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


# ========== MODELOS DE RESPUESTA ==========

class CaseResponse(BaseModel):
    """Modelo de respuesta para un caso individual de Dynamics 365"""
    incidentid: Optional[str] = Field(None, description="ID único del caso")
    title: Optional[str] = Field(None, description="Título del caso")
    ticketnumber: Optional[str] = Field(None, description="Número de ticket")
    description: Optional[str] = Field(None, description="Descripción del caso")
    statuscode: Optional[int] = Field(None, description="Código de estado")
    casetypecode: Optional[int] = Field(None, description="Código de tipo de caso")
    prioritycode: Optional[int] = Field(None, description="Código de prioridad")
    createdon: Optional[datetime] = Field(None, description="Fecha de creación")
    modifiedon: Optional[datetime] = Field(None, description="Fecha de modificación")
    customerid_account: Optional[Dict[str, Any]] = Field(None, description="Información de la cuenta cliente")
    customerid_contact: Optional[Dict[str, Any]] = Field(None, description="Información del contacto cliente")

    class Config:
        json_schema_extra = {
            "example": {
                "incidentid": "4bb40b00-024b-ea11-a815-000d3a591219",
                "title": "Sistema de facturación no funciona",
                "ticketnumber": "CAS-2025-001",
                "description": "El cliente reporta errores en el sistema de facturación",
                "statuscode": 1,
                "casetypecode": 1,
                "prioritycode": 1,
                "createdon": "2025-10-09T10:30:00Z",
                "modifiedon": "2025-10-09T15:45:00Z"
            }
        }


class CasesListResponse(BaseModel):
    """Modelo de respuesta para lista de casos"""
    count: int = Field(..., description="Número de casos en la respuesta")
    cases: List[CaseResponse] = Field(..., description="Lista de casos")
    next_link: Optional[str] = Field(None, description="Enlace para la siguiente página")
    
    model_config = {
        "populate_by_name": True  # Permitir poblar por alias o por nombre de campo
    }


class AccountResponse(BaseModel):
    """Modelo de respuesta para una cuenta individual de Dynamics 365"""
    accountid: Optional[str] = Field(None, description="ID único de la cuenta")
    name: Optional[str] = Field(None, description="Nombre de la cuenta")
    accountnumber: Optional[str] = Field(None, description="Número de cuenta")
    telephone1: Optional[str] = Field(None, description="Teléfono principal")
    emailaddress1: Optional[str] = Field(None, description="Email principal")
    websiteurl: Optional[str] = Field(None, description="Sitio web")
    address1_line1: Optional[str] = Field(None, description="Dirección línea 1")
    address1_city: Optional[str] = Field(None, description="Ciudad")
    address1_stateorprovince: Optional[str] = Field(None, description="Estado/Provincia")
    address1_postalcode: Optional[str] = Field(None, description="Código postal")
    address1_country: Optional[str] = Field(None, description="País")
    industrycode: Optional[int] = Field(None, description="Código de industria")
    revenue: Optional[float] = Field(None, description="Ingresos")
    numberofemployees: Optional[int] = Field(None, description="Número de empleados")
    createdon: Optional[datetime] = Field(None, description="Fecha de creación")
    modifiedon: Optional[datetime] = Field(None, description="Fecha de modificación")

    class Config:
        json_schema_extra = {
            "example": {
                "accountid": "629ca2a0-024a-ea11-a815-000d3a591218",
                "name": "IT Quest Solutions",
                "accountnumber": "ACC-2025-001",
                "telephone1": "+1-555-0123",
                "emailaddress1": "info@itqs.com",
                "websiteurl": "https://www.itqs.com",
                "address1_line1": "123 Tech Street",
                "address1_city": "Tech City",
                "address1_country": "USA"
            }
        }


class AccountsListResponse(BaseModel):
    """Modelo de respuesta para lista de cuentas"""
    count: int = Field(..., description="Número de cuentas en la respuesta")
    accounts: List[AccountResponse] = Field(..., description="Lista de cuentas")
    next_link: Optional[str] = Field(None, description="Enlace para la siguiente página")
    
    model_config = {
        "populate_by_name": True  # Permitir poblar por alias o por nombre de campo
    }


class ContactResponse(BaseModel):
    """Modelo de respuesta para un contacto individual de Dynamics 365"""
    contactid: Optional[str] = Field(None, description="ID único del contacto")
    fullname: Optional[str] = Field(None, description="Nombre completo del contacto")
    firstname: Optional[str] = Field(None, description="Nombre")
    lastname: Optional[str] = Field(None, description="Apellidos")
    emailaddress1: Optional[str] = Field(None, description="Email principal")
    telephone1: Optional[str] = Field(None, description="Teléfono principal")
    mobilephone: Optional[str] = Field(None, description="Teléfono móvil")
    jobtitle: Optional[str] = Field(None, description="Puesto de trabajo")
    address1_line1: Optional[str] = Field(None, description="Dirección línea 1")
    address1_city: Optional[str] = Field(None, description="Ciudad")
    address1_country: Optional[str] = Field(None, description="País")
    createdon: Optional[datetime] = Field(None, description="Fecha de creación")
    modifiedon: Optional[datetime] = Field(None, description="Fecha de modificación")

    class Config:
        json_schema_extra = {
            "example": {
                "contactid": "729ca2a0-024a-ea11-a815-000d3a591220",
                "fullname": "María García López",
                "firstname": "María",
                "lastname": "García López",
                "emailaddress1": "maria.garcia@empresa.com",
                "telephone1": "+1-555-0456",
                "jobtitle": "Gerente de TI"
            }
        }


class ContactsListResponse(BaseModel):
    """Modelo de respuesta para lista de contactos"""
    count: int = Field(..., description="Número de contactos en la respuesta")
    contacts: List[ContactResponse] = Field(..., description="Lista de contactos")
    next_link: Optional[str] = Field(None, description="Enlace para la siguiente página", serialization_alias="next_link")
    
    class Config:
        populate_by_name = True  # Permitir poblar por alias o por nombre de campo


class CaseTypeCodeResponse(BaseModel):
    """Modelo de respuesta para opciones de tipo de caso"""
    value: int = Field(..., description="Valor numérico del tipo de caso")
    label: Optional[str] = Field(None, description="Etiqueta descriptiva del tipo")

    class Config:
        json_schema_extra = {
            "example": {
                "value": 1,
                "label": "Incidencia"
            }
        }


class CaseTypeCodesResponse(BaseModel):
    """Modelo de respuesta para lista de tipos de caso"""
    case_types: List[CaseTypeCodeResponse] = Field(..., description="Lista de tipos de caso disponibles")


class CRMOperationResponse(BaseModel):
    """Modelo de respuesta para operaciones CRUD del CRM"""
    status: str = Field(..., description="Estado de la operación (success, error)")
    entity_url: Optional[str] = Field(None, description="URL de la entidad creada")
    entity_id: Optional[str] = Field(None, description="ID de la entidad afectada")
    message: Optional[str] = Field(None, description="Mensaje adicional")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "entity_id": "629ca2a0-024a-ea11-a815-000d3a591218",
                "message": "Entidad creada exitosamente"
            }
        }


class CRMHealthResponse(BaseModel):
    """Modelo de respuesta para health check del CRM"""
    status: str = Field(..., description="Estado del servicio (ok, error)")
    d365: str = Field(..., description="URL base de Dynamics 365")
    api_version: str = Field(..., description="Versión de la API")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "d365": "https://itqsdev.crm.dynamics.com",
                "api_version": "v9.0"
            }
        }


class CRMTokenResponse(BaseModel):
    """Modelo de respuesta para información de token"""
    token_preview: str = Field(..., description="Vista previa del token (parcialmente oculto)")
    expires_at: int = Field(..., description="Timestamp de expiración del token")

    class Config:
        json_schema_extra = {
            "example": {
                "token_preview": "eyJ0eXAiOiJ...Q4NDAx8A",
                "expires_at": 1728481234
            }
        }


class CRMDiagnoseResponse(BaseModel):
    """Modelo de respuesta para diagnóstico del CRM"""
    environment_variables: Dict[str, str] = Field(..., description="Estado de variables de entorno")
    token_acquisition: Dict[str, Any] = Field(..., description="Estado de adquisición de token")
    d365_connectivity: Dict[str, Any] = Field(..., description="Estado de conectividad con D365")
    recommendations: List[str] = Field(..., description="Recomendaciones de configuración")


# ========== MODELOS DE REQUEST/CREATE ==========

class CaseCreateRequest(BaseModel):
    """Payload para crear un caso en Dynamics 365"""
    title: str = Field(
        ..., 
        description="Título del caso",
        min_length=1,
        max_length=200,
        examples=["Sistema de facturación no funciona"]
    )
    description: Optional[str] = Field(
        None, 
        description="Descripción detallada del caso",
        max_length=2000,
        examples=["El cliente reporta que el sistema de facturación presenta errores al generar reportes mensuales"]
    )
    casetypecode: Optional[int] = Field(
        1, 
        description="Código de tipo de caso (depende de la configuración de D365)",
        examples=[1, 2, 3]
    )
    customer_account_id: Optional[str] = Field(
        None,
        description="GUID de la cuenta (Account) a vincular como cliente",
        examples=["629ca2a0-024a-ea11-a815-000d3a591218"]
    )
    customer_contact_id: Optional[str] = Field(
        None,
        description="GUID del contacto a vincular como cliente (alternativa a account)",
        examples=["729ca2a0-024a-ea11-a815-000d3a591220"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sistema de facturación no funciona",
                "description": "El cliente reporta errores en el sistema de facturación",
                "casetypecode": 1,
                "customer_account_id": "629ca2a0-024a-ea11-a815-000d3a591218"
            }
        }


class CaseUpdateRequest(BaseModel):
    """Payload para actualizar un caso en Dynamics 365"""
    title: Optional[str] = Field(
        None, 
        description="Título del caso",
        min_length=1,
        max_length=200,
        examples=["Sistema de facturación - RESUELTO"]
    )
    description: Optional[str] = Field(
        None, 
        description="Descripción detallada del caso",
        max_length=2000,
        examples=["Caso resuelto. Se actualizó la configuración del servidor de reportes"]
    )
    casetypecode: Optional[int] = Field(
        None, 
        description="Código de tipo de caso",
        examples=[1, 2, 3]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sistema de facturación - RESUELTO",
                "description": "Caso resuelto mediante actualización de configuración"
            }
        }


class AccountCreateRequest(BaseModel):
    """Payload para crear una cuenta en Dynamics 365"""
    name: str = Field(
        ..., 
        description="Nombre de la cuenta (requerido)",
        min_length=1,
        max_length=160,
        examples=["Tecnología Avanzada S.A."]
    )
    accountnumber: Optional[str] = Field(
        None, 
        description="Número de cuenta",
        max_length=20,
        examples=["ACC-2025-001"]
    )
    telephone1: Optional[str] = Field(
        None, 
        description="Teléfono principal",
        max_length=50,
        examples=["+1-555-0123"]
    )
    emailaddress1: Optional[str] = Field(
        None, 
        description="Email principal",
        max_length=100,
        examples=["contacto@empresa.com"]
    )
    websiteurl: Optional[str] = Field(
        None, 
        description="Sitio web",
        max_length=200,
        examples=["https://www.empresa.com"]
    )
    address1_line1: Optional[str] = Field(
        None, 
        description="Dirección línea 1",
        max_length=250,
        examples=["123 Calle Principal"]
    )
    address1_city: Optional[str] = Field(
        None, 
        description="Ciudad",
        max_length=80,
        examples=["Ciudad de México"]
    )
    address1_stateorprovince: Optional[str] = Field(
        None, 
        description="Estado/Provincia",
        max_length=50,
        examples=["CDMX"]
    )
    address1_postalcode: Optional[str] = Field(
        None, 
        description="Código postal",
        max_length=20,
        examples=["01234"]
    )
    address1_country: Optional[str] = Field(
        None, 
        description="País",
        max_length=80,
        examples=["México"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "IT Quest Solutions",
                "accountnumber": "ACC-2025-001",
                "telephone1": "+1-555-0123",
                "emailaddress1": "info@itqs.com",
                "websiteurl": "https://www.itqs.com",
                "address1_line1": "123 Tech Street",
                "address1_city": "Tech City",
                "address1_country": "USA"
            }
        }


class AccountUpdateRequest(BaseModel):
    """Payload para actualizar una cuenta en Dynamics 365"""
    name: Optional[str] = Field(
        None, 
        description="Nombre de la cuenta",
        min_length=1,
        max_length=160
    )
    telephone1: Optional[str] = Field(None, description="Teléfono principal", max_length=50)
    emailaddress1: Optional[str] = Field(None, description="Email principal", max_length=100)
    websiteurl: Optional[str] = Field(None, description="Sitio web", max_length=200)
    address1_line1: Optional[str] = Field(None, description="Dirección línea 1", max_length=250)
    address1_city: Optional[str] = Field(None, description="Ciudad", max_length=80)
    address1_country: Optional[str] = Field(None, description="País", max_length=80)


class ContactCreateRequest(BaseModel):
    """Payload para crear un contacto en Dynamics 365"""
    firstname: str = Field(
        ..., 
        description="Nombre del contacto (requerido)",
        min_length=1,
        max_length=50,
        examples=["María"]
    )
    lastname: str = Field(
        ..., 
        description="Apellidos del contacto (requerido)",
        min_length=1,
        max_length=50,
        examples=["García López"]
    )
    emailaddress1: Optional[str] = Field(
        None, 
        description="Email principal",
        max_length=100,
        examples=["maria.garcia@empresa.com"]
    )
    telephone1: Optional[str] = Field(
        None, 
        description="Teléfono principal",
        max_length=50,
        examples=["+1-555-0456"]
    )
    mobilephone: Optional[str] = Field(
        None, 
        description="Teléfono móvil",
        max_length=50,
        examples=["+1-555-0789"]
    )
    jobtitle: Optional[str] = Field(
        None, 
        description="Puesto de trabajo",
        max_length=100,
        examples=["Gerente de TI"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "firstname": "María",
                "lastname": "García López",
                "emailaddress1": "maria.garcia@empresa.com",
                "telephone1": "+1-555-0456",
                "jobtitle": "Gerente de TI"
            }
        }


class ContactUpdateRequest(BaseModel):
    """Payload para actualizar un contacto en Dynamics 365"""
    firstname: Optional[str] = Field(None, description="Nombre del contacto", min_length=1, max_length=50)
    lastname: Optional[str] = Field(None, description="Apellidos del contacto", min_length=1, max_length=50)
    emailaddress1: Optional[str] = Field(None, description="Email principal", max_length=100)
    telephone1: Optional[str] = Field(None, description="Teléfono principal", max_length=50)
    mobilephone: Optional[str] = Field(None, description="Teléfono móvil", max_length=50)
    jobtitle: Optional[str] = Field(None, description="Puesto de trabajo", max_length=100)