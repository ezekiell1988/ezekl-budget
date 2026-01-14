"""
Aplicación FastAPI híbrida para ezekl-budget con frontend Ionic Angular.
Punto de entrada principal que configura la aplicación y monta los módulos API.
"""

from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.api import router as api_router
from app.ws import router as ws_router
from app.services.email_queue import email_queue
import logging
import sys

# Configurar logging con nivel DEBUG para ver todos los logs
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar a DEBUG para ver todos los logs
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


class CSPMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar Content Security Policy headers."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Solo agregar CSP en respuestas HTML
        if isinstance(response, FileResponse) or (
            hasattr(response, 'media_type') and 
            response.media_type and 
            'html' in response.media_type
        ):
            # CSP para desarrollo - permite más fuentes para facilitar debugging
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "https://cdnjs.cloudflare.com "
                "https://*.msauth.net https://*.msftauth.net https://*.msftauthimages.net "
                "https://*.msauthimages.net https://*.msidentity.com "
                "https://*.microsoftonline-p.com https://*.microsoftazuread-sso.com "
                "https://*.azureedge.net https://*.outlook.com https://*.office.com "
                "https://*.office365.com https://*.microsoft.com https://*.bing.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' ws: wss: "
                f"http://localhost:{settings.port} http://127.0.0.1:{settings.port} "
                f"ws://localhost:{settings.port} ws://127.0.0.1:{settings.port} "
                "https://*.cognitiveservices.azure.com "
                "https://*.openai.azure.com "
                "https://*.dynamics.com "
                "https://*.microsoftonline.com "
                "https://login.microsoftonline.com; "
                "frame-ancestors 'self'; "
                "base-uri 'self'; "
                "form-action 'self' https://login.microsoftonline.com;"
            )
            
            response.headers['Content-Security-Policy'] = csp_policy
            
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación usando el nuevo patrón lifespan.
    Reemplaza los deprecated on_event("startup") y on_event("shutdown").
    """
    # Startup
    from app.core.redis import redis_client
    
    # Inicializar email queue
    await email_queue.start()
    
    # Inicializar Redis (REQUERIDO)
    try:
        await redis_client.initialize()
        logger.info("✅ Redis inicializado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error crítico: No se pudo conectar a Redis: {str(e)}")
        logger.error("❌ Redis es requerido para el funcionamiento de la aplicación")
        raise RuntimeError(f"Redis connection failed: {str(e)}") from e
    
    yield  # Aquí la aplicación está ejecutándose
    
    # Shutdown
    await email_queue.stop()
    
    # Cerrar Redis
    try:
        await redis_client.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.warning(f"Error closing Redis: {str(e)}")


# Configurar rutas para archivos estáticos del frontend Ionic
# Intentar usar la ruta configurada o detectar automáticamente
if settings.frontend_build_path:
    FRONTEND_BUILD_PATH = Path(settings.frontend_build_path)
else:
    # Detectar automáticamente basado en la ubicación del archivo
    FRONTEND_BUILD_PATH = Path(__file__).parent.parent / settings.frontend_dir / "www"

# Inicializar la aplicación FastAPI con lifespan y configuración de seguridad
app = FastAPI(
    title="Ezekl Budget API",
    description="API híbrida para gestión de presupuesto con frontend Ionic Angular y autenticación Microsoft",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True  # Mantener el token entre recargas
    }
)

# Configurar CORS para permitir WebSockets desde localhost
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://localhost:4200",
        f"http://localhost:4200",
        f"https://localhost:{settings.port}",
        f"http://localhost:{settings.port}",
        f"http://127.0.0.1:{settings.port}",
        f"wss://localhost:{settings.port}",
        f"ws://localhost:{settings.port}",
        f"ws://127.0.0.1:{settings.port}",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar middleware de CSP
app.add_middleware(CSPMiddleware)

# 🔧 Configurar módulos de la API (estándar FastAPI)
app.include_router(api_router)           # ✅ HTTP endpoints con prefix="/api"
app.include_router(ws_router)    # ✅ WebSockets con prefix="/ws"

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

    # NO manejar rutas de API aquí - dejar que FastAPI las procese
    # Las rutas de API ya están registradas con include_router() antes de este catch-all
    
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
        "reload": settings.reload,  # Configurado desde .env
        "reload_excludes": ["*.git*", "*.pyc", "__pycache__", "*.log", f"{settings.frontend_dir}/*"],  # Excluir archivos que no requieren reload
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
    
    # Cuando reload está habilitado, usar string de importación en lugar del objeto app
    if settings.reload:
        uvicorn.run("app.main:app", **config_kwargs)
    else:
        uvicorn.run(app, **config_kwargs)
