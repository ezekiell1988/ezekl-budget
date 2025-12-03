"""
API routes y WebSockets para la aplicación ezekl-budget.
Routers estándar de FastAPI para HTTP endpoints y WebSockets.
"""

from fastapi import APIRouter
from .routes import router as routes_router
from .routes.auth import router as auth_router
from .websockets import router as websockets_router
from .sharepoint import sharepoint_router

# Router principal de la API con prefijo /api para endpoints HTTP
api_router = APIRouter(prefix="/api")

# Incluir router de auth directamente en /api/auth (sin /v1)
# Esto permite que /api/auth/callback funcione para compatibilidad
api_router.include_router(auth_router, prefix="/auth")

# Incluir router de routes (endpoints /credentials, /health, etc.)
api_router.include_router(routes_router, prefix="/v1")

# Incluir router de SharePoint
api_router.include_router(sharepoint_router, prefix="/v1")

# Router para WebSockets con prefijo /ws (consistente con estructura)
websockets_router_with_prefix = APIRouter(prefix="/ws")
websockets_router_with_prefix.include_router(websockets_router)

__all__ = ["api_router", "websockets_router_with_prefix"]