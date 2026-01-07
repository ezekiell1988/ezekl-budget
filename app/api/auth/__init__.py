"""
Router principal de autenticación para el sistema Ezekl Budget.
Agrupa todos los routers de autenticación: auth básico y Microsoft OAuth.
"""

from fastapi import APIRouter

# Router principal de autenticación
router = APIRouter(prefix="/auth")

# Incluir sub-routers (importar aquí para evitar circular imports)
from app.api.auth.auth import router as auth_router
from app.api.auth.auth_microsoft import router as microsoft_router

router.include_router(auth_router)
router.include_router(microsoft_router)