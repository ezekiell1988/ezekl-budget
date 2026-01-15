"""
Endpoints para gestión de cuentas contables.
Proporciona funcionalidad para consultar el catálogo de cuentas contables con paginación.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import Optional
import json
import logging
from app.database.connection import execute_sp
from app.utils.auth import get_current_user
from app.models.accounting_account import (
    AccountingAccountRequest,
    AccountingAccountResponse,
    AccountingAccountCreateRequest,
    AccountingAccountUpdateRequest,
    AccountingAccountCreateResponse,
    AccountingAccountErrorResponse
)
from app.models.auth import CurrentUser

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de cuentas contables
router = APIRouter(prefix="/accounting-accounts", tags=["Cuentas Contables"])


@router.get(
    ".json",
    response_model=AccountingAccountResponse,
    summary="Obtener cuentas contables con estructura jerárquica",
    description="""Obtiene una lista de cuentas contables del catálogo con su estructura jerárquica completa.
    
    Este endpoint permite consultar el catálogo de cuentas contables con las siguientes características:
    
    **Funcionalidades:**
    - Estructura jerárquica completa (cuentas padre e hijas anidadas)
    - Paginación configurable (página y elementos por página)
    - Búsqueda recursiva por nombre de cuenta (incluye descendientes)
    - Ordenamiento por diferentes campos (ID, código, nombre)
    - Filtrado por estado activo/inactivo
    - Búsqueda que mantiene la jerarquía (si un hijo coincide, muestra toda la rama)
    
    **Parámetros de ordenamiento disponibles:**
    - `idAccountingAccount_asc`: Por ID ascendente
    - `idAccountingAccountFather_asc`: Por ID padre ascendente
    - `idAccountingAccountFather_desc`: Por ID padre descendente
    - `codeAccountingAccount_asc`: Por código ascendente
    - `codeAccountingAccount_desc`: Por código descendente
    - `nameAccountingAccount_asc`: Por nombre ascendente (default)
    - `nameAccountingAccount_desc`: Por nombre descendente
    
    **Estructura de respuesta:**
    - Cada cuenta incluye: ID, ID padre, código, nombre, estado activo
    - Propiedad `children`: array recursivo de cuentas hijas
    - Preserva la jerarquía completa durante filtrados y búsquedas
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Paginación:**
    - `page`: Número de página (inicia en 1, default: 1)
    - `itemPerPage`: Elementos por página (1-100, default: 10)
    
    **Respuesta:**
    - `total`: Total de registros que coinciden con el filtro
    - `data`: Array de cuentas contables para la página solicitada
    
    **Ejemplos de uso:**
    - Obtener primeras 10 cuentas: `GET /accounting-accounts`
    - Buscar cuentas con "caja": `GET /accounting-accounts?search=caja`
    - Página 2 con 25 elementos: `GET /accounting-accounts?page=2&itemPerPage=25`
    - Ordenar por nombre desc: `GET /accounting-accounts?sort=nameAccountingAccount_desc`
    """,
    responses={
        200: {
            "description": "Lista de cuentas contables obtenida exitosamente",
            "model": AccountingAccountResponse
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        500: {
            "description": "Error interno del servidor",
            "model": AccountingAccountErrorResponse
        }
    }
)
async def get_accounting_accounts(
    search: Optional[str] = Query(
        None,
        description="Término de búsqueda para filtrar por nombre de cuenta",
        max_length=50,
        example="caja"
    ),
    sort: Optional[str] = Query(
        "nameAccountingAccount_asc",
        description="Campo y dirección de ordenamiento",
        regex="^(idAccountingAccount_asc|idAccountingAccountFather_asc|idAccountingAccountFather_desc|codeAccountingAccount_asc|codeAccountingAccount_desc|nameAccountingAccount_asc|nameAccountingAccount_desc)$",
        example="nameAccountingAccount_asc"
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
        description="Incluir cuentas inactivas en los resultados",
        example=False
    ),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de cuentas contables con estructura jerárquica.
    
    Args:
        search: Término de búsqueda para filtrar por nombre
        sort: Campo y dirección de ordenamiento
        page: Número de página
        itemPerPage: Elementos por página
        includeInactive: Incluir cuentas inactivas
        current_user: Usuario autenticado (dependency)
        
    Returns:
        AccountingAccountResponse: Respuesta con total y datos jerárquicos
        
    Raises:
        HTTPException: Error 500 si hay problemas con la base de datos
    """
    try:
        
        # Crear el request object para el stored procedure
        request_data = AccountingAccountRequest(
            search=search,
            sort=sort,
            page=page,
            itemPerPage=itemPerPage,
            includeInactive=includeInactive,
            noQuery=False
        )
        
        # Convertir a diccionario para el stored procedure
        sp_params = request_data.model_dump(exclude_none=True)
        
        
        # Ejecutar el stored procedure
        result = await execute_sp("spAccountingAccountGet", sp_params)
        
        # Los stored procedures de cuentas contables devuelven directamente el JSON de datos
        # No tienen la estructura {"success": bool, "data": ...} como otros endpoints
        if isinstance(result, dict) and "error" in result:
            error_msg = result.get("error", "Error desconocido en la base de datos")
            logger.error(f"Error en stored procedure: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al consultar cuentas contables: {error_msg}"
            )
        
        # El resultado ya es el JSON de datos directamente
        data = result
        
        # El stored procedure devuelve un JSON con 'total' y 'data'
        if isinstance(data, str):
            # Si viene como string JSON, parsearlo
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
        accounts_data = data.get("data", [])
        
        # Asegurar que accounts_data es una lista
        if not isinstance(accounts_data, list):
            accounts_data = []
        
        
        # Crear y retornar la respuesta
        response = AccountingAccountResponse(
            total=total,
            data=accounts_data
        )
        
        return response
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado consultando cuentas contables: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al consultar cuentas contables"
        )


@router.get(
    "/{account_id}/accounting-account.json",
    summary="Obtener cuenta contable por ID",
    description="""Obtiene una cuenta contable específica por su ID.
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    
    **Funcionalidad:**
    - Busca la cuenta contable por su ID único
    - Retorna los datos completos de la cuenta si existe
    - Error 404 si la cuenta no se encuentra
    
    **Respuesta exitosa:**
    - Objeto con los datos completos de la cuenta contable
    - Incluye ID, código y nombre de la cuenta
    """,
    responses={
        200: {
            "description": "Cuenta contable encontrada",
            "model": dict
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        404: {
            "description": "Cuenta contable no encontrada"
        },
        500: {
            "description": "Error interno del servidor",
            "model": AccountingAccountErrorResponse
        }
    }
)
async def get_accounting_account_by_id(
    account_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtiene una cuenta contable específica por su ID.
    
    Args:
        account_id: ID de la cuenta contable a obtener
        current_user: Usuario autenticado (dependency)
        
    Returns:
        AccountingAccount: Datos de la cuenta contable
        
    Raises:
        HTTPException: Error 404 si no se encuentra, 500 si hay error de BD
    """
    try:
        
        # Parámetros para el stored procedure
        sp_params = {"idAccountingAccount": account_id}
        
        
        # Ejecutar el stored procedure
        result = await execute_sp("spAccountingAccountGetOne", sp_params)
        
        if not result.get("success", False):
            error_msg = result.get("message", "Error desconocido en la base de datos")
            logger.error(f"Error en stored procedure: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al consultar cuenta contable: {error_msg}"
            )
        
        # Obtener los datos del resultado
        data = result.get("data", {})
        
        # El stored procedure devuelve un JSON con los datos de la cuenta
        if isinstance(data, str):
            # Si viene como string JSON, parsearlo
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON del stored procedure: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Error en formato de respuesta de la base de datos"
                )
        
        # Verificar si se encontró la cuenta
        if not data or data is None:
            logger.warning(f"Cuenta contable ID {account_id} no encontrada")
            raise HTTPException(
                status_code=404,
                detail=f"Cuenta contable con ID {account_id} no encontrada"
            )
        
        
        # Retornar los datos de la cuenta
        return data
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado consultando cuenta ID {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al consultar cuenta contable"
        )


@router.post(
    "",
    response_model=AccountingAccountCreateResponse,
    summary="Crear nueva cuenta contable",
    description="""Crea una nueva cuenta contable en el catálogo.
    
    Este endpoint permite crear una nueva cuenta contable con las siguientes características:
    
    **Funcionalidades:**
    - Creación de cuentas contables padre o hija
    - Validación de estructura jerárquica
    - Códigos únicos de cuenta contable
    
    **Validaciones:**
    - El código de cuenta contable debe ser único
    - Si se especifica padre, debe existir y estar activo
    - Los nombres deben ser descriptivos
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Ejemplo de uso:**
    ```json
    {
        "idAccountingAccountFather": 1,
        "codeAccountingAccount": "001-002",
        "nameAccountingAccount": "Bancos"
    }
    ```
    """,
    responses={
        201: {
            "description": "Cuenta contable creada exitosamente",
            "model": AccountingAccountCreateResponse
        },
        400: {
            "description": "Datos de entrada inválidos"
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        409: {
            "description": "El código de cuenta contable ya existe"
        },
        500: {
            "description": "Error interno del servidor",
            "model": AccountingAccountErrorResponse
        }
    },
    status_code=201
)
async def create_accounting_account(
    account_data: AccountingAccountCreateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Crea una nueva cuenta contable.
    
    Args:
        account_data: Datos de la cuenta contable a crear
        current_user: Usuario autenticado (dependency)
        
    Returns:
        AccountingAccountCreateResponse: Respuesta con ID de la cuenta creada
        
    Raises:
        HTTPException: Error 400 para datos inválidos, 409 para duplicados, 500 para errores de BD
    """
    try:
        # Convertir a diccionario para el stored procedure
        sp_params = account_data.model_dump(exclude_none=True)
        
        # Ejecutar el stored procedure de creación
        result = await execute_sp("spAccountingAccountAdd", sp_params)
        
        # Verificar si hubo errores en la base de datos
        if isinstance(result, dict) and "error" in result:
            error_msg = result.get("error", "Error desconocido en la base de datos")
            logger.error(f"Error en stored procedure de creación: {error_msg}")
            
            # Analizar el tipo de error para devolver status code apropiado
            if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                raise HTTPException(
                    status_code=409,
                    detail="El código de cuenta contable ya existe"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al crear cuenta contable: {error_msg}"
                )
        
        # Obtener el ID generado
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON del stored procedure: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Error en formato de respuesta de la base de datos"
                )
        
        # Validar que se obtuvo el ID
        if not isinstance(result, dict) or "idAccountingAccount" not in result:
            logger.error(f"Formato de respuesta inválido: {result}")
            raise HTTPException(
                status_code=500,
                detail="Error en formato de respuesta de la base de datos"
            )
        
        created_id = result["idAccountingAccount"]
        
        return AccountingAccountCreateResponse(
            idAccountingAccount=created_id
        )
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado creando cuenta contable: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al crear cuenta contable"
        )


@router.put(
    "/{account_id}",
    summary="Actualizar cuenta contable",
    description="""Actualiza una cuenta contable existente por su ID.
    
    Este endpoint permite actualizar una cuenta contable con las siguientes características:
    
    **Funcionalidades:**
    - Actualización parcial (solo campos especificados)
    - Validación de estructura jerárquica
    - Preservación de integridad de datos
    
    **Validaciones:**
    - La cuenta contable debe existir
    - El código debe ser único si se especifica
    - Si se cambia el padre, debe existir y estar activo
    - No se puede crear referencias circulares
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Ejemplo de uso:**
    ```json
    {
        "nameAccountingAccount": "Caja Principal Actualizada"
    }
    ```
    """,
    responses={
        200: {
            "description": "Cuenta contable actualizada exitosamente"
        },
        400: {
            "description": "Datos de entrada inválidos"
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        404: {
            "description": "Cuenta contable no encontrada"
        },
        409: {
            "description": "El código de cuenta contable ya existe"
        },
        500: {
            "description": "Error interno del servidor",
            "model": AccountingAccountErrorResponse
        }
    }
)
async def update_accounting_account(
    account_id: int = Path(..., description="ID de la cuenta contable a actualizar"),
    account_data: AccountingAccountUpdateRequest = ...,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Actualiza una cuenta contable existente.
    
    Args:
        account_id: ID de la cuenta contable a actualizar
        account_data: Datos de la cuenta contable a actualizar
        current_user: Usuario autenticado (dependency)
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Error 404 si no existe, 400 para datos inválidos, 409 para duplicados, 500 para errores de BD
    """
    try:
        # Convertir a diccionario para el stored procedure
        sp_params = account_data.model_dump(exclude_none=True)
        sp_params["idAccountingAccount"] = account_id
        
        # Ejecutar el stored procedure de actualización
        result = await execute_sp("spAccountingAccountEdit", sp_params)
        
        # Verificar si hubo errores en la base de datos
        if isinstance(result, dict) and "error" in result:
            error_msg = result.get("error", "Error desconocido en la base de datos")
            logger.error(f"Error en stored procedure de actualización: {error_msg}")
            
            # Analizar el tipo de error para devolver status code apropiado
            if "not found" in error_msg.lower() or "no encontr" in error_msg.lower():
                raise HTTPException(
                    status_code=404,
                    detail=f"Cuenta contable con ID {account_id} no encontrada"
                )
            elif "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                raise HTTPException(
                    status_code=409,
                    detail="El código de cuenta contable ya existe"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al actualizar cuenta contable: {error_msg}"
                )
        
        # La actualización fue exitosa
        return {
            "message": f"Cuenta contable ID {account_id} actualizada exitosamente"
        }
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado actualizando cuenta ID {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al actualizar cuenta contable"
        )


@router.delete(
    "/{account_id}",
    summary="Eliminar cuenta contable",
    description="""Elimina una cuenta contable por su ID.
    
    Este endpoint permite eliminar una cuenta contable con las siguientes características:
    
    **Funcionalidades:**
    - Eliminación segura con validaciones
    - Verificación de dependencias (cuentas hijas)
    - Preservación de integridad referencial
    
    **Validaciones:**
    - La cuenta contable debe existir
    - No debe tener cuentas hijas dependientes
    - No debe estar siendo utilizada en transacciones
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Nota importante:**
    - Esta operación no es reversible
    - Se recomienda desactivar la cuenta en lugar de eliminarla si tiene historial
    """,
    responses={
        200: {
            "description": "Cuenta contable eliminada exitosamente"
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        404: {
            "description": "Cuenta contable no encontrada"
        },
        409: {
            "description": "No se puede eliminar: tiene cuentas dependientes"
        },
        500: {
            "description": "Error interno del servidor",
            "model": AccountingAccountErrorResponse
        }
    }
)
async def delete_accounting_account(
    account_id: int = Path(..., description="ID de la cuenta contable a eliminar"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Elimina una cuenta contable.
    
    Args:
        account_id: ID de la cuenta contable a eliminar
        current_user: Usuario autenticado (dependency)
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Error 404 si no existe, 409 si tiene dependencias, 500 para errores de BD
    """
    try:
        # Parámetros para el stored procedure
        sp_params = {"idAccountingAccount": account_id}
        
        # Ejecutar el stored procedure de eliminación
        result = await execute_sp("spAccountingAccountDelete", sp_params)
        
        # Verificar si hubo errores en la base de datos
        if isinstance(result, dict) and "error" in result:
            error_msg = result.get("error", "Error desconocido en la base de datos")
            logger.error(f"Error en stored procedure de eliminación: {error_msg}")
            
            # Analizar el tipo de error para devolver status code apropiado
            if "not found" in error_msg.lower() or "no encontr" in error_msg.lower():
                raise HTTPException(
                    status_code=404,
                    detail=f"Cuenta contable con ID {account_id} no encontrada"
                )
            elif "dependientes" in error_msg.lower() or "children" in error_msg.lower():
                raise HTTPException(
                    status_code=409,
                    detail="No se puede eliminar la cuenta contable porque tiene cuentas dependientes"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al eliminar cuenta contable: {error_msg}"
                )
        
        # La eliminación fue exitosa
        return {
            "message": f"Cuenta contable ID {account_id} eliminada exitosamente"
        }
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except Exception as e:
        logger.error(f"Error inesperado eliminando cuenta ID {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al eliminar cuenta contable"
        )
