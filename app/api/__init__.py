"""
API routes y WebSockets para la aplicación ezekl-budget.
Routers estándar de FastAPI para HTTP endpoints y WebSockets.
"""

from fastapi import APIRouter
from .crm import router as crm_router
from .routes import router as routes_router
from .sharepoint import router as sharepoint_router

# Router principal de la API con prefijo /api para endpoints HTTP
router = APIRouter(prefix="/api")

# Incluir router de routes (endpoints /credentials, /health, etc.)
router.include_router(routes_router)

# Incluir router de CRM
router.include_router(crm_router)

# Incluir router de SharePoint
router.include_router(sharepoint_router)

__all__ = ["router"]