"""
Modelos Pydantic para SharePoint Online.
Define las estructuras de datos para sitios, listas, documentos y respuestas de API.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== SITIOS ====================

class SharePointSite(BaseModel):
    """Modelo para un sitio de SharePoint."""
    id: str = Field(..., description="ID único del sitio")
    name: Optional[str] = Field(None, description="Nombre del sitio")
    displayName: Optional[str] = Field(None, description="Nombre a mostrar del sitio")
    description: Optional[str] = Field(None, description="Descripción del sitio")
    webUrl: Optional[str] = Field(None, description="URL web del sitio")
    createdDateTime: Optional[datetime] = Field(None, description="Fecha de creación")
    lastModifiedDateTime: Optional[datetime] = Field(None, description="Fecha de última modificación")


class SitesListResponse(BaseModel):
    """Respuesta con lista de sitios."""
    value: List[SharePointSite] = Field(default_factory=list, description="Lista de sitios")
    count: int = Field(0, description="Número total de sitios")
    nextLink: Optional[str] = Field(None, alias="@odata.nextLink", description="URL para siguiente página")


# ==================== LISTAS ====================

class SharePointList(BaseModel):
    """Modelo para una lista de SharePoint."""
    id: str = Field(..., description="ID único de la lista")
    name: Optional[str] = Field(None, description="Nombre interno de la lista")
    displayName: Optional[str] = Field(None, description="Nombre a mostrar de la lista")
    description: Optional[str] = Field(None, description="Descripción de la lista")
    webUrl: Optional[str] = Field(None, description="URL web de la lista")
    createdDateTime: Optional[datetime] = Field(None, description="Fecha de creación")
    lastModifiedDateTime: Optional[datetime] = Field(None, description="Fecha de última modificación")
    listTemplate: Optional[str] = Field(None, description="Plantilla de lista utilizada")


class ListsResponse(BaseModel):
    """Respuesta con lista de listas de SharePoint."""
    value: List[SharePointList] = Field(default_factory=list, description="Lista de listas")
    count: int = Field(0, description="Número total de listas")


class ListItemFields(BaseModel):
    """Campos de un elemento de lista."""
    Title: Optional[str] = Field(None, description="Título del elemento")
    # Campos personalizados se pueden agregar dinámicamente
    
    class Config:
        extra = "allow"  # Permite campos adicionales


class ListItem(BaseModel):
    """Modelo para un elemento de lista."""
    id: str = Field(..., description="ID único del elemento")
    createdDateTime: Optional[datetime] = Field(None, description="Fecha de creación")
    lastModifiedDateTime: Optional[datetime] = Field(None, description="Fecha de última modificación")
    webUrl: Optional[str] = Field(None, description="URL web del elemento")
    fields: Optional[Dict[str, Any]] = Field(None, description="Campos del elemento")


class ListItemsResponse(BaseModel):
    """Respuesta con elementos de lista."""
    value: List[ListItem] = Field(default_factory=list, description="Lista de elementos")
    count: int = Field(0, description="Número total de elementos")
    nextLink: Optional[str] = Field(None, alias="@odata.nextLink", description="URL para siguiente página")


class CreateListItemRequest(BaseModel):
    """Request para crear un elemento de lista."""
    fields: Dict[str, Any] = Field(..., description="Campos del elemento a crear")


class UpdateListItemRequest(BaseModel):
    """Request para actualizar un elemento de lista."""
    fields: Dict[str, Any] = Field(..., description="Campos del elemento a actualizar")


# ==================== DRIVES (BIBLIOTECAS DE DOCUMENTOS) ====================

class DriveInfo(BaseModel):
    """Modelo para información de un drive (biblioteca de documentos)."""
    id: str = Field(..., description="ID único del drive")
    name: Optional[str] = Field(None, description="Nombre del drive")
    description: Optional[str] = Field(None, description="Descripción del drive")
    driveType: Optional[str] = Field(None, description="Tipo de drive (documentLibrary, etc.)")
    webUrl: Optional[str] = Field(None, description="URL web del drive")
    createdDateTime: Optional[datetime] = Field(None, description="Fecha de creación")


class DrivesResponse(BaseModel):
    """Respuesta con lista de drives."""
    value: List[DriveInfo] = Field(default_factory=list, description="Lista de drives")
    count: int = Field(0, description="Número total de drives")


class DriveItem(BaseModel):
    """Modelo para un elemento de drive (archivo o carpeta)."""
    id: str = Field(..., description="ID único del elemento")
    name: Optional[str] = Field(None, description="Nombre del elemento")
    size: Optional[int] = Field(None, description="Tamaño en bytes")
    webUrl: Optional[str] = Field(None, description="URL web del elemento")
    createdDateTime: Optional[datetime] = Field(None, description="Fecha de creación")
    lastModifiedDateTime: Optional[datetime] = Field(None, description="Fecha de última modificación")
    folder: Optional[Dict[str, Any]] = Field(None, description="Información de carpeta (si es carpeta)")
    file: Optional[Dict[str, Any]] = Field(None, description="Información de archivo (si es archivo)")
    downloadUrl: Optional[str] = Field(None, alias="@microsoft.graph.downloadUrl", description="URL de descarga directa")


class DriveItemsResponse(BaseModel):
    """Respuesta con elementos de drive."""
    value: List[DriveItem] = Field(default_factory=list, description="Lista de elementos")
    count: int = Field(0, description="Número total de elementos")
    nextLink: Optional[str] = Field(None, alias="@odata.nextLink", description="URL para siguiente página")


class UploadFileRequest(BaseModel):
    """Request para subir un archivo."""
    file_name: str = Field(..., description="Nombre del archivo")
    folder_path: str = Field("root", description="Path de la carpeta destino")
    # file_content se maneja como UploadFile en FastAPI


# ==================== BÚSQUEDA ====================

class SearchHit(BaseModel):
    """Resultado de búsqueda individual."""
    hitId: Optional[str] = Field(None, description="ID del resultado")
    rank: Optional[int] = Field(None, description="Ranking del resultado")
    summary: Optional[str] = Field(None, description="Resumen del resultado")
    resource: Optional[Dict[str, Any]] = Field(None, description="Recurso encontrado")


class SearchResponse(BaseModel):
    """Respuesta de búsqueda."""
    hits: List[SearchHit] = Field(default_factory=list, description="Resultados de búsqueda")
    total: int = Field(0, description="Total de resultados")


# ==================== RESPUESTAS GENERALES ====================

class SharePointOperationResponse(BaseModel):
    """Respuesta genérica para operaciones de SharePoint."""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo de la operación")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales de la respuesta")


class HealthCheckResponse(BaseModel):
    """Respuesta de health check."""
    status: str = Field(..., description="Estado del servicio (healthy/unhealthy)")
    auth_configured: bool = Field(..., description="Indica si la autenticación está configurada")
    token_valid: Optional[bool] = Field(None, description="Indica si el token es válido")
    root_site_accessible: Optional[bool] = Field(None, description="Indica si se puede acceder al sitio raíz")
    root_site_name: Optional[str] = Field(None, description="Nombre del sitio raíz")
    error: Optional[str] = Field(None, description="Error si hay alguno")


# ==================== CONFIGURACIÓN ====================

class SharePointConfig(BaseModel):
    """Configuración de SharePoint."""
    site_url: Optional[str] = Field(None, description="URL del sitio de SharePoint")
    site_id: Optional[str] = Field(None, description="ID del sitio de SharePoint")
    tenant_id: str = Field(..., description="ID del tenant de Azure AD")
    client_id: str = Field(..., description="ID de la aplicación de Azure AD")
    # client_secret no se expone por seguridad
