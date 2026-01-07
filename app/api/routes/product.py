"""
Endpoints para gestión de productos.
Proporciona funcionalidad CRUD completa para productos con estructura jerárquica.
"""

import logging
import json
from fastapi import APIRouter, HTTPException, Depends, Path
from typing import List, Dict
from app.database.connection import execute_sp
from app.utils.auth import get_current_user
from app.models.auth import CurrentUser
from app.models.product import (
    Product,
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductCreateResponse,
    ProductErrorResponse
)

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de productos
router = APIRouter(prefix="/products", tags=["Productos"])


@router.get(
    ".json",
    response_model=List[Product],
    summary="Obtener productos con estructura jerárquica",
    description="""Obtiene todos los productos organizados en estructura de árbol.
    
    Este endpoint retorna los productos con su jerarquía completa:
    
    **Características:**
    - Estructura jerárquica completa (padres e hijos)
    - Los productos raíz tienen `childrens` como lista de productos hijos
    - Los productos sin hijos tienen `childrens` como `null`
    - Estructura recursiva ilimitada
    
    **Autenticación:**
    - Requiere token JWT válido en el header Authorization
    - Header: `Authorization: Bearer {token}`
    
    **Respuesta:**
    - Array de productos raíz con sus respectivos hijos anidados
    
    **Ejemplo de estructura:**
    ```json
    [
      {
        "idProduct": 1,
        "nameProduct": "Gastos generales",
        "descriptionProduct": "Gastos generales en familia",
        "childrens": [
          {
            "idProduct": 2,
            "nameProduct": "Alimentación",
            "descriptionProduct": "Alimentación",
            "childrens": null
          }
        ]
      }
    ]
    ```
    """,
    responses={
        200: {
            "description": "Lista de productos obtenida exitosamente"
        },
        401: {
            "description": "Token de autorización requerido, inválido o expirado"
        },
        500: {
            "description": "Error interno del servidor",
            "model": ProductErrorResponse
        }
    }
)
async def get_products():
    """
    Obtener todos los productos con estructura jerárquica.
    """
    try:
        
        # Preparar parámetros para el SP
        params = {
            "json": "{}"
        }
        
        # Ejecutar stored procedure
        result = await execute_sp("spProductGet", params)
        
        if not result:
            logger.warning("No se encontraron productos")
            return []
        
        # El execute_sp ya parsea el JSON automáticamente
        # Si viene como campo 'json', lo parseamos, sino lo retornamos directo
        if isinstance(result, list) and len(result) > 0:
            # Si el primer elemento tiene un campo 'json', lo parseamos
            if isinstance(result[0], dict) and 'json' in result[0]:
                products_json = result[0]['json']
                if not products_json:
                    logger.warning("JSON de productos vacío")
                    return []
                products_data = json.loads(products_json)
            else:
                # Ya viene parseado como lista de diccionarios
                products_data = result
        else:
            logger.warning("Resultado vacío")
            return []
        
        # Asegurar que es una lista
        if not isinstance(products_data, list):
            products_data = [products_data] if products_data else []
        
        logger.info(f"Productos obtenidos: {len(products_data)} productos raíz")
        return products_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON de productos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la respuesta del servidor: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error al obtener productos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener productos: {str(e)}"
        )


@router.get(
    "/{idProduct}",
    response_model=Dict,
    summary="Obtener detalle completo de un producto",
    description="""Obtiene el detalle completo de un producto por su ID.
    
    **Autenticación:**
    - Requiere token JWT válido
    
    **Parámetros:**
    - `idProduct`: ID del producto a consultar
    
    **Respuesta:**
    - Producto con toda su información incluyendo cuentas contables, precios de entrega y productos requeridos
    """,
    responses={
        200: {
            "description": "Producto obtenido exitosamente"
        },
        401: {
            "description": "No autorizado"
        },
        404: {
            "description": "Producto no encontrado",
            "model": ProductErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ProductErrorResponse
        }
    }
)
async def get_product(
    idProduct: int = Path(description="ID del producto", ge=1),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Obtener el detalle completo de un producto específico por ID.
    """
    try:
        logger.info(f"Usuario {current_user.user.idLogin} solicitando producto {idProduct}")
        
        # Preparar parámetros para el SP
        params = {
            "idProduct": idProduct
        }
        
        logger.info(f"Parámetros para SP: {params}")
        
        # Ejecutar stored procedure
        result = await execute_sp("spProductGetOne", params)
        
        logger.info(f"Resultado del SP - Tipo: {type(result)}, Contenido: {result}")
        
        if not result:
            logger.warning(f"Producto {idProduct} no encontrado - resultado vacío")
            raise HTTPException(
                status_code=404,
                detail=f"Producto con ID {idProduct} no encontrado"
            )
        
        # El execute_sp ya devuelve el diccionario parseado directamente
        # Solo verificamos que tenga datos válidos
        if isinstance(result, dict):
            # Verificar si es la respuesta de éxito sin datos
            if result.get('success') and len(result) == 1:
                logger.warning(f"Producto {idProduct} no encontrado - solo success")
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto con ID {idProduct} no encontrado"
                )
            # Si tiene más campos, es un producto válido
            product_data = result
        else:
            logger.warning(f"Tipo de resultado inesperado: {type(result)}")
            raise HTTPException(
                status_code=500,
                detail="Error al procesar la respuesta del servidor"
            )
        
        logger.info(f"Producto {idProduct} obtenido exitosamente")
        return product_data
        
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON del producto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la respuesta del servidor: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error al obtener producto {idProduct}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener producto: {str(e)}"
        )


@router.post(
    "",
    response_model=ProductCreateResponse,
    status_code=201,
    summary="Crear nuevo producto",
    description="""Crea un nuevo producto en el sistema.
    
    **Autenticación:**
    - Requiere token JWT válido
    
    **Body:**
    - `nameProduct`: Nombre del producto (requerido)
    - `descriptionProduct`: Descripción del producto (requerido)
    - `idProductFather`: ID del producto padre (opcional, null para productos raíz)
    
    **Respuesta:**
    - `idProduct`: ID del producto creado
    """,
    responses={
        201: {
            "description": "Producto creado exitosamente"
        },
        400: {
            "description": "Datos inválidos",
            "model": ProductErrorResponse
        },
        401: {
            "description": "No autorizado"
        },
        500: {
            "description": "Error interno del servidor",
            "model": ProductErrorResponse
        }
    }
)
async def create_product(
    product: ProductCreateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Crear un nuevo producto.
    """
    try:
        logger.info(f"Usuario {current_user.user.idLogin} creando producto: {product.nameProduct}")
        
        # Preparar parámetros para el SP
        params = {
            "idProductFather": product.idProductFather,
            "nameProduct": product.nameProduct,
            "descriptionProduct": product.descriptionProduct,
            "idCompany": current_user.user.idCompany
        }
        
        # Ejecutar stored procedure
        result = await execute_sp("spProductAdd", params)
        
        if not result or "idProduct" not in result[0]:
            raise HTTPException(
                status_code=500,
                detail="Error al crear producto: respuesta inválida del servidor"
            )
        
        id_product = result[0]["idProduct"]
        logger.info(f"Producto creado con ID: {id_product}")
        
        return ProductCreateResponse(idProduct=id_product)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear producto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear producto: {str(e)}"
        )


@router.put(
    "/{idProduct}",
    status_code=204,
    summary="Actualizar producto existente",
    description="""Actualiza un producto existente.
    
    **Autenticación:**
    - Requiere token JWT válido
    
    **Parámetros:**
    - `idProduct`: ID del producto a actualizar
    
    **Body (todos opcionales):**
    - `nameProduct`: Nuevo nombre del producto
    - `descriptionProduct`: Nueva descripción
    - `idProductFather`: Nuevo ID del producto padre
    
    **Respuesta:**
    - 204 No Content si la actualización fue exitosa
    """,
    responses={
        204: {
            "description": "Producto actualizado exitosamente"
        },
        400: {
            "description": "Datos inválidos",
            "model": ProductErrorResponse
        },
        401: {
            "description": "No autorizado"
        },
        404: {
            "description": "Producto no encontrado",
            "model": ProductErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ProductErrorResponse
        }
    }
)
async def update_product(
    idProduct: int = Path(description="ID del producto a actualizar", ge=1),
    product: ProductUpdateRequest = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Actualizar un producto existente.
    """
    try:
        logger.info(f"Usuario {current_user.user.idLogin} actualizando producto {idProduct}")
        
        # Preparar parámetros para el SP (solo enviar campos que no sean None)
        params = {
            "idProduct": idProduct,
            "idCompany": current_user.user.idCompany
        }
        
        if product.idProductFather is not None:
            params["idProductFather"] = product.idProductFather
        if product.nameProduct is not None:
            params["nameProduct"] = product.nameProduct
        if product.descriptionProduct is not None:
            params["descriptionProduct"] = product.descriptionProduct
        
        # Ejecutar stored procedure
        await execute_sp("spProductEdit", params)
        
        logger.info(f"Producto {idProduct} actualizado exitosamente")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar producto {idProduct}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar producto: {str(e)}"
        )


@router.delete(
    "/{idProduct}",
    status_code=204,
    summary="Eliminar producto",
    description="""Elimina un producto del sistema.
    
    **Autenticación:**
    - Requiere token JWT válido
    
    **Parámetros:**
    - `idProduct`: ID del producto a eliminar
    
    **Nota:**
    - Si el producto tiene hijos, el comportamiento depende del SP
    - Puede ser eliminación en cascada o restricción
    
    **Respuesta:**
    - 204 No Content si la eliminación fue exitosa
    """,
    responses={
        204: {
            "description": "Producto eliminado exitosamente"
        },
        401: {
            "description": "No autorizado"
        },
        404: {
            "description": "Producto no encontrado",
            "model": ProductErrorResponse
        },
        409: {
            "description": "Conflicto - El producto tiene dependencias",
            "model": ProductErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ProductErrorResponse
        }
    }
)
async def delete_product(
    idProduct: int = Path(description="ID del producto a eliminar", ge=1),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Eliminar un producto.
    """
    try:
        logger.info(f"Usuario {current_user.user.idLogin} eliminando producto {idProduct}")
        
        # Preparar parámetros para el SP
        params = {
            "idProduct": idProduct,
            "idCompany": current_user.user.idCompany
        }
        
        # Ejecutar stored procedure
        await execute_sp("spProductDelete", params)
        
        logger.info(f"Producto {idProduct} eliminado exitosamente")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar producto {idProduct}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar producto: {str(e)}"
        )
