"""
Endpoints para integración con WhatsApp Business API.
Proporciona webhook para recibir mensajes y notificaciones de WhatsApp.
"""

from fastapi import APIRouter, HTTPException, Request, Query, Header
from fastapi.responses import PlainTextResponse
from typing import Optional
import logging
import json
from app.models.whatsapp import WhatsAppWebhookPayload

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de WhatsApp
router = APIRouter()

# Token de verificación del webhook (debe coincidir con el configurado en Meta)
# En producción, esto debe estar en variables de entorno
WEBHOOK_VERIFY_TOKEN = "mi_token_secreto_whatsapp_2025"


@router.get(
    "/webhook",
    response_class=PlainTextResponse,
    summary="Verificación del webhook de WhatsApp",
    description="""Endpoint para verificación del webhook de WhatsApp Business API.
    
    Meta/Facebook envía una petición GET a este endpoint para verificar que el webhook
    está configurado correctamente. Debes configurar el mismo verify_token en la 
    consola de desarrolladores de Meta.
    
    **Parámetros de verificación:**
    - `hub.mode`: Debe ser "subscribe"
    - `hub.verify_token`: Debe coincidir con el token configurado
    - `hub.challenge`: Valor que debe retornarse para completar la verificación
    
    **Respuesta exitosa:**
    - Retorna el valor de hub.challenge como texto plano
    
    **Configuración en Meta:**
    1. Ve a la consola de desarrolladores de Meta
    2. Configura el webhook URL: https://tu-dominio.com/api/whatsapp/webhook
    3. Configura el verify token: mi_token_secreto_whatsapp_2024
    4. Suscríbete a los eventos: messages
    """
)
async def verify_webhook(
    request: Request,
    mode: str = Query(alias="hub.mode", description="Modo del hub"),
    token: str = Query(alias="hub.verify_token", description="Token de verificación"),
    challenge: str = Query(alias="hub.challenge", description="Challenge a retornar")
):
    """
    Verifica el webhook de WhatsApp.
    
    Args:
        mode: Modo del hub (debe ser "subscribe")
        token: Token de verificación (debe coincidir con WEBHOOK_VERIFY_TOKEN)
        challenge: Challenge enviado por Meta
        
    Returns:
        PlainTextResponse: El challenge si la verificación es exitosa
        
    Raises:
        HTTPException: Error 403 si la verificación falla
    """
    logger.info(f"📞 Verificación de webhook recibida")
    logger.debug(f"Mode: {mode}, Token recibido: {token[:10]}..., Challenge: {challenge[:20]}...")
    
    # Verificar que el modo sea "subscribe"
    if mode != "subscribe":
        logger.warning(f"❌ Modo inválido: {mode}")
        raise HTTPException(
            status_code=403,
            detail="Modo de verificación inválido"
        )
    
    # Verificar que el token coincida
    if token != WEBHOOK_VERIFY_TOKEN:
        logger.warning(f"❌ Token de verificación incorrecto")
        raise HTTPException(
            status_code=403,
            detail="Token de verificación inválido"
        )
    
    logger.info(f"✅ Webhook verificado exitosamente")
    
    # Retornar el challenge para completar la verificación
    return PlainTextResponse(content=challenge)


@router.post(
    "/webhook",
    summary="Recibir webhooks de WhatsApp",
    description="""Endpoint para recibir notificaciones de WhatsApp Business API.
    
    Este endpoint recibe notificaciones de Meta cuando:
    - Se recibe un nuevo mensaje
    - Cambia el estado de un mensaje enviado
    - Ocurren otros eventos configurados
    
    **Eventos soportados:**
    - `messages`: Mensajes entrantes de usuarios
    - `message_status`: Cambios de estado de mensajes enviados (enviado, entregado, leído)
    
    **Tipos de mensajes soportados:**
    - text: Mensajes de texto
    - image: Imágenes
    - video: Videos
    - document: Documentos
    - audio: Audios
    - location: Ubicaciones
    - contacts: Contactos
    
    **Seguridad:**
    - Meta firma las peticiones con x-hub-signature-256
    - Se debe validar la firma para producción (pendiente implementar)
    
    **Respuesta:**
    - Siempre retorna 200 OK para confirmar recepción
    - El procesamiento es asíncrono (actualmente solo logging)
    """,
    responses={
        200: {
            "description": "Webhook procesado exitosamente"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
async def receive_webhook(
    request: Request,
    payload: WhatsAppWebhookPayload,
    x_hub_signature_256: Optional[str] = Header(None, description="Firma de Meta para validación")
):
    """
    Recibe y procesa webhooks de WhatsApp.
    
    Args:
        request: Request de FastAPI
        payload: Payload del webhook validado con Pydantic
        x_hub_signature_256: Firma de seguridad de Meta
        
    Returns:
        dict: Confirmación de recepción
        
    Note:
        Por ahora solo imprime los datos recibidos.
        TODO: Implementar validación de firma x-hub-signature-256
        TODO: Implementar procesamiento de mensajes
        TODO: Implementar respuestas automáticas
    """
    try:
        logger.info("=" * 80)
        logger.info(f"📱 WEBHOOK DE WHATSAPP RECIBIDO")
        logger.info("=" * 80)
        
        # Log de la firma de seguridad
        if x_hub_signature_256:
            logger.info(f"🔐 Firma de seguridad: {x_hub_signature_256[:30]}...")
        else:
            logger.warning("⚠️ Sin firma de seguridad (x-hub-signature-256)")
        
        # Log del objeto principal
        logger.info(f"📦 Tipo de objeto: {payload.object}")
        
        # Procesar cada entrada
        for entry_idx, entry in enumerate(payload.entry, 1):
            logger.info(f"\n📋 ENTRADA #{entry_idx}")
            logger.info(f"  - WhatsApp Business Account ID: {entry.id}")
            
            # Procesar cada cambio
            for change_idx, change in enumerate(entry.changes, 1):
                logger.info(f"\n  🔄 CAMBIO #{change_idx}")
                logger.info(f"    - Campo: {change.field}")
                logger.info(f"    - Producto: {change.value.messaging_product}")
                
                # Metadata del número de teléfono
                metadata = change.value.metadata
                logger.info(f"    - Número de teléfono: {metadata.display_phone_number}")
                logger.info(f"    - Phone Number ID: {metadata.phone_number_id}")
                
                # Procesar mensajes entrantes
                if change.value.messages:
                    logger.info(f"\n    📨 MENSAJES ENTRANTES: {len(change.value.messages)}")
                    
                    for msg_idx, message in enumerate(change.value.messages, 1):
                        logger.info(f"\n      💬 MENSAJE #{msg_idx}")
                        logger.info(f"        - ID: {message.id}")
                        logger.info(f"        - De: {message.from_}")
                        logger.info(f"        - Timestamp: {message.timestamp}")
                        logger.info(f"        - Tipo: {message.type}")
                        
                        # Si es mensaje de texto, mostrar el contenido
                        if message.type == "text" and message.text:
                            logger.info(f"        - Contenido: '{message.text.body}'")
                        
                        # Log del contacto
                        if change.value.contacts:
                            for contact in change.value.contacts:
                                if contact.wa_id == message.from_:
                                    logger.info(f"        - Nombre del contacto: {contact.profile.name}")
                                    logger.info(f"        - WhatsApp ID: {contact.wa_id}")
                
                # Procesar cambios de estado
                if change.value.statuses:
                    logger.info(f"\n    📊 ESTADOS DE MENSAJES: {len(change.value.statuses)}")
                    
                    for status_idx, status in enumerate(change.value.statuses, 1):
                        logger.info(f"\n      📍 ESTADO #{status_idx}")
                        logger.info(f"        - Estado: {json.dumps(status, indent=10)}")
        
        # Log del payload completo en formato JSON
        logger.info("\n" + "=" * 80)
        logger.info("📄 PAYLOAD COMPLETO (JSON):")
        logger.info("=" * 80)
        logger.info(json.dumps(payload.model_dump(by_alias=True), indent=2, ensure_ascii=False))
        logger.info("=" * 80)
        
        # Retornar confirmación de recepción
        return {
            "status": "received",
            "message": "Webhook procesado exitosamente"
        }
        
    except Exception as e:
        logger.error(f"❌ Error procesando webhook de WhatsApp: {str(e)}", exc_info=True)
        
        # Meta requiere que siempre retornemos 200 para evitar reintentos
        # Por eso capturamos el error pero retornamos éxito
        return {
            "status": "error",
            "message": f"Error procesando webhook: {str(e)}"
        }


@router.get(
    "/status",
    summary="Estado del servicio de WhatsApp",
    description="Verifica que el servicio de WhatsApp está activo y configurado correctamente"
)
async def whatsapp_status():
    """
    Verifica el estado del servicio de WhatsApp.
    
    Returns:
        dict: Estado del servicio
    """
    return {
        "status": "active",
        "service": "WhatsApp Business API",
        "webhook_configured": True,
        "verify_token_set": bool(WEBHOOK_VERIFY_TOKEN),
        "features": {
            "receive_messages": True,
            "send_messages": False,  # Pendiente implementar
            "validate_signature": False  # Pendiente implementar
        }
    }
