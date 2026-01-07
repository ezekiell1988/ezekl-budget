"""
API routes y WebSockets para la aplicación ezekl-budget.
Routers estándar de FastAPI para HTTP endpoints y WebSockets.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .crm import router as crm_router
from .routes import router as routes_router
from .sharepoint import router as sharepoint_router

# Router principal de la API con prefijo /api para endpoints HTTP
api_router = APIRouter(prefix="/api")

# Incluir router de auth directamente en /api/auth (sin /v1)
# Esto permite que /api/auth/callback funcione para compatibilidad
api_router.include_router(auth_router)

# Incluir router de routes (endpoints /credentials, /health, etc.)
api_router.include_router(routes_router)

# Incluir router de CRM
api_router.include_router(crm_router)

# Incluir router de SharePoint
api_router.include_router(sharepoint_router)

__all__ = ["api_router"]