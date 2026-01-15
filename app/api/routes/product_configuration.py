"""
Endpoints para gestión de configuración de productos.
Proporciona funcionalidad para actualizar la configuración de productos.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Path
from app.utils.auth import get_current_user
from app.models.auth import CurrentUser
from app.models.product_configuration import (
    ProductConfigurationUpdateRequest,
    ProductConfigurationResponse
)
from app.services.product_configuration_service import update_product_configuration
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de configuración de productos
router = APIRouter(prefix="/product-configuration", tags=["Configuración de Productos"])


@router.put(
    "/{idProduct}",
    response_model=ProductConfigurationResponse,
    summary="Actualizar configuración de producto",
    description="""Actualiza la configuración de un producto específico.
    
    Este endpoint permite modificar las propiedades de configuración de un producto:
    
    **Características:**
    - Actualiza configuraciones del producto (isMainCategory, isCategory, etc.)
    - Validación de pertenencia del producto a la compañía
    - Todos los campos son opcionales para actualización parcial
    
    **Parámetros:**
    - **idProduct** (path): ID del producto a actualizar
    
    **Body:**
    - Campos de configuración a actualizar (todos opcionales)
    
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
            "description": "Configuración actualizada exitosamente",
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
async def update_configuration(
    idProduct: int = Path(
        ...,
        description="ID del producto a actualizar",
        gt=0,
        example=34
    ),
    configuration: ProductConfigurationUpdateRequest = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Actualiza la configuración de un producto específico.
    """
    try:
        # Obtener idCompany desde settings
        id_company = settings.idCompany
        
        # Preparar datos de configuración (solo campos no None)
        config_data = configuration.model_dump(exclude_none=True)
        
        # Actualizar configuración
        result = await update_product_configuration(
            id_product=idProduct,
            id_company=id_company,
            configuration_data=config_data
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al actualizar configuración: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar configuración del producto: {str(e)}"
        )
