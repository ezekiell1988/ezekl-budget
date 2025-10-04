"""
Aplicación FastAPI para ezekl-budget.
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from app.settings import settings


# Inicializar la aplicación FastAPI
app = FastAPI(
    title="Ezekl Budget API",
    description="API para gestión de presupuesto con credenciales Azure OpenAI",
    version="1.0.0",
)


class CredentialsResponse(BaseModel):
    """Modelo de respuesta para las credenciales."""
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    message: str


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirecciona a la documentación de la API."""
    return RedirectResponse(url="/docs")


@app.get("/credentials", response_model=CredentialsResponse)
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


@app.get("/health")
async def health_check():
    """
    Endpoint de salud para verificar que la API está funcionando.
    
    Returns:
        dict: Estado de la aplicación
    """
    return {
        "status": "healthy",
        "message": "Ezekl Budget API está funcionando correctamente",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
