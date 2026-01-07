"""
Rutas para gestión de casos (incidents) en Dynamics 365 CRM.
Proporciona endpoints completos CRUD para casos con funcionalidad de paginación y filtros.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional
import logging

from app.models.auth import CurrentUser
from app.services.crm_service import crm_service
from app.models.crm import (
    CasesListResponse, CaseResponse, CaseCreateRequest, 
    CaseUpdateRequest, CRMOperationResponse
)
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cases", tags=["CRM - Casos"])


@router.get(
    "",
    response_model=CasesListResponse,
    summary="Obtener lista de casos",
    description="""
    Obtiene una lista paginada de casos (incidents) desde Dynamics 365 CRM.
    
    **Funcionalidades:**
    - Paginación configurable con parámetros top y skip
    - Filtros OData para búsqueda avanzada
    - Selección de campos específicos para optimizar respuesta
    - Ordenamiento personalizable
    
    **Filtros OData soportados:**
    - `contains(title,'texto')` - Buscar en título
    - `statuscode eq 1` - Filtrar por estado
    - `casetypecode eq 2` - Filtrar por tipo de caso
    - `createdon gt 2025-01-01T00:00:00Z` - Filtrar por fecha
    
    **Ejemplos:**
    - Casos activos: `?filter_query=statuscode eq 1`
    - Buscar por título: `?filter_query=contains(title,'facturación')`
    - Solo campos básicos: `?select_fields=title,statuscode,createdon`
    """,
    responses={
        200: {"description": "Lista de casos obtenida exitosamente"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error interno del servidor o configuración CRM"}
    }
)
async def get_cases(
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
        examples=["statuscode eq 1", "contains(title,'sistema')"]
    ),
    select_fields: Optional[str] = Query(
        None, 
        description="Campos separados por comas a seleccionar",
        examples=["title,statuscode,createdon", "title,description,customerid_account"]
    ),
    order_by: Optional[str] = Query(
        None, 
        description="Campo para ordenar los resultados",
        examples=["createdon desc", "title asc", "statuscode asc"]
    )
):
    """Obtiene una lista paginada de casos de Dynamics 365."""
    
    try:
        
        result = await crm_service.get_cases(
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
        logger.error(f"❌ Error obteniendo casos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/by-nextlink",
    response_model=CasesListResponse,
    summary="Obtener siguiente página usando nextLink",
    description="""
    Obtiene la siguiente página de casos usando el @odata.nextLink de Dynamics 365.
    
    **⚠️ Importante - Server-Driven Paging:**
    - Dynamics 365 NO soporta el parámetro $skip para paginación
    - Usa server-driven paging con $skiptoken (cookie de paginación)
    - El nextLink incluye automáticamente el $skiptoken correcto
    
    **Flujo de Paginación:**
    1. Primera petición: GET /cases?top=25 → retorna @odata.nextLink
    2. Siguientes páginas: GET /by-nextlink?next_link=<url> → retorna más datos + nextLink
    3. Continuar hasta que nextLink sea null (última página)
    
    **Reglas Críticas:**
    - ✅ Usar el nextLink completo tal como viene en la respuesta
    - ❌ NO modificar el nextLink ni agregar parámetros adicionales
    - ❌ NO intentar decodificar o manipular el $skiptoken
    - ✅ Mantener el mismo page size en todas las peticiones
    
    **Ejemplo de nextLink:**
    ```
    /api/data/v9.2/incidents?$select=title&$skiptoken=%3Ccookie%20pagenumber=%222%22...
    ```
    """,
    responses={
        200: {"description": "Siguiente página obtenida exitosamente"},
        400: {"description": "nextLink inválido o malformado"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_cases_by_nextlink(
    next_link: str = Query(
        ...,
        description="URL completa del @odata.nextLink retornado por Dynamics 365",
        examples=[
            "/api/data/v9.2/incidents?$select=incidentid,title&$skiptoken=%3Ccookie...",
            "/api/data/v9.2/incidents?$orderby=incidentid&$top=25&$skiptoken=%3Ccookie..."
        ]
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene la siguiente página de casos usando nextLink de Dynamics 365.
    
    Este endpoint implementa server-driven paging correctamente según la
    especificación OData v4.0 y las limitaciones de Dynamics 365 Web API.
    """
    
    try:
        
        result = await crm_service.get_cases_by_nextlink(next_link)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo siguiente página: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Obtener caso por ID",
    description="""
    Obtiene un caso específico por su GUID de Dynamics 365.
    
    **Funcionalidad:**
    - Búsqueda por ID único (GUID) del caso
    - Retorna todos los campos disponibles del caso
    - Incluye información de cliente asociado (account/contact)
    
    **Formato del ID:**
    - Debe ser un GUID válido de Dynamics 365
    - Ejemplo: `4bb40b00-024b-ea11-a815-000d3a591219`
    """,
    responses={
        200: {"description": "Caso encontrado"},
        401: {"description": "Token de autorización requerido"},
        404: {"description": "Caso no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_case_by_id(
    case_id: str = Path(
        ..., 
        description="GUID único del caso en Dynamics 365",
        examples=["4bb40b00-024b-ea11-a815-000d3a591219"]
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Obtiene un caso específico por su ID."""
    
    try:
        
        result = await crm_service.get_case_by_id(case_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo caso {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post(
    "",
    response_model=CRMOperationResponse,
    summary="Crear nuevo caso",
    description="""
    Crea un nuevo caso en Dynamics 365 CRM.
    
    **Campos requeridos:**
    - `title`: Título descriptivo del caso
    
    **Campos opcionales:**
    - `description`: Descripción detallada
    - `casetypecode`: Tipo de caso (depende de configuración D365)
    - `customer_account_id`: GUID de cuenta cliente
    - `customer_contact_id`: GUID de contacto cliente (alternativa a account)
    
    **Nota:** Solo se puede especificar customer_account_id O customer_contact_id, no ambos.
    """,
    responses={
        200: {"description": "Caso creado exitosamente"},
        400: {"description": "Datos de entrada inválidos"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error interno del servidor"}
    }
)
async def create_case(
    case_data: CaseCreateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Crea un nuevo caso en Dynamics 365."""
    
    try:
        pass  # Logger eliminado
        
        # Validación: no se puede especificar tanto account como contact
        if case_data.customer_account_id and case_data.customer_contact_id:
            raise HTTPException(
                status_code=400,
                detail="No se puede especificar tanto customer_account_id como customer_contact_id"
            )
        
        result = await crm_service.create_case(case_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creando caso: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.patch(
    "/{case_id}",
    response_model=CRMOperationResponse,
    summary="Actualizar caso",
    description="""
    Actualiza un caso existente en Dynamics 365.
    
    **Funcionalidad:**
    - Actualización parcial (PATCH) - solo se envían los campos modificados
    - Todos los campos son opcionales
    - Mantiene los valores existentes para campos no especificados
    
    **Campos actualizables:**
    - `title`: Título del caso
    - `description`: Descripción detallada  
    - `casetypecode`: Tipo de caso
    """,
    responses={
        200: {"description": "Caso actualizado exitosamente"},
        400: {"description": "Datos de entrada inválidos"},
        401: {"description": "Token de autorización requerido"},
        404: {"description": "Caso no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def update_case(
    case_id: str = Path(
        ..., 
        description="GUID único del caso a actualizar",
        examples=["4bb40b00-024b-ea11-a815-000d3a591219"]
    ),
    case_data: CaseUpdateRequest = ...,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Actualiza un caso existente en Dynamics 365."""
    
    try:
        
        result = await crm_service.update_case(case_id, case_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando caso {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete(
    "/{case_id}",
    response_model=CRMOperationResponse,
    summary="Eliminar caso",
    description="""
    Elimina un caso de Dynamics 365.
    
    **⚠️ Advertencia:**
    Esta operación es irreversible. El caso será eliminado permanentemente
    del sistema CRM.
    
    **Funcionalidad:**
    - Eliminación permanente del caso
    - No se puede deshacer la operación
    - Se recomienda verificar el ID antes de eliminar
    """,
    responses={
        200: {"description": "Caso eliminado exitosamente"},
        401: {"description": "Token de autorización requerido"},
        404: {"description": "Caso no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def delete_case(
    case_id: str = Path(
        ..., 
        description="GUID único del caso a eliminar",
        examples=["4bb40b00-024b-ea11-a815-000d3a591219"]
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Elimina un caso de Dynamics 365."""
    
    try:
        
        result = await crm_service.delete_case(case_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando caso {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")