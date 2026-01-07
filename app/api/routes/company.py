"""
Endpoints para gestión de compañías.
Proporciona funcionalidad CRUD completa para compañías con autenticación.
"""

import logging
import json
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import Optional, Dict
from app.database.connection import execute_sp
from app.utils.auth import get_current_user
from app.models.auth import CurrentUser
from app.models.company import (
    Company,
    CompanyCreateRequest,
    CompanyUpdateRequest,
    CompanyCreateResponse,
    CompanyListRequest,
    CompanyListResponse,
    CompanyErrorResponse
)

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de compañías
router = APIRouter()


@router.get(
    "",
    response_model=CompanyListResponse,
    summary="Obtener compañías paginadas",
    description="""Obtiene una lista paginada de compañías.
    
    Este endpoint permite consultar las compañías con las siguientes características:
    
    **Funcionalidades:**
    - Paginación configurable (página y elementos por página)
    - Búsqueda por nombre o código/cédula de compañía (búsqueda parcial, case-insensitive)
    - Ordenamiento por diferentes campos (ID, código, nombre)
    - Filtro para incluir/excluir compañías inactivas
    
    **Parámetros de ordenamiento disponibles:**
    - `idCompany_asc`: Por ID ascendente
    - `codeCompany_asc`: Por código ascendente
    - `codeCompany_desc`: Por código descendente
    - `nameCompany_asc`: Por nombre ascendente (default)
    - `nameCompany_desc`: Por nombre descendente
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Paginación:**
    - `page`: Número de página (inicia en 1, default: 1)
    - `itemPerPage`: Elementos por página (1-100, default: 10)
    
    **Respuesta:**
    - `total`: Total de registros que coinciden con el filtro
    - `data`: Array de compañías para la página solicitada
    
    **Ejemplos de uso:**
    - Obtener primeras 10 compañías: `GET /companies`
    - Buscar compañías con cédula específica: `GET /companies?search=3-101-123456`
    - Página 2 con 25 elementos: `GET /companies?page=2&itemPerPage=25`
    - Incluir inactivas: `GET /companies?includeInactive=true`
    """,
    responses={
        200: {
            "description": "Lista de compañías obtenida exitosamente",
            "model": CompanyListResponse
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        500: {
            "description": "Error interno del servidor",
            "model": CompanyErrorResponse
        }
    }
)
async def get_companies(
    search: Optional[str] = Query(
        None,
        description="Término de búsqueda para filtrar por nombre o código/cédula",
        max_length=50,
        example="3-101-123456"
    ),
    sort: Optional[str] = Query(
        "nameCompany_asc",
        description="Campo y dirección de ordenamiento",
        regex="^(idCompany_asc|codeCompany_asc|codeCompany_desc|nameCompany_asc|nameCompany_desc)$",
        example="nameCompany_asc"
    ),
    page: Optional[int] = Query(
        1,
        ge=1,
        description="Número de página (inicia en 1)",
        example=1
    ),
    itemPerPage: Optional[int] = Query(
        10,
        ge=1,
        le=100,
        description="Número de elementos por página (máximo 100)",
        example=20
    ),
    includeInactive: Optional[bool] = Query(
        False,
        description="Si incluir compañías inactivas en el resultado"
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de compañías.
    
    Args:
        search: Término de búsqueda para filtrar por nombre o código/cédula
        sort: Campo y dirección de ordenamiento
        page: Número de página
        itemPerPage: Elementos por página
        includeInactive: Si incluir compañías inactivas
        current_user: Usuario autenticado (dependency)
        
    Returns:
        CompanyListResponse: Respuesta con total y datos paginados
        
    Raises:
        HTTPException: Error 500 si hay problemas con la base de datos
    """
    try:
        # Crear el request object para el stored procedure
        request_data = CompanyListRequest(
            search=search,
            sort=sort,
            page=page,
            itemPerPage=itemPerPage,
            includeInactive=includeInactive
        )
        
        # Convertir a diccionario para el stored procedure
        sp_params = request_data.model_dump(exclude_none=True)
        
        # Ejecutar el stored procedure (asumiendo que existe spCompanyGet)
        result = await execute_sp("spCompanyGet", sp_params)
        
        # Manejar errores del stored procedure
        if isinstance(result, dict) and "error" in result:
            error_msg = result.get("error", "Error desconocido en la base de datos")
            logger.error(f"Error en stored procedure: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al consultar compañías: {error_msg}"
            )
        
        # El resultado ya es el JSON de datos directamente
        data = result
        
        # El stored procedure devuelve un JSON con 'total' y 'data'
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON del stored procedure: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Error en formato de respuesta de la base de datos"
                )
        
        # Validar estructura de respuesta
        if not isinstance(data, dict):
            logger.error(f"Formato de respuesta inválido: {type(data)}")
            raise HTTPException(
                status_code=500,
                detail="Formato de respuesta inválido de la base de datos"
            )
        
        total = data.get("total", 0)
        companies_data = data.get("data", [])
        
        # Asegurar que companies_data es una lista
        if not isinstance(companies_data, list):
            companies_data = []
        
        # Crear y retornar la respuesta
        response = CompanyListResponse(
            total=total,
            data=companies_data
        )
        
        return response
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado consultando compañías: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al consultar compañías"
        )


@router.get(
    "/{company_id}",
    response_model=Company,
    summary="Obtener compañía por ID",
    description="""Obtiene una compañía específica por su ID.
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    
    **Funcionalidad:**
    - Busca la compañía por su ID único
    - Retorna los datos completos de la compañía si existe
    - Error 404 si la compañía no se encuentra
    
    **Respuesta exitosa:**
    - Objeto con los datos completos de la compañía
    - Incluye ID, código/cédula, nombre, descripción y estado activo
    """,
    responses={
        200: {
            "description": "Compañía encontrada",
            "model": Company
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        404: {
            "description": "Compañía no encontrada"
        },
        500: {
            "description": "Error interno del servidor",
            "model": CompanyErrorResponse
        }
    }
)
async def get_company_by_id(
    company_id: int = Path(..., description="ID de la compañía a obtener", example=1),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene una compañía específica por su ID.
    
    Args:
        company_id: ID de la compañía a obtener
        current_user: Usuario autenticado (dependency)
        
    Returns:
        Company: Datos de la compañía
        
    Raises:
        HTTPException: Error 404 si no se encuentra, 500 si hay error de BD
    """
    try:
        # Parámetros para el stored procedure
        sp_params = {"idCompany": company_id}
        
        # Ejecutar el stored procedure (asumiendo que existe spCompanyGetOne)
        result = await execute_sp("spCompanyGetOne", sp_params)
        
        # Manejar errores del stored procedure
        if isinstance(result, dict) and "error" in result:
            error_msg = result.get("error", "Error desconocido en la base de datos")
            logger.error(f"Error en stored procedure: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al consultar compañía: {error_msg}"
            )
        
        # El resultado ya es el JSON de datos directamente
        data = result
        
        # El stored procedure devuelve un JSON con los datos de la compañía
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON del stored procedure: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Error en formato de respuesta de la base de datos"
                )
        
        # Verificar si se encontró la compañía
        if not data or data is None:
            logger.warning(f"Compañía ID {company_id} no encontrada")
            raise HTTPException(
                status_code=404,
                detail=f"Compañía con ID {company_id} no encontrada"
            )
        
        # Retornar los datos de la compañía
        return data
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado consultando compañía ID {company_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al consultar compañía"
        )


@router.post(
    "",
    response_model=CompanyCreateResponse,
    status_code=201,
    summary="Crear nueva compañía",
    description="""Crea una nueva compañía en el sistema.
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    
    **Funcionalidad:**
    - Crea una nueva compañía con los datos proporcionados
    - Valida que los datos sean correctos
    - Retorna el ID de la compañía creada
    
    **Campos requeridos:**
    - `codeCompany`: Código único de la compañía (puede usarse como cédula empresarial - máx. 20 caracteres)
    - `nameCompany`: Nombre de la compañía (máx. 100 caracteres)
    - `descriptionCompany`: Descripción de la compañía (máx. 500 caracteres)
    
    **Respuesta exitosa:**
    - Código HTTP 201 (Created)
    - JSON con el ID de la compañía creada
    """,
    responses={
        201: {
            "description": "Compañía creada exitosamente",
            "model": CompanyCreateResponse
        },
        400: {
            "description": "Datos de entrada inválidos"
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        409: {
            "description": "Conflicto - código/cédula de compañía ya existe"
        },
        500: {
            "description": "Error interno del servidor",
            "model": CompanyErrorResponse
        }
    }
)
async def create_company(
    company: CompanyCreateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Crea una nueva compañía.
    
    Args:
        company: Datos de la compañía a crear
        current_user: Usuario autenticado (dependency)
        
    Returns:
        CompanyCreateResponse: ID de la compañía creada
        
    Raises:
        HTTPException: Error 409 si código ya existe, 500 si hay error de BD
    """
    try:
        # Convertir a diccionario para el stored procedure
        sp_params = company.model_dump()
        
        # Ejecutar el stored procedure
        result = await execute_sp("spCompanyAdd", sp_params)
        
        # Manejar errores del stored procedure
        if isinstance(result, dict) and "error" in result:
            error_msg = result.get("error", "Error desconocido en la base de datos")
            logger.error(f"Error en stored procedure: {error_msg}")
            
            # Si es error de duplicado, retornar 409
            if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                raise HTTPException(
                    status_code=409,
                    detail="El código/cédula de compañía ya existe"
                )
            
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear compañía: {error_msg}"
            )
        
        # El resultado contiene el JSON con el ID
        data = result
        
        # Parsear si es string JSON
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON del stored procedure: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Error en formato de respuesta de la base de datos"
                )
        
        # Obtener el ID de la respuesta
        company_id = data.get("idCompany")
        if company_id is None:
            logger.error("No se recibió ID de compañía en la respuesta")
            raise HTTPException(
                status_code=500,
                detail="Error al obtener ID de la compañía creada"
            )
        
        logger.info(f"Compañía creada exitosamente con ID: {company_id}")
        
        return CompanyCreateResponse(idCompany=company_id)
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado creando compañía: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al crear compañía"
        )


@router.put(
    "/{company_id}",
    summary="Actualizar compañía",
    description="""Actualiza una compañía existente.
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    
    **Funcionalidad:**
    - Actualiza una compañía existente con los datos proporcionados
    - Permite actualización parcial (solo los campos enviados se actualizan)
    - Valida que la compañía exista antes de actualizar
    
    **Campos opcionales:**
    - `codeCompany`: Código de la compañía (puede usarse como cédula empresarial - máx. 20 caracteres)
    - `nameCompany`: Nombre de la compañía (máx. 100 caracteres)  
    - `descriptionCompany`: Descripción de la compañía (máx. 500 caracteres)
    
    **Respuesta exitosa:**
    - Código HTTP 200 (OK)
    - No retorna contenido (operación exitosa sin datos)
    """,
    responses={
        200: {
            "description": "Compañía actualizada exitosamente"
        },
        400: {
            "description": "Datos de entrada inválidos"
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        404: {
            "description": "Compañía no encontrada"
        },
        409: {
            "description": "Conflicto - código/cédula de compañía ya existe"
        },
        500: {
            "description": "Error interno del servidor",
            "model": CompanyErrorResponse
        }
    }
)
async def update_company(
    company_id: int = Path(..., description="ID de la compañía a actualizar", example=1),
    company: CompanyUpdateRequest = ...,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Actualiza una compañía existente.
    
    Args:
        company_id: ID de la compañía a actualizar
        company: Datos de actualización (campos opcionales)
        current_user: Usuario autenticado (dependency)
        
    Raises:
        HTTPException: Error 404 si no se encuentra, 409 si código duplicado, 500 si hay error de BD
    """
    try:
        # Preparar parámetros con ID incluido
        sp_params = company.model_dump(exclude_none=True)
        sp_params["idCompany"] = company_id
        
        # Ejecutar el stored procedure
        result = await execute_sp("spCompanyEdit", sp_params)
        
        # Manejar errores del stored procedure
        if isinstance(result, dict) and "error" in result:
            error_msg = result.get("error", "Error desconocido en la base de datos")
            logger.error(f"Error en stored procedure: {error_msg}")
            
            # Si menciona que no se encontró la compañía
            if "not found" in error_msg.lower() or "no se encontró" in error_msg.lower():
                raise HTTPException(
                    status_code=404,
                    detail=f"Compañía con ID {company_id} no encontrada"
                )
            
            # Si es error de duplicado
            if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                raise HTTPException(
                    status_code=409,
                    detail="El código/cédula de compañía ya existe"
                )
            
            raise HTTPException(
                status_code=500,
                detail=f"Error al actualizar compañía: {error_msg}"
            )
        
        # Si llegamos aquí, la actualización fue exitosa
        logger.info(f"Compañía ID {company_id} actualizada exitosamente")
        
        # Actualización exitosa - no retornar contenido
        return None
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado actualizando compañía ID {company_id}: {str(e)}")
        
        # Verificar si es un error específico de la base de datos
        error_message = str(e).lower()
        if "compañía no encontrada" in error_message or "no se encontró" in error_message:
            raise HTTPException(
                status_code=404,
                detail=f"Compañía con ID {company_id} no encontrada"
            )
        elif "código duplicado" in error_message or "duplicate" in error_message or "unique" in error_message:
            raise HTTPException(
                status_code=409,
                detail="El código/cédula de compañía ya existe"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error interno del servidor al actualizar compañía"
            )


@router.delete(
    "/{company_id}",
    summary="Eliminar compañía (soft delete)",
    description="""Elimina una compañía del sistema (eliminación lógica).
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    
    **Funcionalidad:**
    - Realiza eliminación lógica (soft delete) marcando la compañía como inactiva
    - No elimina físicamente los datos de la base de datos
    - Valida que la compañía exista y esté activa antes de eliminar
    - Permite restauración posterior cambiando el estado a activo
    
    **Comportamiento:**
    - Marca el campo `active = false` en lugar de eliminar el registro
    - Preserva integridad referencial con otras tablas
    - Mantiene historial y auditoría
    
    **Respuesta exitosa:**
    - Código HTTP 200 (OK)
    - No retorna contenido (operación exitosa sin datos)
    """,
    responses={
        200: {
            "description": "Compañía eliminada exitosamente"
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        404: {
            "description": "Compañía no encontrada"
        },
        409: {
            "description": "Conflicto - compañía ya está eliminada"
        },
        500: {
            "description": "Error interno del servidor",
            "model": CompanyErrorResponse
        }
    }
)
async def delete_company(
    company_id: int = Path(..., description="ID de la compañía a eliminar", example=1),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Elimina una compañía (soft delete).
    
    Args:
        company_id: ID de la compañía a eliminar
        current_user: Usuario autenticado (dependency)
        
    Raises:
        HTTPException: Error 404 si no se encuentra, 409 si ya está eliminada, 500 si hay error de BD
    """
    try:
        # Parámetros para el stored procedure
        sp_params = {"idCompany": company_id}
        
        # Ejecutar el stored procedure
        result = await execute_sp("spCompanyDelete", sp_params)
        
        # Manejar errores del stored procedure
        if isinstance(result, dict) and "error" in result:
            error_msg = result.get("error", "Error desconocido en la base de datos")
            logger.error(f"Error en stored procedure: {error_msg}")
            
            # Si menciona que no se encontró la compañía
            if "not found" in error_msg.lower() or "no se encontró" in error_msg.lower():
                raise HTTPException(
                    status_code=404,
                    detail=f"Compañía con ID {company_id} no encontrada"
                )
            
            # Si la compañía ya está eliminada
            if "ya está eliminada" in error_msg.lower() or "already deleted" in error_msg.lower():
                raise HTTPException(
                    status_code=409,
                    detail=f"La compañía con ID {company_id} ya está eliminada"
                )
            
            raise HTTPException(
                status_code=500,
                detail=f"Error al eliminar compañía: {error_msg}"
            )
        
        # Si llegamos aquí, la eliminación fue exitosa
        logger.info(f"Compañía ID {company_id} eliminada exitosamente (soft delete)")
        
        # Eliminación exitosa - no retornar contenido
        return None
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado eliminando compañía ID {company_id}: {str(e)}")
        
        # Verificar si es un error específico de la base de datos
        error_message = str(e).lower()
        if "compañía no encontrada" in error_message or "no se encontró" in error_message:
            raise HTTPException(
                status_code=404,
                detail=f"Compañía con ID {company_id} no encontrada"
            )
        elif "ya está eliminada" in error_message or "already deleted" in error_message:
            raise HTTPException(
                status_code=409,
                detail=f"La compañía con ID {company_id} ya está eliminada"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error interno del servidor al eliminar compañía"
            )