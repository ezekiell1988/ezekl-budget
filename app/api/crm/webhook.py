"""
Webhook para recibir datos JSON y guardarlos en la base de datos.
"""

from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
import logging
from app.database.connection import execute_sp
from app.models.webhook import WebhookPayload, WebhookLogResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook", response_model=WebhookLogResponse)
async def receive_webhook(payload: WebhookPayload):
    """
    Recibe cualquier payload JSON y lo guarda en la base de datos usando spLogAdd.
    
    Args:
        payload: Payload JSON flexible que acepta cualquier estructura
        
    Returns:
        WebhookLogResponse: Confirmación con el ID del log creado
        
    Example:
        ```json
        {
            "evento": "pedido_creado",
            "cliente": "Juan Pérez",
            "monto": 150.50,
            "items": [
                {"producto": "Laptop", "cantidad": 1}
            ]
        }
        ```
    """
    try:
        # Convertir el payload a diccionario
        payload_dict = payload.model_dump()
        
        # Generar timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Preparar datos para el stored procedure
        sp_params = {
            "typeLog": "webhook",
            "log": payload_dict
        }
        
        # Ejecutar stored procedure
        result = await execute_sp("spLogAdd", sp_params)
        
        logger.info(f"✅ Webhook recibido y guardado en BD con ID: {result.get('idLog')}")
        
        return WebhookLogResponse(
            success=True,
            message="Webhook recibido y guardado en base de datos",
            idLog=result.get("idLog"),
            timestamp=timestamp
        )
        
    except Exception as e:
        logger.error(f"❌ Error al procesar webhook: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar webhook: {str(e)}"
        )
