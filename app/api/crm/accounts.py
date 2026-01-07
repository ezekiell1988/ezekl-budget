"""
Rutas para gestión de cuentas (accounts) en Dynamics 365 CRM.
Proporciona endpoints completos CRUD para cuentas/empresas con funcionalidad de paginación y filtros.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional
import logging

from app.models.auth import CurrentUser
from app.services.crm_service import crm_service
from app.models.crm import (
    AccountsListResponse, AccountResponse, AccountCreateRequest, 
    AccountUpdateRequest, CRMOperationResponse
)
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accounts", tags=["CRM - Cuentas"])


@router.get(
    "",
    response_model=AccountsListResponse,
    summary="Obtener lista de cuentas",
    description="""
    Obtiene una lista paginada de cuentas (accounts/empresas) desde Dynamics 365 CRM.
    
    **Funcionalidades:**
    - Paginación configurable con parámetros top y skip
    - Filtros OData para búsqueda avanzada por nombre, ciudad, etc.
    - Selección de campos específicos para optimizar respuesta
    - Ordenamiento por diferentes campos
    
    **Filtros OData soportados:**
    - `contains(name,'texto')` - Buscar por nombre de empresa
    - `contains(address1_city,'ciudad')` - Filtrar por ciudad
    - `industrycode eq 1` - Filtrar por código de industria
    - `revenue gt 1000000` - Filtrar por ingresos mínimos
    
    **Ejemplos:**
    - Empresas de tecnología: `?filter_query=contains(name,'Tecnología')`
    - Por ciudad: `?filter_query=contains(address1_city,'Madrid')`
    - Solo datos básicos: `?select_fields=name,telephone1,emailaddress1`
    """,
    responses={
        200: {"description": "Lista de cuentas obtenida exitosamente"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error interno del servidor o configuración CRM"}
    }
)
async def get_accounts(
    current_user: CurrentUser = Depends(get_current_user),
    top: Optional[int] = Query(
        10, 
        description="Número de registros a retornar", 
        ge=1, 
        le=1000,
        examples=[10, 25, 50]
    ),
    skip: Optional[int] = Query(
        0, 
        description="Número de registros a saltar para paginación", 
        ge=0,
        examples=[0, 10, 50]
    ),
    filter_query: Optional[str] = Query(
        None, 
        description="Expresión de filtro OData",
        examples=["contains(name,'Tecnología')", "contains(address1_city,'Madrid')"]
    ),
    select_fields: Optional[str] = Query(
        None, 
        description="Campos separados por comas a seleccionar",
        examples=["name,telephone1,emailaddress1", "name,address1_city,websiteurl"]
    ),
    order_by: Optional[str] = Query(
        None, 
        description="Campo para ordenar los resultados",
        examples=["name asc", "createdon desc", "revenue desc"]
    )
):
    """Obtiene una lista paginada de cuentas de Dynamics 365."""
    
    try:
        
        result = await crm_service.get_accounts(
            top=top,
            skip=skip,
            filter_query=filter_query,
            select_fields=select_fields,
            order_by=order_by
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo cuentas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/by-nextlink",
    response_model=AccountsListResponse,
    summary="Obtener siguiente página usando nextLink",
    description="""
    Obtiene la siguiente página de cuentas usando el @odata.nextLink de Dynamics 365.
    
    **⚠️ Importante - Server-Driven Paging:**
    - Dynamics 365 NO soporta el parámetro $skip para paginación
    - Usa server-driven paging con $skiptoken (cookie de paginación)
    - El nextLink incluye automáticamente el $skiptoken correcto
    
    **Flujo de Paginación:**
    1. Primera petición: GET /accounts?top=25 → retorna @odata.nextLink
    2. Siguientes páginas: GET /by-nextlink?next_link=<url> → retorna más datos + nextLink
    3. Continuar hasta que nextLink sea null (última página)
    
    **Reglas Críticas:**
    - ✅ Usar el nextLink completo tal como viene en la respuesta
    - ❌ NO modificar el nextLink ni agregar parámetros adicionales
    - ❌ NO intentar decodificar o manipular el $skiptoken
    - ✅ Mantener el mismo page size en todas las peticiones
    
    **Ejemplo de nextLink:**
    ```
    /api/data/v9.2/accounts?$select=name&$skiptoken=%3Ccookie%20pagenumber=%222%22...
    ```
    
    Ver guía completa: src/app/crm/accounts/D365_PAGINATION_GUIDE.md
    """,
    responses={
        200: {"description": "Siguiente página obtenida exitosamente"},
        400: {"description": "nextLink inválido o malformado"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_accounts_by_nextlink(
    next_link: str = Query(
        ...,
        description="URL completa del @odata.nextLink retornado por Dynamics 365",
        examples=[
            "/api/data/v9.2/accounts?$select=accountid,name&$skiptoken=%3Ccookie...",
            "/api/data/v9.2/accounts?$orderby=accountid&$top=25&$skiptoken=%3Ccookie..."
        ]
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene la siguiente página de cuentas usando nextLink de Dynamics 365.
    
    Este endpoint implementa server-driven paging correctamente según la
    especificación OData v4.0 y las limitaciones de Dynamics 365 Web API.
    """
    
    try:
        
        result = await crm_service.get_accounts_by_nextlink(next_link)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo siguiente página: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Obtener cuenta por ID",
    description="""
    Obtiene una cuenta específica por su GUID de Dynamics 365.
    
    **Funcionalidad:**
    - Búsqueda por ID único (GUID) de la cuenta
    - Retorna todos los campos disponibles de la cuenta
    - Incluye información completa de dirección, contacto y financiera
    
    **Formato del ID:**
    - Debe ser un GUID válido de Dynamics 365
    - Ejemplo: `629ca2a0-024a-ea11-a815-000d3a591218`
    """,
    responses={
        200: {"description": "Cuenta encontrada"},
        401: {"description": "Token de autorización requerido"},
        404: {"description": "Cuenta no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_account_by_id(
    account_id: str = Path(
        ..., 
        description="GUID único de la cuenta en Dynamics 365",
        examples=["629ca2a0-024a-ea11-a815-000d3a591218"]
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Obtiene una cuenta específica por su ID."""
    
    try:
        
        result = await crm_service.get_account_by_id(account_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo cuenta {account_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post(
    "",
    response_model=CRMOperationResponse,
    summary="Crear nueva cuenta",
    description="""
    Crea una nueva cuenta en Dynamics 365 CRM.
    
    **Campos requeridos:**
    - `name`: Nombre de la empresa/cuenta (obligatorio)
    
    **Campos opcionales:**
    - `accountnumber`: Número de cuenta para referencia interna
    - `telephone1`: Teléfono principal de contacto
    - `emailaddress1`: Email principal de contacto
    - `websiteurl`: Sitio web de la empresa
    - Campos de dirección: `address1_line1`, `address1_city`, etc.
    
    **Validaciones:**
    - El nombre debe tener entre 1 y 160 caracteres
    - Email debe tener formato válido si se proporciona
    - URL debe tener formato válido si se proporciona
    """,
    responses={
        200: {"description": "Cuenta creada exitosamente"},
        400: {"description": "Datos de entrada inválidos"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error interno del servidor"}
    }
)
async def create_account(
    account_data: AccountCreateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Crea una nueva cuenta en Dynamics 365."""
    
    try:
        
        result = await crm_service.create_account(account_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creando cuenta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.patch(
    "/{account_id}",
    response_model=CRMOperationResponse,
    summary="Actualizar cuenta",
    description="""
    Actualiza una cuenta existente en Dynamics 365.
    
    **Funcionalidad:**
    - Actualización parcial (PATCH) - solo se envían los campos modificados
    - Todos los campos son opcionales
    - Mantiene los valores existentes para campos no especificados
    
    **Campos actualizables:**
    - `name`: Nombre de la cuenta
    - `telephone1`, `emailaddress1`: Información de contacto
    - `websiteurl`: Sitio web
    - Campos de dirección: `address1_line1`, `address1_city`, `address1_country`
    """,
    responses={
        200: {"description": "Cuenta actualizada exitosamente"},
        400: {"description": "Datos de entrada inválidos"},
        401: {"description": "Token de autorización requerido"},
        404: {"description": "Cuenta no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def update_account(
    account_id: str = Path(
        ..., 
        description="GUID único de la cuenta a actualizar",
        examples=["629ca2a0-024a-ea11-a815-000d3a591218"]
    ),
    account_data: AccountUpdateRequest = ...,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Actualiza una cuenta existente en Dynamics 365."""
    
    try:
        
        result = await crm_service.update_account(account_id, account_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando cuenta {account_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete(
    "/{account_id}",
    response_model=CRMOperationResponse,
    summary="Eliminar cuenta",
    description="""
    Elimina una cuenta de Dynamics 365.
    
    **⚠️ Advertencia:**
    Esta operación es irreversible. La cuenta será eliminada permanentemente
    del sistema CRM, incluyendo sus relaciones con casos, oportunidades y contactos.
    
    **Funcionalidad:**
    - Eliminación permanente de la cuenta
    - No se puede deshacer la operación
    - Se recomienda verificar dependencias antes de eliminar
    """,
    responses={
        200: {"description": "Cuenta eliminada exitosamente"},
        401: {"description": "Token de autorización requerido"},
        404: {"description": "Cuenta no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def delete_account(
    account_id: str = Path(
        ..., 
        description="GUID único de la cuenta a eliminar",
        examples=["629ca2a0-024a-ea11-a815-000d3a591218"]
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Elimina una cuenta de Dynamics 365."""
    
    try:
        
        result = await crm_service.delete_account(account_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando cuenta {account_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")