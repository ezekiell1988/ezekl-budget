"""
Endpoints para gestión de cuentas contables.
Proporciona funcionalidad para consultar el catálogo de cuentas contables con paginación.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict
import json
import logging
from app.database.connection import execute_sp
from app.api.routes.auth import get_current_user
from app.models.accounting_account import (
    AccountingAccountRequest,
    AccountingAccountResponse,
    AccountingAccountErrorResponse
)

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de cuentas contables
router = APIRouter()


@router.get(
    "",
    response_model=AccountingAccountResponse,
    summary="Obtener cuentas contables paginadas",
    description="""Obtiene una lista paginada de cuentas contables del catálogo de cuentas.
    
    Este endpoint permite consultar el catálogo de cuentas contables con las siguientes características:
    
    **Funcionalidades:**
    - Paginación configurable (página y elementos por página)
    - Búsqueda por nombre de cuenta (búsqueda parcial, case-insensitive)
    - Ordenamiento por diferentes campos (ID, código, nombre)
    - Filtrado por texto en el nombre de la cuenta
    
    **Parámetros de ordenamiento disponibles:**
    - `idAccountingAccount_asc`: Por ID ascendente
    - `codeAccountingAccount_asc`: Por código ascendente (default)
    - `codeAccountingAccount_desc`: Por código descendente
    - `nameAccountingAccount_asc`: Por nombre ascendente
    - `nameAccountingAccount_desc`: Por nombre descendente
    
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
        "codeAccountingAccount_asc",
        description="Campo y dirección de ordenamiento",
        regex="^(idAccountingAccount_asc|codeAccountingAccount_asc|codeAccountingAccount_desc|nameAccountingAccount_asc|nameAccountingAccount_desc)$",
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
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de cuentas contables.
    
    Args:
        search: Término de búsqueda para filtrar por nombre
        sort: Campo y dirección de ordenamiento
        page: Número de página
        itemPerPage: Elementos por página
        current_user: Usuario autenticado (dependency)
        
    Returns:
        AccountingAccountResponse: Respuesta con total y datos paginados
        
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
    "/{account_id}",
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
    current_user: Dict = Depends(get_current_user)
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
