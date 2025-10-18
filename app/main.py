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
import sys

# Configurar logging con nivel DEBUG para ver todos los logs
logging.basicConfig(
    level=logging.INFO,  # Cambiar a DEBUG para ver todos los logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Enviar logs a stdout para Docker
    ]
)

# Configurar nivel de logs para bibliotecas externas (reducir ruido)
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación usando el nuevo patrón lifespan.
    Reemplaza los deprecated on_event("startup") y on_event("shutdown").
    """
    # Startup
    await email_queue.start()
    
    yield  # Aquí la aplicación está ejecutándose
    
    # Shutdown  
    await email_queue.stop()


# Configurar rutas para archivos estáticos del frontend Ionic
FRONTEND_BUILD_PATH = Path(__file__).parent.parent / "ezekl-budget-ionic" / "www"

# Inicializar la aplicación FastAPI con lifespan
app = FastAPI(
    title="Ezekl Budget API",
    description="API híbrida para gestión de presupuesto con frontend Ionic Angular y autenticación Microsoft",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS para permitir WebSockets desde localhost
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "ws://localhost:8001",
        "ws://127.0.0.1:8001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    is_windows = platform.system() == "Windows"
    
    config_kwargs = {
        # En Windows, usar 127.0.0.1 en lugar de 0.0.0.0 para WebSockets
        "host": "127.0.0.1" if is_windows else "0.0.0.0",
        "port": settings.port,
        "ws_ping_interval": 20,
        "ws_ping_timeout": 20,
        "ws_max_size": 16777216,  # 16MB
        "reload": False,  # Evitar problemas en Windows con reload
        "log_level": "info",
    }
    
    # En Windows, no usar uvloop (no es compatible)
    if not is_windows:
        config_kwargs["loop"] = "uvloop"
    else:
        # Windows usa el event loop por defecto de asyncio
        config_kwargs["loop"] = "asyncio"
        # En Windows, asegurar que se use el selector de eventos correcto
        import asyncio
        if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    
    uvicorn.run(app, **config_kwargs)
