"""
Endpoints para gestión de tipos de entrega de productos.
Proporciona funcionalidad para actualizar los tipos de entrega asociados a productos.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Path
from app.utils.auth import get_current_user
from app.models.auth import CurrentUser
from app.models.product_delivery_type import (
    ProductDeliveryTypeUpdateRequest,
    ProductDeliveryTypeResponse
)
from app.services.product_delivery_type_service import update_product_delivery_type
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de tipos de entrega de productos
router = APIRouter(prefix="/product/delivery-type", tags=["Tipos de Entrega de Productos"])


@router.put(
    "/{idProduct}",
    response_model=ProductDeliveryTypeResponse,
    summary="Actualizar tipos de entrega de producto",
    description="""Actualiza los tipos de entrega asociados a un producto específico.
    
    Este endpoint permite modificar la configuración de tipos de entrega de un producto:
    
    **Características:**
    - Asocia múltiples tipos de entrega a un producto
    - Cada tipo de entrega puede estar activo o inactivo
    - Cada tipo de entrega tiene un precio asociado
    - Valida pertenencia del producto a la compañía
    - Actualiza tanto el estado activo como el precio
    
    **Parámetros:**
    - **idProduct** (path): ID del producto a actualizar
    
    **Body:**
    - **deliveryType**: Array de tipos de entrega con:
      - **idDeliveryType**: ID del tipo de entrega
      - **active**: Estado activo/inactivo
      - **price**: Precio del tipo de entrega
      - **idProductDeliveryType**: ID de la relación existente
    
    **Validaciones:**
    - El producto debe existir y pertenecer a la compañía
    - Los precios deben ser valores positivos o cero
    - Los IDs de relación deben existir
    
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
    - **401**: Token inválido o expirado
    - **404**: Producto no encontrado o no pertenece a la compañía
    - **500**: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Tipos de entrega actualizados exitosamente",
            "content": {
                "application/json": {
                    "example": {"idProduct": 34}
                }
            }
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
async def update_delivery_types(
    idProduct: int = Path(
        ...,
        description="ID del producto a actualizar",
        gt=0,
        example=34
    ),
    request: ProductDeliveryTypeUpdateRequest = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Actualiza los tipos de entrega de un producto específico.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Convertir a diccionarios
        delivery_types = [
            item.model_dump() 
            for item in request.deliveryType
        ]
        
        # Actualizar tipos de entrega
        result = await update_product_delivery_type(
            id_product=idProduct,
            id_company=id_company,
            delivery_types=delivery_types
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al actualizar tipos de entrega: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar tipos de entrega del producto: {str(e)}"
        )
