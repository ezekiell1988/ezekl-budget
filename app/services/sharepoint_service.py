"""
Servicio principal para interactuar con SharePoint Online a través de Microsoft Graph API.
Proporciona operaciones CRUD para sitios, listas, documentos y más.
"""

import logging
import aiohttp
from typing import Dict, Any, Optional, List
from urllib.parse import quote, urlparse

from app.services.sharepoint_auth import sharepoint_auth_service

logger = logging.getLogger(__name__)


class SharePointService:
    """
    Servicio para interactuar con SharePoint Online usando Microsoft Graph API.
    
    Funcionalidades:
    - Gestión de sitios de SharePoint
    - Gestión de listas y bibliotecas de documentos
    - Operaciones con documentos (subir, descargar, eliminar)
    - Búsqueda de contenido
    """
    
    def __init__(self):
        """Inicializa el servicio de SharePoint."""
        from app.core.config import settings
        
        self.graph_base_url = "https://graph.microsoft.com/v1.0"
        self.sharepoint_site_url = getattr(settings, 'sharepoint_site_url', None)
        
        # Extraer site_id si se proporciona URL completa de SharePoint
        self.site_hostname = None
        self.site_path = None
        
        if self.sharepoint_site_url:
            parsed = urlparse(self.sharepoint_site_url)
            self.site_hostname = parsed.netloc
            self.site_path = parsed.path.strip('/')
    
    @property
    def is_configured(self) -> bool:
        """Verifica si el servicio está configurado."""
        return sharepoint_auth_service.is_configured
    
    async def _get_headers(self) -> Dict[str, str]:
        """Obtiene headers HTTP con token de autenticación."""
        token = await sharepoint_auth_service.get_access_token()
        
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    # ==================== SITIOS ====================
    
    async def get_root_site(self) -> Dict[str, Any]:
        """
        Obtiene información del sitio raíz de SharePoint.
        
        Returns:
            dict: Información del sitio raíz
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/root"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_site_by_path(self, hostname: str, site_path: str) -> Dict[str, Any]:
        """
        Obtiene información de un sitio específico por su hostname y path.
        
        Args:
            hostname: Hostname del sitio (ej: contoso.sharepoint.com)
            site_path: Path del sitio (ej: /sites/team-site)
            
        Returns:
            dict: Información del sitio
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{hostname}:/{site_path}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_site_by_id(self, site_id: str) -> Dict[str, Any]:
        """
        Obtiene información de un sitio por su ID.
        
        Args:
            site_id: ID del sitio
            
        Returns:
            dict: Información del sitio
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{site_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def list_sites(self, search: Optional[str] = None) -> Dict[str, Any]:
        """
        Lista todos los sitios de SharePoint accesibles.
        
        Args:
            search: Término de búsqueda opcional
            
        Returns:
            dict: Lista de sitios
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites"
        
        if search:
            url += f"?search={quote(search)}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
    
    # ==================== LISTAS ====================
    
    async def get_lists(self, site_id: str) -> Dict[str, Any]:
        """
        Obtiene todas las listas de un sitio.
        
        Args:
            site_id: ID del sitio
            
        Returns:
            dict: Listas del sitio
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{site_id}/lists"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_list_by_id(self, site_id: str, list_id: str) -> Dict[str, Any]:
        """
        Obtiene información de una lista específica.
        
        Args:
            site_id: ID del sitio
            list_id: ID de la lista
            
        Returns:
            dict: Información de la lista
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{site_id}/lists/{list_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_list_items(
        self, 
        site_id: str, 
        list_id: str,
        top: int = 100,
        skip: int = 0,
        filter_query: Optional[str] = None,
        expand: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene elementos de una lista.
        
        Args:
            site_id: ID del sitio
            list_id: ID de la lista
            top: Número máximo de elementos
            skip: Número de elementos a saltar
            filter_query: Filtro OData
            expand: Campos a expandir
            
        Returns:
            dict: Elementos de la lista
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{site_id}/lists/{list_id}/items"
        
        params = {
            "$top": top,
            "$skip": skip,
            "$expand": "fields"
        }
        
        if filter_query:
            params["$filter"] = filter_query
        
        if expand:
            params["$expand"] = expand
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()
    
    async def create_list_item(
        self, 
        site_id: str, 
        list_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea un nuevo elemento en una lista.
        
        Args:
            site_id: ID del sitio
            list_id: ID de la lista
            fields: Campos del elemento
            
        Returns:
            dict: Elemento creado
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{site_id}/lists/{list_id}/items"
        
        body = {"fields": fields}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as response:
                response.raise_for_status()
                return await response.json()
    
    async def update_list_item(
        self, 
        site_id: str, 
        list_id: str,
        item_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza un elemento de una lista.
        
        Args:
            site_id: ID del sitio
            list_id: ID de la lista
            item_id: ID del elemento
            fields: Campos a actualizar
            
        Returns:
            dict: Elemento actualizado
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{site_id}/lists/{list_id}/items/{item_id}"
        
        body = {"fields": fields}
        
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=body) as response:
                response.raise_for_status()
                return await response.json()
    
    async def delete_list_item(
        self, 
        site_id: str, 
        list_id: str,
        item_id: str
    ) -> bool:
        """
        Elimina un elemento de una lista.
        
        Args:
            site_id: ID del sitio
            list_id: ID de la lista
            item_id: ID del elemento
            
        Returns:
            bool: True si se eliminó correctamente
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{site_id}/lists/{list_id}/items/{item_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                response.raise_for_status()
                return True
    
    # ==================== DRIVES (BIBLIOTECAS DE DOCUMENTOS) ====================
    
    async def get_drives(self, site_id: str) -> Dict[str, Any]:
        """
        Obtiene todas las bibliotecas de documentos de un sitio.
        
        Args:
            site_id: ID del sitio
            
        Returns:
            dict: Bibliotecas de documentos
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{site_id}/drives"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_drive_items(
        self, 
        site_id: str, 
        drive_id: str,
        folder_path: str = "root"
    ) -> Dict[str, Any]:
        """
        Obtiene los elementos de una carpeta en una biblioteca de documentos.
        
        Args:
            site_id: ID del sitio
            drive_id: ID del drive
            folder_path: Path de la carpeta (default: root)
            
        Returns:
            dict: Elementos de la carpeta
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        
        if folder_path == "root":
            url = f"{self.graph_base_url}/sites/{site_id}/drives/{drive_id}/root/children"
        else:
            url = f"{self.graph_base_url}/sites/{site_id}/drives/{drive_id}/root:/{folder_path}:/children"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def upload_file(
        self, 
        site_id: str, 
        drive_id: str,
        file_name: str,
        file_content: bytes,
        folder_path: str = "root"
    ) -> Dict[str, Any]:
        """
        Sube un archivo a una biblioteca de documentos.
        
        Args:
            site_id: ID del sitio
            drive_id: ID del drive
            file_name: Nombre del archivo
            file_content: Contenido del archivo en bytes
            folder_path: Path de la carpeta destino
            
        Returns:
            dict: Información del archivo subido
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        headers["Content-Type"] = "application/octet-stream"
        
        if folder_path == "root":
            url = f"{self.graph_base_url}/sites/{site_id}/drives/{drive_id}/root:/{file_name}:/content"
        else:
            url = f"{self.graph_base_url}/sites/{site_id}/drives/{drive_id}/root:/{folder_path}/{file_name}:/content"
        
        timeout = aiohttp.ClientTimeout(total=60.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.put(url, headers=headers, data=file_content) as response:
                response.raise_for_status()
                return await response.json()
    
    async def download_file(
        self, 
        site_id: str, 
        drive_id: str,
        item_id: str
    ) -> bytes:
        """
        Descarga un archivo de una biblioteca de documentos.
        
        Args:
            site_id: ID del sitio
            drive_id: ID del drive
            item_id: ID del elemento
            
        Returns:
            bytes: Contenido del archivo
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{site_id}/drives/{drive_id}/items/{item_id}/content"
        
        timeout = aiohttp.ClientTimeout(total=60.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.read()
    
    async def delete_file(
        self, 
        site_id: str, 
        drive_id: str,
        item_id: str
    ) -> bool:
        """
        Elimina un archivo de una biblioteca de documentos.
        
        Args:
            site_id: ID del sitio
            drive_id: ID del drive
            item_id: ID del elemento
            
        Returns:
            bool: True si se eliminó correctamente
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/sites/{site_id}/drives/{drive_id}/items/{item_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                response.raise_for_status()
                return True
    
    # ==================== BÚSQUEDA ====================
    
    async def search(self, query: str, site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Busca contenido en SharePoint.
        
        Args:
            query: Término de búsqueda
            site_id: ID del sitio (opcional, busca en todos los sitios si no se especifica)
            
        Returns:
            dict: Resultados de búsqueda
        """
        if not self.is_configured:
            raise Exception("Servicio de SharePoint no configurado")
        
        headers = await self._get_headers()
        url = f"{self.graph_base_url}/search/query"
        
        request_body = {
            "requests": [
                {
                    "entityTypes": ["driveItem", "listItem", "site"],
                    "query": {
                        "queryString": query
                    }
                }
            ]
        }
        
        if site_id:
            request_body["requests"][0]["query"]["filters"] = {
                "siteId": site_id
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=request_body) as response:
                response.raise_for_status()
                return await response.json()
    
    # ==================== DIAGNÓSTICO ====================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica la salud del servicio de SharePoint.
        
        Returns:
            dict: Estado del servicio
        """
        try:
            token_info = sharepoint_auth_service.get_token_info()
            
            # Intentar obtener el sitio raíz
            root_site = await self.get_root_site()
            
            return {
                "status": "healthy",
                "auth_configured": self.is_configured,
                "token_valid": token_info["is_valid"],
                "root_site_accessible": bool(root_site),
                "root_site_name": root_site.get("displayName", "N/A")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "auth_configured": self.is_configured,
                "error": str(e)
            }


# Instancia global del servicio
sharepoint_service = SharePointService()
