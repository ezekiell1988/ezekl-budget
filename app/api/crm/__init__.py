"""
Inicialización del módulo CRM.
Exporta los routers principales para las rutas de CRM.
"""

from fastapi import APIRouter
from .cases import router as cases_router
from .accounts import router as accounts_router
from .contacts import router as contacts_router
from .system import router as system_router
from .webhook import router as webhook_router

# Router principal del módulo CRM
router = APIRouter(prefix="/v1/crm")

# Incluir todos los routers CRM en el router principal
router.include_router(cases_router)
router.include_router(accounts_router)
router.include_router(contacts_router)
router.include_router(system_router)
router.include_router(webhook_router)

__all__ = ["router"]