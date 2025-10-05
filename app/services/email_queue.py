"""
Servicio de cola de emails en background para Ezekl Budget.
Maneja el envío asíncrono de emails sin bloquear las respuestas de la API.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from app.services.email_service import send_notification_email

logger = logging.getLogger(__name__)

@dataclass
class EmailTask:
    """Tarea de email para la cola"""
    id: str
    to: List[str]
    subject: str
    message: str
    is_html: bool = False
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class EmailQueue:
    """
    Cola de emails asíncrona para envío en background.
    
    Características:
    - Cola FIFO usando asyncio.Queue
    - Worker en background que procesa emails
    - Logging detallado para monitoreo
    - Manejo robusto de errores sin fallar el worker
    """
    
    def __init__(self, max_size: int = 1000):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.worker_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.processed_count = 0
        self.failed_count = 0
        
    async def start(self):
        """Inicia el worker de la cola"""
        if self.is_running:
            logger.warning("Email queue worker ya está ejecutándose")
            return
            
        self.is_running = True
        self.worker_task = asyncio.create_task(self._worker())
        logger.info("🚀 Email queue worker iniciado exitosamente")
        
    async def stop(self):
        """Detiene el worker de la cola"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
                
        logger.info(f"⏹️ Email queue worker detenido. Procesados: {self.processed_count}, Fallos: {self.failed_count}")
        
    async def add_email(self, email_task: EmailTask) -> bool:
        """
        Agrega un email a la cola para envío en background.
        
        Args:
            email_task: Tarea de email a procesar
            
        Returns:
            True si se agregó exitosamente, False si la cola está llena
        """
        try:
            # Usar put_nowait para no bloquear si la cola está llena
            self.queue.put_nowait(email_task)
            logger.info(f"📧 Email agregado a la cola: {email_task.id} -> {email_task.to[0]} - {email_task.subject}")
            return True
        except asyncio.QueueFull:
            logger.error(f"❌ Cola de emails llena, no se puede agregar: {email_task.id}")
            return False
            
    async def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cola"""
        return {
            "is_running": self.is_running,
            "queue_size": self.queue.qsize(),
            "processed_count": self.processed_count,
            "failed_count": self.failed_count,
            "success_rate": round(self.processed_count / max(self.processed_count + self.failed_count, 1) * 100, 2)
        }
        
    async def _worker(self):
        """Worker que procesa emails en background"""
        logger.info("📨 Email queue worker iniciando procesamiento...")
        
        while self.is_running:
            try:
                # Esperar por un email en la cola (timeout para permitir verificación de is_running)
                email_task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                await self._process_email(email_task)
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                # Timeout normal, continuar el loop
                continue
            except asyncio.CancelledError:
                # Worker cancelado, salir
                break
            except Exception as e:
                logger.error(f"❌ Error inesperado en email worker: {str(e)}")
                # Continuar procesando otros emails aunque uno falle
                
    async def _process_email(self, email_task: EmailTask):
        """
        Procesa un email individual.
        
        Args:
            email_task: Tarea de email a procesar
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"📧 Procesando email {email_task.id}: {email_task.subject}")
            
            # Enviar email usando el servicio existente
            result = await send_notification_email(
                to=email_task.to,
                subject=email_task.subject,
                message=email_task.message,
                is_html=email_task.is_html,
                cc=email_task.cc,
                bcc=email_task.bcc
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result.success:
                self.processed_count += 1
                logger.info(f"✅ Email {email_task.id} enviado exitosamente en {duration:.2f}s")
            else:
                self.failed_count += 1
                logger.error(f"❌ Error enviando email {email_task.id}: {result.message} ({duration:.2f}s)")
                
        except Exception as e:
            self.failed_count += 1
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Excepción procesando email {email_task.id}: {str(e)} ({duration:.2f}s)")

# Instancia global de la cola de emails
email_queue = EmailQueue()

async def queue_email(to: List[str], subject: str, message: str, 
                     is_html: bool = False, cc: Optional[List[str]] = None, 
                     bcc: Optional[List[str]] = None) -> str:
    """
    Función de conveniencia para agregar emails a la cola.
    
    Args:
        to: Lista de destinatarios
        subject: Asunto del email
        message: Contenido del email
        is_html: Si el contenido es HTML
        cc: Lista de destinatarios en copia (opcional)
        bcc: Lista de destinatarios en copia oculta (opcional)
        
    Returns:
        ID de la tarea de email
    """
    import uuid
    
    task_id = str(uuid.uuid4())[:8]  # ID corto para logging
    
    email_task = EmailTask(
        id=task_id,
        to=to,
        subject=subject,
        message=message,
        is_html=is_html,
        cc=cc,
        bcc=bcc
    )
    
    success = await email_queue.add_email(email_task)
    
    if not success:
        logger.error(f"No se pudo agregar email a la cola: {task_id}")
        
    return task_id