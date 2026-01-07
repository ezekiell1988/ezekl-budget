"""
Inicialización del módulo SharePoint.
Exporta el router principal para las rutas de SharePoint.
"""

from fastapi import APIRouter
from .demo import router

# Router principal del módulo SharePoint
router = APIRouter(prefix="/v1/sharepoint")

# Incluir todos los routers SharePoint en el router principal
router.include_router(router)

__all__ = ["router"]