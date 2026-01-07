"""
Endpoints HTTP de la API ezekl-budget.
Estructura preparada para escalar con múltiples rutas organizadas.
"""

from fastapi import APIRouter
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
router.include_router(product_router, prefix="/products")
router.include_router(email_router, prefix="/email")
router.include_router(queue_router, prefix="/queue")
router.include_router(accounting_account_router, prefix="/accounting-accounts")
router.include_router(whatsapp_router, prefix="/whatsapp")
router.include_router(ai_router, prefix="/ai")
router.include_router(copilot_router, prefix="/copilot")
router.include_router(exam_question_router, prefix="/exam-questions")
router.include_router(company_router, prefix="/companies")
router.include_router(credentials_router, prefix="/credentials")
router.include_router(system_router)

# Exportar routers para uso externo
__all__ = ["router"]

# 🚀 Estructura de routers organizados:
# 
# api/routes/
# ├── __init__.py              # (este archivo - router principal)
# ├── credentials.py           # /v1/credentials/* - credenciales Azure OpenAI
# ├── system.py                # /v1/health - health check del sistema
# ├── product.py               # /v1/products/* - gestión de productos
# ├── email.py                 # /v1/email/* - gestión de emails
# ├── queue.py                 # /v1/queue/* - gestión de colas
# ├── accounting_account.py    # /v1/accounting-accounts/* - cuentas contables
# ├── company.py               # /v1/companies/* - gestión de empresas
# ├── whatsapp.py              # /v1/whatsapp/* - integración WhatsApp
# ├── ai.py                    # /v1/ai/* - funcionalidades AI
# ├── copilot.py               # /v1/copilot/* - integración Copilot
# └── exam_question.py         # /v1/exam-questions/* - preguntas de examen

