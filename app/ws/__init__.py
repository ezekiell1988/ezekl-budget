"""
WebSockets para la aplicación ezekl-budget.
Router estándar de FastAPI para WebSockets con ping-pong y diferentes tipos de mensajes.
"""

import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.config import settings

# Router para WebSockets (estándar FastAPI)
router = APIRouter(prefix="/ws")


@router.websocket("/")
async def websocket_realtime_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint para conexión en tiempo real con ping-pong.
    Mantiene la conexión activa y responde a pings del cliente.
    """
    await websocket.accept()

    try:
        # Enviar mensaje de bienvenida
        welcome_message = {
            "type": "welcome",
            "message": "Conectado al servidor WebSocket de Ezekl Budget",
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "version": "1.0.0",
                "environment": (
                    "development" if not settings.is_production else "production"
                ),
            },
        }
        await websocket.send_text(json.dumps(welcome_message))

        while True:
            try:
                # Recibir mensaje del cliente
                data = await websocket.receive_text()
                message = json.loads(data)

                # Manejar diferentes tipos de mensajes
                if message.get("type") == "ping":
                    # Responder con pong
                    pong_response = {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat(),
                        "client_timestamp": message.get("timestamp"),
                        "message": "pong from server",
                    }
                    await websocket.send_text(json.dumps(pong_response))

                elif message.get("type") == "echo":
                    # Echo del mensaje recibido
                    echo_response = {
                        "type": "echo",
                        "original_message": message.get("message", ""),
                        "timestamp": datetime.now().isoformat(),
                        "echo": f"Servidor recibió: {message.get('message', '')}",
                    }
                    await websocket.send_text(json.dumps(echo_response))

                else:
                    # Mensaje genérico
                    response = {
                        "type": "response",
                        "message": f"Servidor recibió mensaje de tipo: {message.get('type', 'unknown')}",
                        "timestamp": datetime.now().isoformat(),
                        "original": message,
                    }
                    await websocket.send_text(json.dumps(response))

            except json.JSONDecodeError:
                # Si no es JSON válido, tratar como texto plano
                response = {
                    "type": "text_response",
                    "message": f"Servidor recibió texto: {data}",
                    "timestamp": datetime.now().isoformat(),
                }
                await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        pass  # Logger eliminado
    except Exception as e:
        pass  # Logger eliminado
        try:
            error_message = {
                "type": "error",
                "message": f"Error del servidor: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }
            await websocket.send_text(json.dumps(error_message))
        except:
            pass  # Conexión ya cerrada


# 🚀 Estructura futura para múltiples WebSockets:
#
# Cuando necesites más WebSockets, puedes crear archivos específicos:
# 
# api/websockets/
# ├── __init__.py          # (este archivo - router base sin prefijos)  
# ├── realtime.py          # router con WebSocket "/" - tiempo real actual
# ├── chat.py              # router con WebSocket "/chat" - chat en tiempo real
# └── notifications.py     # router con WebSocket "/notifications" - notificaciones push
#
# Y luego incluir todos en este __init__.py:
# from .realtime import router as realtime_router
# from .chat import router as chat_router  
# from .notifications import router as notifications_router
# 
# router.include_router(realtime_router)
# router.include_router(chat_router, prefix="/chat")
# router.include_router(notifications_router, prefix="/notifications")
#
# En api/__init__.py el prefijo "/ws" se aplica a todo el conjunto:
# websockets_router_with_prefix.include_router(websockets_router)
# Resultado: /ws/, /ws/chat, /ws/notifications
