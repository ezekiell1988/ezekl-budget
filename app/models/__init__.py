"""
Modelos Pydantic para requests y responses de la API.
"""

# Exportar modelos principales de la aplicación
from .auth import *
from .requests import *
from .responses import *
from .accounting_account import *
from .product import *

# Exportar modelos CRM
from .crm import *

__all__ = [
    # Modelos de autenticación
    "LoginRequest", "AuthResponse",
    
    # Modelos de requests y responses generales
    "EmailSendRequest", "EmailSendResponse",
    "CredentialsResponse", "RealtimeCredentialsResponse", "HealthCheckResponse",
    
    # Modelos de cuentas contables
    "AccountingAccount", "AccountingAccountRequest", "AccountingAccountResponse", "AccountingAccountErrorResponse",
    
    # Modelos CRM - Respuestas
    "CaseResponse", "CasesListResponse",
    "AccountResponse", "AccountsListResponse", 
    "ContactResponse", "ContactsListResponse",
    "CaseTypeCodeResponse", "CaseTypeCodesResponse",
    "CRMOperationResponse", "CRMHealthResponse", "CRMTokenResponse", "CRMDiagnoseResponse",
    
    # Modelos CRM - Requests
    "CaseCreateRequest", "CaseUpdateRequest",
    "AccountCreateRequest", "AccountUpdateRequest", 
    "ContactCreateRequest", "ContactUpdateRequest"
]