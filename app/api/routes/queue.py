"""
Endpoints para monitorear y gestionar la cola de emails.
Permite ver estadísticas, tamaño de la cola y estado del worker.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import logging

from app.services.email_queue import email_queue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/queue", tags=["Cola de Emails"])


@router.get(
    "/stats",
    summary="Estadísticas de la cola de emails",
    description="""Obtiene estadísticas detalladas de la cola de emails.
    
    Retorna información sobre:
    - Estado del worker (running/stopped)
    - Tamaño actual de la cola
    - Emails procesados exitosamente
    - Emails fallidos
    - Tasa de éxito en porcentaje
    
    Útil para monitorear el estado del sistema de emails en tiempo real.
    """
)
async def get_queue_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas de la cola de emails.
    
    Returns:
        Dict con estadísticas: is_running, queue_size, processed_count, 
        failed_count, success_rate, timestamp
    """
    try:
        stats = await email_queue.get_stats()
        stats["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"📊 Estadísticas consultadas: {stats['processed_count']} procesados, "
                   f"{stats['failed_count']} fallidos, cola: {stats['queue_size']}")
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        error_msg = f"Error al obtener estadísticas: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get(
    "/status",
    summary="Estado del worker de la cola",
    description="""Verifica el estado del worker de la cola de emails.
    
    Retorna:
    - is_running: Si el worker está ejecutándose
    - queue_size: Cantidad de emails pendientes en cola
    - status_message: Descripción del estado actual
    
    Útil para verificar que el servicio de emails está operativo.
    """
)
async def get_queue_status() -> Dict[str, Any]:
    """
    Verifica el estado del worker de emails.
    
    Returns:
        Dict con estado del worker y tamaño de la cola
    """
    try:
        stats = await email_queue.get_stats()
        is_running = stats["is_running"]
        queue_size = stats["queue_size"]
        
        status_message = (
            f"Worker {'activo' if is_running else 'detenido'} | "
            f"Cola: {queue_size} email(s) pendiente(s)"
        )
        
        logger.info(f"🔍 Estado consultado: {status_message}")
        
        return {
            "success": True,
            "is_running": is_running,
            "queue_size": queue_size,
            "status": "healthy" if is_running else "stopped",
            "message": status_message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        error_msg = f"Error al verificar estado: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post(
    "/start",
    summary="Iniciar worker de la cola",
    description="""Inicia el worker de procesamiento de emails si está detenido.
    
    Normalmente el worker se inicia automáticamente al arrancar la aplicación,
    pero este endpoint permite reiniciarlo manualmente si fue detenido.
    
    Retorna el nuevo estado del worker después de iniciarlo.
    """
)
async def start_queue() -> Dict[str, Any]:
    """
    Inicia el worker de la cola de emails.
    
    Returns:
        Dict con confirmación de inicio exitoso
    """
    try:
        await email_queue.start()
        
        logger.info("🚀 Worker de emails iniciado manualmente")
        
        return {
            "success": True,
            "message": "Worker de emails iniciado exitosamente",
            "is_running": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        error_msg = f"Error al iniciar worker: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post(
    "/stop",
    summary="Detener worker de la cola",
    description="""Detiene el worker de procesamiento de emails.
    
    ⚠️ ADVERTENCIA: Detener el worker pausará el envío de emails.
    Los emails en cola no se enviarán hasta que se reinicie el worker.
    
    Usar solo para mantenimiento o debugging.
    """
)
async def stop_queue() -> Dict[str, Any]:
    """
    Detiene el worker de la cola de emails.
    
    Returns:
        Dict con confirmación de detención exitosa
    """
    try:
        await email_queue.stop()
        
        logger.warning("⏸️ Worker de emails detenido manualmente")
        
        return {
            "success": True,
            "message": "Worker de emails detenido. Los emails no se enviarán hasta reiniciar.",
            "is_running": False,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        error_msg = f"Error al detener worker: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get(
    "/health",
    summary="Health check de la cola",
    description="""Endpoint de health check para monitoreo externo.
    
    Retorna HTTP 200 si todo está OK, HTTP 503 si hay problemas.
    
    Criterios de salud:
    - Worker debe estar ejecutándose
    - Cola no debe estar llena
    
    Útil para sistemas de monitoreo como Kubernetes, Docker health checks, etc.
    """
)
async def health_check() -> Dict[str, Any]:
    """
    Health check para la cola de emails.
    
    Returns:
        Dict con estado de salud del sistema
        
    Raises:
        HTTPException 503 si el sistema no está saludable
    """
    try:
        stats = await email_queue.get_stats()
        is_running = stats["is_running"]
        queue_size = stats["queue_size"]
        
        # Verificar que el worker esté corriendo
        if not is_running:
            logger.error("❌ Health check FAIL: Worker no está ejecutándose")
            raise HTTPException(
                status_code=503,
                detail="Worker de emails no está ejecutándose"
            )
        
        # Verificar que la cola no esté llena (capacidad máxima 1000)
        if queue_size >= 1000:
            logger.warning("⚠️ Health check WARNING: Cola llena")
            raise HTTPException(
                status_code=503,
                detail="Cola de emails está llena"
            )
        
        logger.debug(f"✅ Health check OK: Worker activo, cola: {queue_size}")
        
        return {
            "status": "healthy",
            "worker_running": is_running,
            "queue_size": queue_size,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error en health check: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=503, detail=error_msg)
