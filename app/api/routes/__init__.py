"""
Endpoints HTTP de la API ezekl-budget.
Estructura preparada para escalar con múltiples rutas organizadas.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .auth_microsoft import router as auth_microsoft_router
from .email import router as email_router
from .queue import router as queue_router
from .accounting_account import router as accounting_account_router
from .company import router as company_router
from .product import router as product_router
from .whatsapp import router as whatsapp_router
from .ai import router as ai_router
from .copilot import router as copilot_router
from .exam_question import router as exam_question_router
from .credentials import router as credentials_router
from .system import router as system_router

# Router principal para todos los endpoints de la API
router = APIRouter(prefix="/v1")

# Incluir routers de módulos específicos
router.include_router(system_router)
router.include_router(auth_router)
router.include_router(auth_microsoft_router)
router.include_router(product_router)
router.include_router(email_router)
router.include_router(queue_router)
router.include_router(accounting_account_router)
router.include_router(whatsapp_router)
router.include_router(ai_router)
router.include_router(copilot_router)
router.include_router(exam_question_router)
router.include_router(company_router)
router.include_router(credentials_router)

# Exportar routers para uso externo
__all__ = ["router"]

