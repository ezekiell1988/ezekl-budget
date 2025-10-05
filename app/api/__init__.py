"""
API routes y WebSockets para la aplicación ezekl-budget.
Routers estándar de FastAPI para HTTP endpoints y WebSockets.
"""

from fastapi import APIRouter
from .routes import router as routes_router
from .websockets import router as websockets_router

# Router principal de la API con prefijo /api para endpoints HTTP
api_router = APIRouter(prefix="/api")

# Incluir router de routes (endpoints /credentials, /health, etc.)
api_router.include_router(routes_router)

# Router para WebSockets con prefijo /ws (consistente con estructura)
websockets_router_with_prefix = APIRouter(prefix="/ws")
websockets_router_with_prefix.include_router(websockets_router)

__all__ = ["api_router", "websockets_router_with_prefix"]