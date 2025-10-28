"""
Rutas para gestión de SharePoint Online.
Proporciona endpoints completos para sitios, listas, documentos y búsqueda.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Optional
import logging
import io

from app.services.sharepoint_service import sharepoint_service
from app.models.sharepoint import (
    SharePointSite, SitesListResponse, ListsResponse, ListItemsResponse,
    ListItem, CreateListItemRequest, UpdateListItemRequest,
    DrivesResponse, DriveItemsResponse, DriveItem,
    SearchResponse, SharePointOperationResponse, HealthCheckResponse
)
from app.api.routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sharepoint", tags=["SharePoint Online"])


# ==================== HEALTH CHECK ====================

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check del servicio SharePoint",
    description="""
    Verifica el estado del servicio de SharePoint Online.
    
    **Validaciones:**
    - Configuración de autenticación
    - Validez del token de acceso
    - Accesibilidad al sitio raíz
    """
)
async def health_check(current_user: dict = Depends(get_current_user)):
    """Verifica la salud del servicio de SharePoint."""
    try:
        result = await sharepoint_service.health_check()
        return result
    except Exception as e:
        logger.error(f"❌ Error en health check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SITIOS ====================

@router.get(
    "/sites",
    response_model=SitesListResponse,
    summary="Listar sitios de SharePoint",
    description="""
    Obtiene una lista de sitios de SharePoint accesibles.
    
    **Funcionalidad:**
    - Búsqueda opcional por término
    - Retorna información básica de cada sitio
    """
)
async def list_sites(
    current_user: dict = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Término de búsqueda opcional")
):
    """Lista todos los sitios de SharePoint."""
    try:
        result = await sharepoint_service.list_sites(search=search)
        
        return SitesListResponse(
            value=result.get("value", []),
            count=len(result.get("value", []))
        )
    except Exception as e:
        logger.error(f"❌ Error listando sitios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sites/root",
    response_model=SharePointSite,
    summary="Obtener sitio raíz",
    description="""
    Obtiene información del sitio raíz de SharePoint.
    """
)
async def get_root_site(current_user: dict = Depends(get_current_user)):
    """Obtiene el sitio raíz de SharePoint."""
    try:
        result = await sharepoint_service.get_root_site()
        return result
    except Exception as e:
        logger.error(f"❌ Error obteniendo sitio raíz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sites/{site_id}",
    response_model=SharePointSite,
    summary="Obtener sitio por ID",
    description="""
    Obtiene información de un sitio específico por su ID.
    """
)
async def get_site_by_id(
    site_id: str = Path(..., description="ID del sitio de SharePoint"),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene un sitio específico por su ID."""
    try:
        result = await sharepoint_service.get_site_by_id(site_id)
        return result
    except Exception as e:
        logger.error(f"❌ Error obteniendo sitio {site_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LISTAS ====================

@router.get(
    "/sites/{site_id}/lists",
    response_model=ListsResponse,
    summary="Listar listas de un sitio",
    description="""
    Obtiene todas las listas de SharePoint de un sitio.
    """
)
async def get_lists(
    site_id: str = Path(..., description="ID del sitio"),
    current_user: dict = Depends(get_current_user)
):
    """Lista todas las listas de un sitio."""
    try:
        result = await sharepoint_service.get_lists(site_id)
        
        return ListsResponse(
            value=result.get("value", []),
            count=len(result.get("value", []))
        )
    except Exception as e:
        logger.error(f"❌ Error obteniendo listas del sitio {site_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sites/{site_id}/lists/{list_id}",
    summary="Obtener lista por ID",
    description="""
    Obtiene información de una lista específica.
    """
)
async def get_list_by_id(
    site_id: str = Path(..., description="ID del sitio"),
    list_id: str = Path(..., description="ID de la lista"),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene una lista específica."""
    try:
        result = await sharepoint_service.get_list_by_id(site_id, list_id)
        return result
    except Exception as e:
        logger.error(f"❌ Error obteniendo lista {list_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sites/{site_id}/lists/{list_id}/items",
    response_model=ListItemsResponse,
    summary="Obtener elementos de lista",
    description="""
    Obtiene los elementos de una lista de SharePoint.
    
    **Funcionalidad:**
    - Paginación con top y skip
    - Filtros OData
    - Expansión de campos
    """
)
async def get_list_items(
    site_id: str = Path(..., description="ID del sitio"),
    list_id: str = Path(..., description="ID de la lista"),
    current_user: dict = Depends(get_current_user),
    top: int = Query(100, description="Número máximo de elementos", ge=1, le=1000),
    skip: int = Query(0, description="Número de elementos a saltar", ge=0),
    filter_query: Optional[str] = Query(None, description="Filtro OData")
):
    """Obtiene los elementos de una lista."""
    try:
        result = await sharepoint_service.get_list_items(
            site_id=site_id,
            list_id=list_id,
            top=top,
            skip=skip,
            filter_query=filter_query
        )
        
        return ListItemsResponse(
            value=result.get("value", []),
            count=len(result.get("value", [])),
            nextLink=result.get("@odata.nextLink")
        )
    except Exception as e:
        logger.error(f"❌ Error obteniendo elementos de lista {list_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/sites/{site_id}/lists/{list_id}/items",
    response_model=SharePointOperationResponse,
    summary="Crear elemento de lista",
    description="""
    Crea un nuevo elemento en una lista de SharePoint.
    """
)
async def create_list_item(
    site_id: str = Path(..., description="ID del sitio"),
    list_id: str = Path(..., description="ID de la lista"),
    item_data: CreateListItemRequest = ...,
    current_user: dict = Depends(get_current_user)
):
    """Crea un nuevo elemento en una lista."""
    try:
        result = await sharepoint_service.create_list_item(
            site_id=site_id,
            list_id=list_id,
            fields=item_data.fields
        )
        
        return SharePointOperationResponse(
            success=True,
            message="Elemento creado exitosamente",
            data=result
        )
    except Exception as e:
        logger.error(f"❌ Error creando elemento en lista {list_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/sites/{site_id}/lists/{list_id}/items/{item_id}",
    response_model=SharePointOperationResponse,
    summary="Actualizar elemento de lista",
    description="""
    Actualiza un elemento existente en una lista de SharePoint.
    """
)
async def update_list_item(
    site_id: str = Path(..., description="ID del sitio"),
    list_id: str = Path(..., description="ID de la lista"),
    item_id: str = Path(..., description="ID del elemento"),
    item_data: UpdateListItemRequest = ...,
    current_user: dict = Depends(get_current_user)
):
    """Actualiza un elemento de una lista."""
    try:
        result = await sharepoint_service.update_list_item(
            site_id=site_id,
            list_id=list_id,
            item_id=item_id,
            fields=item_data.fields
        )
        
        return SharePointOperationResponse(
            success=True,
            message="Elemento actualizado exitosamente",
            data=result
        )
    except Exception as e:
        logger.error(f"❌ Error actualizando elemento {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/sites/{site_id}/lists/{list_id}/items/{item_id}",
    response_model=SharePointOperationResponse,
    summary="Eliminar elemento de lista",
    description="""
    Elimina un elemento de una lista de SharePoint.
    """
)
async def delete_list_item(
    site_id: str = Path(..., description="ID del sitio"),
    list_id: str = Path(..., description="ID de la lista"),
    item_id: str = Path(..., description="ID del elemento"),
    current_user: dict = Depends(get_current_user)
):
    """Elimina un elemento de una lista."""
    try:
        await sharepoint_service.delete_list_item(
            site_id=site_id,
            list_id=list_id,
            item_id=item_id
        )
        
        return SharePointOperationResponse(
            success=True,
            message="Elemento eliminado exitosamente"
        )
    except Exception as e:
        logger.error(f"❌ Error eliminando elemento {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DRIVES (BIBLIOTECAS DE DOCUMENTOS) ====================

@router.get(
    "/sites/{site_id}/drives",
    response_model=DrivesResponse,
    summary="Listar bibliotecas de documentos",
    description="""
    Obtiene todas las bibliotecas de documentos de un sitio.
    """
)
async def get_drives(
    site_id: str = Path(..., description="ID del sitio"),
    current_user: dict = Depends(get_current_user)
):
    """Lista todas las bibliotecas de documentos de un sitio."""
    try:
        result = await sharepoint_service.get_drives(site_id)
        
        return DrivesResponse(
            value=result.get("value", []),
            count=len(result.get("value", []))
        )
    except Exception as e:
        logger.error(f"❌ Error obteniendo drives del sitio {site_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sites/{site_id}/drives/{drive_id}/items",
    response_model=DriveItemsResponse,
    summary="Listar elementos de biblioteca",
    description="""
    Obtiene los elementos (archivos y carpetas) de una biblioteca de documentos.
    """
)
async def get_drive_items(
    site_id: str = Path(..., description="ID del sitio"),
    drive_id: str = Path(..., description="ID del drive"),
    current_user: dict = Depends(get_current_user),
    folder_path: str = Query("root", description="Path de la carpeta (default: root)")
):
    """Obtiene los elementos de una biblioteca de documentos."""
    try:
        result = await sharepoint_service.get_drive_items(
            site_id=site_id,
            drive_id=drive_id,
            folder_path=folder_path
        )
        
        return DriveItemsResponse(
            value=result.get("value", []),
            count=len(result.get("value", [])),
            nextLink=result.get("@odata.nextLink")
        )
    except Exception as e:
        logger.error(f"❌ Error obteniendo elementos del drive {drive_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/sites/{site_id}/drives/{drive_id}/upload",
    response_model=SharePointOperationResponse,
    summary="Subir archivo",
    description="""
    Sube un archivo a una biblioteca de documentos de SharePoint.
    """
)
async def upload_file(
    site_id: str = Path(..., description="ID del sitio"),
    drive_id: str = Path(..., description="ID del drive"),
    file: UploadFile = File(..., description="Archivo a subir"),
    current_user: dict = Depends(get_current_user),
    folder_path: str = Query("root", description="Path de la carpeta destino")
):
    """Sube un archivo a SharePoint."""
    try:
        file_content = await file.read()
        
        result = await sharepoint_service.upload_file(
            site_id=site_id,
            drive_id=drive_id,
            file_name=file.filename,
            file_content=file_content,
            folder_path=folder_path
        )
        
        return SharePointOperationResponse(
            success=True,
            message=f"Archivo '{file.filename}' subido exitosamente",
            data=result
        )
    except Exception as e:
        logger.error(f"❌ Error subiendo archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sites/{site_id}/drives/{drive_id}/items/{item_id}/download",
    summary="Descargar archivo",
    description="""
    Descarga un archivo de una biblioteca de documentos de SharePoint.
    """
)
async def download_file(
    site_id: str = Path(..., description="ID del sitio"),
    drive_id: str = Path(..., description="ID del drive"),
    item_id: str = Path(..., description="ID del elemento"),
    current_user: dict = Depends(get_current_user)
):
    """Descarga un archivo de SharePoint."""
    try:
        file_content = await sharepoint_service.download_file(
            site_id=site_id,
            drive_id=drive_id,
            item_id=item_id
        )
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=document"}
        )
    except Exception as e:
        logger.error(f"❌ Error descargando archivo {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/sites/{site_id}/drives/{drive_id}/items/{item_id}",
    response_model=SharePointOperationResponse,
    summary="Eliminar archivo",
    description="""
    Elimina un archivo o carpeta de una biblioteca de documentos.
    """
)
async def delete_file(
    site_id: str = Path(..., description="ID del sitio"),
    drive_id: str = Path(..., description="ID del drive"),
    item_id: str = Path(..., description="ID del elemento"),
    current_user: dict = Depends(get_current_user)
):
    """Elimina un archivo de SharePoint."""
    try:
        await sharepoint_service.delete_file(
            site_id=site_id,
            drive_id=drive_id,
            item_id=item_id
        )
        
        return SharePointOperationResponse(
            success=True,
            message="Elemento eliminado exitosamente"
        )
    except Exception as e:
        logger.error(f"❌ Error eliminando archivo {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== BÚSQUEDA ====================

@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Buscar contenido en SharePoint",
    description="""
    Busca contenido en SharePoint Online.
    
    **Funcionalidad:**
    - Búsqueda global o por sitio
    - Busca en archivos, listas y sitios
    """
)
async def search(
    query: str = Query(..., description="Término de búsqueda"),
    current_user: dict = Depends(get_current_user),
    site_id: Optional[str] = Query(None, description="ID del sitio (opcional)")
):
    """Busca contenido en SharePoint."""
    try:
        result = await sharepoint_service.search(query=query, site_id=site_id)
        
        # Procesar resultados de búsqueda
        hits = []
        if "value" in result and len(result["value"]) > 0:
            hitsContainers = result["value"][0].get("hitsContainers", [])
            if hitsContainers:
                hits = hitsContainers[0].get("hits", [])
        
        return SearchResponse(
            hits=hits,
            total=len(hits)
        )
    except Exception as e:
        logger.error(f"❌ Error en búsqueda: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
