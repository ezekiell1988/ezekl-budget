"""
Aplicación FastAPI híbrida para ezekl-budget con frontend Ionic Angular.
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from app.settings import settings
from app.database import test_db_connection


# Configurar rutas para archivos estáticos del frontend Ionic
FRONTEND_BUILD_PATH = Path(__file__).parent.parent / "ezekl-budget-ionic" / "www"

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="Ezekl Budget API",
    description="API híbrida para gestión de presupuesto con frontend Ionic Angular y autenticación Microsoft",
    version="1.0.0",
)

# Crear router para todas las rutas de la API
api_router = APIRouter(prefix="/api")


class CredentialsResponse(BaseModel):
    """Modelo de respuesta para las credenciales."""
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    message: str


@api_router.get("/credentials", response_model=CredentialsResponse)
async def get_credentials():
    """
    Obtiene las credenciales de Azure OpenAI desde las variables de entorno.
    
    Returns:
        CredentialsResponse: Las credenciales configuradas (sin incluir la API key por seguridad)
    """
    return CredentialsResponse(
        azure_openai_endpoint=settings.azure_openai_endpoint,
        azure_openai_deployment_name=settings.azure_openai_deployment_name,
        message="Credenciales cargadas exitosamente desde .env"
    )


@api_router.get("/health")
async def health_check():
    """
    Endpoint de salud para verificar que la API y la base de datos están funcionando.
    
    Returns:
        dict: Estado de la aplicación incluyendo conexión a base de datos
    """
    # Verificar conexión a base de datos de forma asíncrona
    db_status = "healthy" if await test_db_connection() else "unhealthy"
    
    # Si la BD no está disponible, devolver error 503
    if db_status == "unhealthy":
        raise HTTPException(
            status_code=503, 
            detail="Servicio no disponible: Error de conexión a base de datos"
        )
    
    return {
        "status": "healthy",
        "message": "Ezekl Budget API está funcionando correctamente",
        "version": "1.0.0",
        "environment": {
            "is_production": settings.is_production,
            "configured_host": settings.db_host,
            "effective_host": settings.effective_db_host
        },
        "database": {
            "status": db_status,
            "host": settings.effective_db_host,
            "database": settings.db_name
        },
        "components": {
            "api": "healthy",
            "database": db_status
        }
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint para conexión en tiempo real con ping-pong.
    Mantiene la conexión activa y responde a pings del cliente.
    """
    await websocket.accept()
    print(f"🔌 WebSocket conectado: {websocket.client}")
    
    try:
        # Enviar mensaje de bienvenida
        welcome_message = {
            "type": "welcome",
            "message": "Conectado al servidor WebSocket de Ezekl Budget",
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "version": "1.0.0",
                "environment": "development" if not settings.is_production else "production"
            }
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
                        "message": "pong from server"
                    }
                    await websocket.send_text(json.dumps(pong_response))
                    
                elif message.get("type") == "echo":
                    # Echo del mensaje recibido
                    echo_response = {
                        "type": "echo",
                        "original_message": message.get("message", ""),
                        "timestamp": datetime.now().isoformat(),
                        "echo": f"Servidor recibió: {message.get('message', '')}"
                    }
                    await websocket.send_text(json.dumps(echo_response))
                    
                else:
                    # Mensaje genérico
                    response = {
                        "type": "response",
                        "message": f"Servidor recibió mensaje de tipo: {message.get('type', 'unknown')}",
                        "timestamp": datetime.now().isoformat(),
                        "original": message
                    }
                    await websocket.send_text(json.dumps(response))
                    
            except json.JSONDecodeError:
                # Si no es JSON válido, tratar como texto plano
                response = {
                    "type": "text_response",
                    "message": f"Servidor recibió texto: {data}",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(response))
                
    except WebSocketDisconnect:
        print(f"🔌 WebSocket desconectado: {websocket.client}")
    except Exception as e:
        print(f"❌ Error en WebSocket: {str(e)}")
        try:
            error_message = {
                "type": "error",
                "message": f"Error del servidor: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(error_message))
        except:
            pass  # Conexión ya cerrada


# Incluir el router de la API
app.include_router(api_router)

# Servir archivos estáticos del frontend (CSS, JS, assets, etc.)
if FRONTEND_BUILD_PATH.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_BUILD_PATH), name="static")

# Endpoint para servir el index.html del frontend en la raíz
@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Sirve el frontend de Ionic Angular."""
    index_file = FRONTEND_BUILD_PATH / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    else:
        # Si no existe el build del frontend, redirigir a la documentación de la API
        return RedirectResponse(url="/docs")


# Catch-all para rutas del frontend (SPA routing)
@app.get("/{path:path}", include_in_schema=False)
async def serve_frontend_routes(path: str):
    """
    Maneja todas las rutas del frontend para el SPA routing.
    Si el archivo existe, lo sirve; si no, sirve index.html para el routing de Angular.
    """
    if not FRONTEND_BUILD_PATH.exists():
        return RedirectResponse(url="/docs")
    
    # Verificar si es una ruta de API
    if path.startswith("api/"):
        return RedirectResponse(url="/docs")
    
    # Verificar si el archivo solicitado existe
    file_path = FRONTEND_BUILD_PATH / path
    if file_path.is_file():
        return FileResponse(file_path)
    
    # Para todas las demás rutas, servir index.html (SPA routing)
    index_file = FRONTEND_BUILD_PATH / "index.html"
    return FileResponse(index_file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
