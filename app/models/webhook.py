"""
Modelos Pydantic para webhook logs.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class WebhookPayload(BaseModel):
    """Modelo flexible para recibir cualquier payload JSON en el webhook."""
    
    class Config:
        extra = "allow"  # Permite cualquier campo adicional
        json_schema_extra = {
            "example": {
                "evento": "pedido_creado",
                "cliente": "Juan Pérez",
                "monto": 150.50,
                "items": [
                    {"producto": "Laptop", "cantidad": 1},
                    {"producto": "Mouse", "cantidad": 2}
                ]
            }
        }


class WebhookLogRequest(BaseModel):
    """Modelo para el payload del webhook que se guardará como log."""
    typeLog: str = "webhook"
    log: Dict[str, Any]


class WebhookLogResponse(BaseModel):
    """Respuesta del webhook después de guardar en la base de datos."""
    success: bool
    message: str
    idLog: Optional[int] = None
    timestamp: str
