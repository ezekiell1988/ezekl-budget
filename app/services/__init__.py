"""
Módulo de servicios de la aplicación.

Este módulo contiene la lógica de negocio y servicios reutilizables
que pueden ser utilizados desde diferentes partes de la aplicación.
"""

# Servicios principales
from .email_service import email_service, send_email, send_notification_email
from .email_queue import email_queue

# Servicios CRM
from .crm_auth import crm_auth_service
from .crm_service import crm_service

__all__ = [
    # Servicios de email
    "email_service", "send_email", "send_notification_email", "email_queue",
    
    # Servicios CRM
    "crm_auth_service", "crm_service"
]

# Exportar servicios principales
from .email_service import email_service, send_email, send_notification_email
from .email_queue import email_queue

# Exportar servicios CRM
from .crm_auth import crm_auth_service
from .crm_service import crm_service

__all__ = [
    # Servicios de email
    "email_service", "send_email", "send_notification_email", "email_queue",
    
    # Servicios CRM
    "crm_auth_service", "crm_service"
]