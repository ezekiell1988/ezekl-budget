"""
Webhook para recibir datos JSON y guardarlos en archivos.
"""

from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Ruta relativa donde se guardarán los archivos JSON
# Se resuelve desde la raíz del proyecto (donde está app/)
DATA_PATH = Path(__file__).parent.parent.parent.parent / "data"


@router.post("/webhook")
async def receive_webhook(request: Request):
    """
    Recibe cualquier payload JSON y lo guarda en un archivo con timestamp como nombre.
    
    Args:
        request: Request de FastAPI con el payload JSON
        
    Returns:
        dict: Confirmación con el nombre del archivo guardado
    """
    try:
        # Obtener el JSON del request
        payload = await request.json()
        
        # Generar timestamp para el nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{timestamp}.json"
        
        # Asegurar que el directorio existe
        DATA_PATH.mkdir(parents=True, exist_ok=True)
        
        # Guardar el archivo
        file_path = DATA_PATH / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Webhook recibido y guardado en: {filename}")
        
        return {
            "success": True,
            "message": "Webhook recibido correctamente",
            "filename": filename,
            "timestamp": timestamp
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error al parsear JSON: {str(e)}")
        raise HTTPException(status_code=400, detail="El payload no es un JSON válido")
    
    except Exception as e:
        logger.error(f"❌ Error al procesar webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar webhook: {str(e)}")
