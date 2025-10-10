"""
Inicialización del módulo CRM.
Exporta los routers principales para las rutas de CRM.
"""

from .cases import router as cases_router
from .accounts import router as accounts_router
from .contacts import router as contacts_router
from .system import router as system_router

__all__ = ["cases_router", "accounts_router", "contacts_router", "system_router"]