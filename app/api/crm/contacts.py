"""
Rutas para gestión de contactos (contacts) en Dynamics 365 CRM.
Proporciona endpoints completos CRUD para contactos/personas con funcionalidad de paginación y filtros.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional
import logging

from app.services.crm_service import crm_service
from app.models.crm import (
    ContactsListResponse, ContactResponse, ContactCreateRequest, 
    ContactUpdateRequest, CRMOperationResponse
)
from app.api.routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contacts", tags=["CRM - Contactos"])


@router.get(
    "",
    response_model=ContactsListResponse,
    summary="Obtener lista de contactos",
    description="""
    Obtiene una lista paginada de contactos (contacts/personas) desde Dynamics 365 CRM.
    
    **Funcionalidades:**
    - Paginación configurable con parámetros top y skip
    - Filtros OData para búsqueda avanzada por nombre, email, puesto, etc.
    - Selección de campos específicos para optimizar respuesta
    - Ordenamiento por diferentes campos
    
    **Filtros OData soportados:**
    - `contains(fullname,'texto')` - Buscar por nombre completo
    - `contains(emailaddress1,'@empresa.com')` - Filtrar por dominio de email
    - `contains(jobtitle,'gerente')` - Filtrar por puesto de trabajo
    - `firstname eq 'María'` - Buscar por nombre específico
    
    **Ejemplos:**
    - Buscar gerentes: `?filter_query=contains(jobtitle,'Gerente')`
    - Por dominio email: `?filter_query=contains(emailaddress1,'@empresa.com')`
    - Solo datos básicos: `?select_fields=fullname,emailaddress1,telephone1`
    """,
    responses={
        200: {"description": "Lista de contactos obtenida exitosamente"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error interno del servidor o configuración CRM"}
    }
)
async def get_contacts(
    current_user: dict = Depends(get_current_user),
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
        examples=["contains(fullname,'María')", "contains(jobtitle,'Gerente')"]
    ),
    select_fields: Optional[str] = Query(
        None, 
        description="Campos separados por comas a seleccionar",
        examples=["fullname,emailaddress1,telephone1", "fullname,jobtitle,mobilephone"]
    ),
    order_by: Optional[str] = Query(
        None, 
        description="Campo para ordenar los resultados",
        examples=["fullname asc", "createdon desc", "lastname asc"]
    )
):
    """Obtiene una lista paginada de contactos de Dynamics 365."""
    
    try:
        
        result = await crm_service.get_contacts(
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
        logger.error(f"❌ Error obteniendo contactos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/by-nextlink",
    response_model=ContactsListResponse,
    summary="Obtener siguiente página usando nextLink",
    description="""
    Obtiene la siguiente página de contactos usando el @odata.nextLink de Dynamics 365.
    
    **⚠️ Importante - Server-Driven Paging:**
    - Dynamics 365 NO soporta el parámetro $skip para paginación
    - Usa server-driven paging con $skiptoken (cookie de paginación)
    - El nextLink incluye automáticamente el $skiptoken correcto
    
    **Flujo de Paginación:**
    1. Primera petición: GET /contacts?top=25 → retorna @odata.nextLink
    2. Siguientes páginas: GET /by-nextlink?next_link=<url> → retorna más datos + nextLink
    3. Continuar hasta que nextLink sea null (última página)
    
    **Reglas Críticas:**
    - ✅ Usar el nextLink completo tal como viene en la respuesta
    - ❌ NO modificar el nextLink ni agregar parámetros adicionales
    - ❌ NO intentar decodificar o manipular el $skiptoken
    - ✅ Mantener el mismo page size en todas las peticiones
    
    **Ejemplo de nextLink:**
    ```
    /api/data/v9.2/contacts?$select=fullname&$skiptoken=%3Ccookie%20pagenumber=%222%22...
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
async def get_contacts_by_nextlink(
    next_link: str = Query(
        ...,
        description="URL completa del @odata.nextLink retornado por la primera llamada a get_contacts",
        examples=["/api/data/v9.2/contacts?$select=fullname&$skiptoken=%3Ccookie..."]
    ),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene la siguiente página de contactos usando el nextLink de D365."""
    
    try:
        
        result = await crm_service.get_contacts_by_nextlink(next_link)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo siguiente página de contactos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Obtener contacto por ID",
    description="""
    Obtiene un contacto específico por su GUID de Dynamics 365.
    
    **Funcionalidad:**
    - Búsqueda por ID único (GUID) del contacto
    - Retorna todos los campos disponibles del contacto
    - Incluye información completa de contacto, dirección y puesto
    
    **Formato del ID:**
    - Debe ser un GUID válido de Dynamics 365
    - Ejemplo: `729ca2a0-024a-ea11-a815-000d3a591220`
    """,
    responses={
        200: {"description": "Contacto encontrado"},
        401: {"description": "Token de autorización requerido"},
        404: {"description": "Contacto no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_contact_by_id(
    contact_id: str = Path(
        ..., 
        description="GUID único del contacto en Dynamics 365",
        examples=["729ca2a0-024a-ea11-a815-000d3a591220"]
    ),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene un contacto específico por su ID."""
    
    try:
        
        result = await crm_service.get_contact_by_id(contact_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo contacto {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post(
    "",
    response_model=CRMOperationResponse,
    summary="Crear nuevo contacto",
    description="""
    Crea un nuevo contacto en Dynamics 365 CRM.
    
    **Campos requeridos:**
    - `firstname`: Nombre del contacto (obligatorio)
    - `lastname`: Apellidos del contacto (obligatorio)
    
    **Campos opcionales:**
    - `emailaddress1`: Email principal del contacto
    - `telephone1`: Teléfono principal
    - `mobilephone`: Teléfono móvil
    - `jobtitle`: Puesto de trabajo o cargo
    
    **Validaciones:**
    - Nombre y apellidos deben tener entre 1 y 50 caracteres cada uno
    - Email debe tener formato válido si se proporciona
    - El nombre completo se genera automáticamente como "firstname lastname"
    """,
    responses={
        200: {"description": "Contacto creado exitosamente"},
        400: {"description": "Datos de entrada inválidos"},
        401: {"description": "Token de autorización requerido"},
        500: {"description": "Error interno del servidor"}
    }
)
async def create_contact(
    contact_data: ContactCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Crea un nuevo contacto en Dynamics 365."""
    
    try:
        full_name = f"{contact_data.firstname} {contact_data.lastname}"
        
        result = await crm_service.create_contact(contact_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creando contacto: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.patch(
    "/{contact_id}",
    response_model=CRMOperationResponse,
    summary="Actualizar contacto",
    description="""
    Actualiza un contacto existente en Dynamics 365.
    
    **Funcionalidad:**
    - Actualización parcial (PATCH) - solo se envían los campos modificados
    - Todos los campos son opcionales
    - Mantiene los valores existentes para campos no especificados
    - El nombre completo se actualiza automáticamente si se cambian firstname/lastname
    
    **Campos actualizables:**
    - `firstname`, `lastname`: Nombre y apellidos
    - `emailaddress1`: Email principal
    - `telephone1`, `mobilephone`: Teléfonos
    - `jobtitle`: Puesto de trabajo
    """,
    responses={
        200: {"description": "Contacto actualizado exitosamente"},
        400: {"description": "Datos de entrada inválidos"},
        401: {"description": "Token de autorización requerido"},
        404: {"description": "Contacto no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def update_contact(
    contact_id: str = Path(
        ..., 
        description="GUID único del contacto a actualizar",
        examples=["729ca2a0-024a-ea11-a815-000d3a591220"]
    ),
    contact_data: ContactUpdateRequest = ...,
    current_user: dict = Depends(get_current_user)
):
    """Actualiza un contacto existente en Dynamics 365."""
    
    try:
        
        result = await crm_service.update_contact(contact_id, contact_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando contacto {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete(
    "/{contact_id}",
    response_model=CRMOperationResponse,
    summary="Eliminar contacto",
    description="""
    Elimina un contacto de Dynamics 365.
    
    **⚠️ Advertencia:**
    Esta operación es irreversible. El contacto será eliminado permanentemente
    del sistema CRM, incluyendo sus relaciones con casos, actividades y cuentas.
    
    **Funcionalidad:**
    - Eliminación permanente del contacto
    - No se puede deshacer la operación
    - Se recomienda verificar dependencias antes de eliminar
    """,
    responses={
        200: {"description": "Contacto eliminado exitosamente"},
        401: {"description": "Token de autorización requerido"},
        404: {"description": "Contacto no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def delete_contact(
    contact_id: str = Path(
        ..., 
        description="GUID único del contacto a eliminar",
        examples=["729ca2a0-024a-ea11-a815-000d3a591220"]
    ),
    current_user: dict = Depends(get_current_user)
):
    """Elimina un contacto de Dynamics 365."""
    
    try:
        
        result = await crm_service.delete_contact(contact_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando contacto {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")