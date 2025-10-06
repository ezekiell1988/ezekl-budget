"""
Aplicación FastAPI híbrida para ezekl-budget con frontend Ionic Angular.
Punto de entrada principal que configura la aplicación y monta los módulos API.
"""

from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from app.core.config import settings
from app.api import api_router, websockets_router_with_prefix
from app.services.email_queue import email_queue
import logging

# Configurar logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación usando el nuevo patrón lifespan.
    Reemplaza los deprecated on_event("startup") y on_event("shutdown").
    """
    # Startup
    logger.info("🚀 Iniciando servicios de la aplicación...")
    await email_queue.start()
    logger.info("✅ Servicios iniciados exitosamente")
    
    yield  # Aquí la aplicación está ejecutándose
    
    # Shutdown  
    logger.info("⏹️ Cerrando servicios de la aplicación...")
    await email_queue.stop()
    logger.info("✅ Servicios cerrados exitosamente")


# Configurar rutas para archivos estáticos del frontend Ionic
FRONTEND_BUILD_PATH = Path(__file__).parent.parent / "ezekl-budget-ionic" / "www"

# Inicializar la aplicación FastAPI con lifespan
app = FastAPI(
    title="Ezekl Budget API",
    description="API híbrida para gestión de presupuesto con frontend Ionic Angular y autenticación Microsoft",
    version="1.0.0",
    lifespan=lifespan
)

# 🔧 Configurar módulos de la API (estándar FastAPI)
app.include_router(api_router)                    # ✅ HTTP endpoints con prefix="/api"
app.include_router(websockets_router_with_prefix)  # ✅ WebSockets con prefix="/ws"

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
    import platform
    
    # Configuración específica para WebSockets compatible con Windows
    config_kwargs = {
        "host": "0.0.0.0",
        "port": settings.port,
        "ws_ping_interval": 20,
        "ws_ping_timeout": 20,
        "ws_max_size": 16777216,  # 16MB
        "reload": False  # Evitar problemas en Windows
    }
    
    # En Windows, no usar uvloop (no es compatible)
    if platform.system() != "Windows":
        config_kwargs["loop"] = "uvloop"
    else:
        # Windows usa el event loop por defecto de asyncio
        config_kwargs["loop"] = "asyncio"
    
    uvicorn.run(app, **config_kwargs)
