"""
Endpoints para gestión de cuentas contables de productos.
Proporciona funcionalidad para actualizar las cuentas contables asociadas a productos.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Path
from app.utils.auth import get_current_user
from app.models.auth import CurrentUser
from app.models.product_accounting_account import (
    ProductAccountingAccountUpdateRequest,
    ProductAccountingAccountResponse
)
from app.services.product_accounting_account_service import update_product_accounting_account
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de cuentas contables de productos
router = APIRouter(prefix="/product-accounting-account", tags=["Cuentas Contables de Productos"])


@router.put(
    "/{idProduct}",
    response_model=ProductAccountingAccountResponse,
    summary="Actualizar cuentas contables de producto",
    description="""Actualiza las cuentas contables asociadas a un producto específico.
    
    Este endpoint permite modificar la distribución de cuentas contables de un producto:
    
    **Características:**
    - Asocia múltiples cuentas contables a un producto
    - Cada cuenta tiene un efecto (1=débito, -1=crédito) y un porcentaje
    - Los porcentajes deben sumar exactamente 100% para cada efecto
    - Valida pertenencia del producto a la compañía
    - Maneja automáticamente la creación/actualización de relaciones
    
    **Parámetros:**
    - **idProduct** (path): ID del producto a actualizar
    
    **Body:**
    - **accountingAccount**: Array de cuentas contables con:
      - **idAccountingAccount**: ID de la cuenta contable
      - **effect**: 1 (débito) o -1 (crédito)
      - **percent**: Porcentaje de distribución (0-100)
      - **idProductAccountingAccount**: ID de la relación (null para nuevas)
    
    **Validaciones:**
    - Se requieren mínimo 2 cuentas contables
    - Los porcentajes por cada efecto deben sumar exactamente 100
    - El efecto debe ser 1 o -1
    - El producto debe existir y pertenecer a la compañía
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Respuesta exitosa (200):**
    ```json
    {
        "idProduct": 34
    }
    ```
    
    **Errores posibles:**
    - **400**: Porcentajes inválidos o no suman 100
    - **401**: Token inválido o expirado
    - **404**: Producto no encontrado o no pertenece a la compañía
    - **500**: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Cuentas contables actualizadas exitosamente",
            "content": {
                "application/json": {
                    "example": {"idProduct": 34}
                }
            }
        },
        400: {
            "description": "Error de validación - Porcentajes inválidos"
        },
        401: {
            "description": "No autorizado - Token inválido o expirado"
        },
        404: {
            "description": "Producto no encontrado"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def update_accounting_accounts(
    idProduct: int = Path(
        ...,
        description="ID del producto a actualizar",
        gt=0,
        example=34
    ),
    request: ProductAccountingAccountUpdateRequest = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Actualiza las cuentas contables de un producto específico.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Convertir a diccionarios
        accounting_accounts = [
            item.model_dump(exclude_none=True) 
            for item in request.accountingAccount
        ]
        
        # Actualizar cuentas contables
        result = await update_product_accounting_account(
            id_product=idProduct,
            id_company=id_company,
            accounting_accounts=accounting_accounts
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        error_message = str(e)
        status_code = 400 if "porcentajes" in error_message.lower() else 404
        raise HTTPException(status_code=status_code, detail=error_message)
    except Exception as e:
        logger.error(f"Error al actualizar cuentas contables: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar cuentas contables del producto: {str(e)}"
        )
