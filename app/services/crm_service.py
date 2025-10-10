"""
Servicio principal para integración con Dynamics 365 CRM.
Proporciona métodos para interactuar con cuentas, contactos y casos.
"""

import aiohttp
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import HTTPException

from app.core.config import settings
from app.services.crm_auth import crm_auth_service
from app.models.crm import (
    CaseResponse, CasesListResponse, CaseCreateRequest, CaseUpdateRequest,
    AccountResponse, AccountsListResponse, AccountCreateRequest, AccountUpdateRequest,
    ContactResponse, ContactsListResponse, ContactCreateRequest, ContactUpdateRequest,
    CaseTypeCodesResponse, CRMOperationResponse, CRMHealthResponse, CRMDiagnoseResponse
)

logger = logging.getLogger(__name__)


class CRMService:
    """
    Servicio principal para integración con Dynamics 365 CRM.
    
    Proporciona métodos de alto nivel para gestionar entidades de CRM:
    - Casos (Incidents)
    - Cuentas (Accounts) 
    - Contactos (Contacts)
    
    Incluye funcionalidades de diagnóstico y health check.
    """
    
    def __init__(self):
        """Inicializa el servicio CRM."""
        self.api_version = getattr(settings, 'crm_api_version', 'v9.0')
        self.base_url = getattr(settings, 'crm_d365_base_url', None)
        
        if self.base_url:
            self.api_base_url = f"{self.base_url}/api/data/{self.api_version}"
        else:
            self.api_base_url = None
    
    @property
    def is_configured(self) -> bool:
        """Verifica si el servicio está correctamente configurado."""
        return crm_auth_service.is_configured and self.api_base_url is not None
    
    def _check_configuration(self):
        """Verifica la configuración antes de realizar operaciones."""
        if not self.is_configured:
            raise HTTPException(
                status_code=500,
                detail="Servicio CRM no configurado. Verifique las variables de entorno CRM_*"
            )
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        prefer_maxpagesize: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Realiza una petición HTTP a la API de Dynamics 365.
        
        Args:
            method: Método HTTP (GET, POST, PATCH, DELETE)
            endpoint: Endpoint relativo (ej: "accounts", "incidents")
            data: Datos JSON para el body (POST/PATCH)
            params: Parámetros de query string
            prefer_maxpagesize: Tamaño máximo de página (usar header Prefer en lugar de $top)
            
        Returns:
            Dict con la respuesta JSON de la API
            
        Raises:
            HTTPException: Si la petición falla
        """
        self._check_configuration()
        
        token = await crm_auth_service.get_access_token()
        url = f"{self.api_base_url}/{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }
        
        # Agregar header Prefer para paginación server-driven si se especifica
        if prefer_maxpagesize:
            headers["Prefer"] = f"odata.maxpagesize={prefer_maxpagesize}"
        
        if data:
            headers["Content-Type"] = "application/json"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params
                ) as resp:
                    
                    response_text = await resp.text()
                    
                    if resp.status >= 400:
                        logger.error(f"❌ Error en petición CRM: {method} {url} - HTTP {resp.status}")
                        logger.error(f"Response: {response_text}")
                        
                        try:
                            error_data = await resp.json() if response_text else {}
                            error_msg = error_data.get("error", {}).get("message", response_text)
                        except:
                            error_msg = response_text
                            
                        raise HTTPException(
                            status_code=resp.status,
                            detail=f"Error en CRM: {error_msg}"
                        )
                    
                    # Para operaciones POST/PATCH que retornan 204, no hay contenido JSON
                    if resp.status == 204:
                        return {"status": "success"}
                    
                    if response_text:
                        return await resp.json()
                    else:
                        return {"status": "success"}
                        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Error de conexión CRM: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error de conexión con Dynamics 365: {str(e)}"
            )
    
    # ========== MÉTODOS PARA CASOS (INCIDENTS) ==========
    
    async def get_cases(
        self,
        top: int = 10,
        skip: int = 0,
        filter_query: Optional[str] = None,
        select_fields: Optional[str] = None,
        order_by: Optional[str] = None
    ) -> CasesListResponse:
        """
        Obtiene una lista paginada de casos de Dynamics 365.
        
        IMPORTANTE: NO enviar $skip porque D365 no lo soporta.
        En su lugar, usamos Prefer: odata.maxpagesize header y @odata.nextLink
        para paginación server-driven.
        """
        
        # CRÍTICO: NO enviar $skip porque D365 no lo soporta
        params = {"$count": "true"}  # Solicitar el conteo total
        
        # NO incluir $skip - D365 no lo soporta
        # if skip:
        #     params["$skip"] = skip
        
        if filter_query:
            params["$filter"] = filter_query
        if select_fields:
            params["$select"] = select_fields
        if order_by:
            params["$orderby"] = order_by
        
        # Usar Prefer header para paginación en lugar de $top
        response = await self._make_request(
            "GET", 
            "incidents", 
            params=params,
            prefer_maxpagesize=top  # Usar header en lugar de query param
        )
        
        cases = [CaseResponse(**case) for case in response.get("value", [])]
        
        # Usar @odata.count si está disponible, de lo contrario usar len(cases)
        total_count = response.get("@odata.count", len(cases))
        
        logger.info(f"✅ Casos obtenidos: {len(cases)}, Total: {total_count}, hasNextLink: {response.get('@odata.nextLink') is not None}")
        
        return CasesListResponse(
            count=total_count,
            cases=cases,
            next_link=response.get("@odata.nextLink")
        )
    
    async def get_case_by_id(self, case_id: str) -> CaseResponse:
        """Obtiene un caso específico por su ID."""
        response = await self._make_request("GET", f"incidents({case_id})")
        return CaseResponse(**response)
    
    async def create_case(self, case_data: CaseCreateRequest) -> CRMOperationResponse:
        """Crea un nuevo caso en Dynamics 365."""
        
        # Preparar datos para D365
        d365_data = {
            "title": case_data.title,
        }
        
        if case_data.description:
            d365_data["description"] = case_data.description
        if case_data.casetypecode:
            d365_data["casetypecode"] = case_data.casetypecode
        if case_data.customer_account_id:
            d365_data["customerid_account@odata.bind"] = f"/accounts({case_data.customer_account_id})"
        if case_data.customer_contact_id:
            d365_data["customerid_contact@odata.bind"] = f"/contacts({case_data.customer_contact_id})"
        
        response = await self._make_request("POST", "incidents", data=d365_data)
        
        return CRMOperationResponse(
            status="success",
            message="Caso creado exitosamente"
        )
    
    async def update_case(self, case_id: str, case_data: CaseUpdateRequest) -> CRMOperationResponse:
        """Actualiza un caso existente."""
        
        d365_data = {}
        if case_data.title:
            d365_data["title"] = case_data.title
        if case_data.description:
            d365_data["description"] = case_data.description
        if case_data.casetypecode:
            d365_data["casetypecode"] = case_data.casetypecode
        
        await self._make_request("PATCH", f"incidents({case_id})", data=d365_data)
        
        return CRMOperationResponse(
            status="success",
            entity_id=case_id,
            message="Caso actualizado exitosamente"
        )
    
    async def delete_case(self, case_id: str) -> CRMOperationResponse:
        """Elimina un caso."""
        await self._make_request("DELETE", f"incidents({case_id})")
        
        return CRMOperationResponse(
            status="success",
            entity_id=case_id,
            message="Caso eliminado exitosamente"
        )
    
    async def get_cases_by_nextlink(self, next_link: str) -> CasesListResponse:
        """
        Obtiene la siguiente página de casos usando nextLink de Dynamics 365.
        
        Dynamics 365 usa server-driven paging con @odata.nextLink que incluye
        un $skiptoken (cookie de paginación). Este método usa el nextLink completo
        para obtener la siguiente página sin calcular offset manualmente.
        
        Args:
            next_link: URL completa del @odata.nextLink retornado por D365.
                      Ejemplo: "/api/data/v9.2/incidents?$select=...&$skiptoken=<cookie>"
        
        Returns:
            CasesListResponse con la siguiente página de casos y el nextLink
            para la página siguiente (si existe).
            
        Note:
            - NO modificar el nextLink, usarlo tal como viene
            - NO agregar parámetros adicionales
            - El $skiptoken es interno de D365, no intentar decodificarlo
        """
        self._check_configuration()
        
        logger.debug(f"🔗 nextLink recibido: {next_link[:150]}...")
        
        # Manejar URLs absolutas (https://...) y relativas (/api/data/...)
        if next_link.startswith("http://") or next_link.startswith("https://"):
            from urllib.parse import urlparse
            parsed = urlparse(next_link)
            path_and_query = parsed.path
            if parsed.query:
                path_and_query += f"?{parsed.query}"
            next_link = path_and_query
            logger.debug(f"🔗 URL convertida a relativa: {next_link[:150]}...")
        
        # Extraer solo la parte después de /api/data/v9.x/
        if "/api/data/" in next_link:
            parts = next_link.split(f"/api/data/{self.api_version}/")
            if len(parts) > 1:
                endpoint_with_params = parts[1]
            else:
                endpoint_with_params = next_link
        else:
            endpoint_with_params = next_link
        
        logger.debug(f"🔗 Endpoint extraído: {endpoint_with_params[:100]}...")
        
        # Construir URL manualmente para preservar el query string exacto
        token = await crm_auth_service.get_access_token()
        url = f"{self.api_base_url}/{endpoint_with_params}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Prefer": "odata.maxpagesize=25"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, headers=headers) as resp:
                    
                    if resp.status >= 400:
                        response_text = await resp.text()
                        logger.error(f"❌ Error en nextLink: GET {url} - HTTP {resp.status}")
                        logger.error(f"Response: {response_text}")
                        
                        try:
                            error_data = json.loads(response_text)
                            error_msg = error_data.get("error", {}).get("message", response_text)
                        except:
                            error_msg = response_text
                        
                        raise HTTPException(
                            status_code=resp.status,
                            detail=f"Error de Dynamics 365: {error_msg}"
                        )
                    
                    response = await resp.json()
                    
                    cases = [CaseResponse(**case) for case in response.get("value", [])]
                    total_count = response.get("@odata.count", len(cases))
                    
                    logger.info(f"✅ nextLink procesado: {len(cases)} casos obtenidos")
                    
                    return CasesListResponse(
                        count=total_count,
                        cases=cases,
                        next_link=response.get("@odata.nextLink")
                    )
                    
        except aiohttp.ClientError as e:
            logger.error(f"❌ Error de conexión procesando nextLink: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error de conexión con Dynamics 365: {str(e)}"
            )
    
    # ========== MÉTODOS PARA CUENTAS (ACCOUNTS) ==========
    
    async def get_accounts(
        self,
        top: int = 10,
        skip: int = 0,
        filter_query: Optional[str] = None,
        select_fields: Optional[str] = None,
        order_by: Optional[str] = None
    ) -> AccountsListResponse:
        """Obtiene una lista paginada de cuentas de Dynamics 365."""
        
        # CRÍTICO: NO enviar $skip porque D365 no lo soporta
        # En su lugar, usamos Prefer: odata.maxpagesize header
        params = {"$count": "true"}  # Solicitar el conteo total
        
        # NO incluir $skip - D365 no lo soporta
        # if skip:
        #     params["$skip"] = skip
        
        if filter_query:
            params["$filter"] = filter_query
        if select_fields:
            params["$select"] = select_fields
        if order_by:
            params["$orderby"] = order_by
        
        # Preparar headers con Prefer para paginación
        token = await crm_auth_service.get_access_token()
        url = f"{self.api_base_url}/accounts"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Prefer": f"odata.maxpagesize={top}"  # ✅ Esto hace que D365 retorne nextLink
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=url,
                    headers=headers,
                    params=params
                ) as resp:
                    
                    if resp.status >= 400:
                        response_text = await resp.text()
                        logger.error(f"❌ Error en petición CRM: GET {url} - HTTP {resp.status}")
                        logger.error(f"Response: {response_text}")
                        
                        try:
                            error_data = await resp.json() if response_text else {}
                            error_msg = error_data.get("error", {}).get("message", response_text)
                        except:
                            error_msg = response_text
                            
                        raise HTTPException(
                            status_code=resp.status,
                            detail=f"Error en CRM: {error_msg}"
                        )
                    
                    response = await resp.json()
                    
                    accounts = [AccountResponse(**account) for account in response.get("value", [])]
                    total_count = response.get("@odata.count", len(accounts))
                    next_link = response.get("@odata.nextLink")
                    
                    return AccountsListResponse(
                        count=total_count,
                        accounts=accounts,
                        next_link=next_link
                    )
                        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Error de conexión CRM: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error de conexión con Dynamics 365: {str(e)}"
            )
    
    async def get_accounts_by_nextlink(self, next_link: str) -> AccountsListResponse:
        """
        Obtiene la siguiente página de cuentas usando nextLink de Dynamics 365.
        
        Dynamics 365 usa server-driven paging con @odata.nextLink que incluye
        un $skiptoken (cookie de paginación). Este método usa el nextLink completo
        para obtener la siguiente página sin calcular offset manualmente.
        
        Args:
            next_link: URL completa del @odata.nextLink retornado por D365.
                      Ejemplo: "/api/data/v9.2/accounts?$select=...&$skiptoken=<cookie>"
        
        Returns:
            AccountsListResponse con la siguiente página de cuentas y el nextLink
            para la página siguiente (si existe).
            
        Note:
            - NO modificar el nextLink, usarlo tal como viene
            - NO agregar parámetros adicionales
            - El $skiptoken es interno de D365, no intentar decodificarlo
        """
        self._check_configuration()
        
        logger.debug(f"🔗 nextLink recibido: {next_link[:150]}...")
        
        # Manejar URLs absolutas (https://...) y relativas (/api/data/...)
        if next_link.startswith("http://") or next_link.startswith("https://"):
            # URL absoluta de D365 - extraer solo la parte del path y query
            # Ejemplo: "https://org.crm.dynamics.com/api/data/v9.2/accounts?..."
            from urllib.parse import urlparse
            parsed = urlparse(next_link)
            # parsed.path = "/api/data/v9.2/accounts"
            # parsed.query = "$select=...&$skiptoken=..."
            path_and_query = parsed.path
            if parsed.query:
                path_and_query += f"?{parsed.query}"
            next_link = path_and_query  # Ahora es relativo
            logger.debug(f"🔗 URL convertida a relativa: {next_link[:150]}...")
        
        # Extraer solo la parte después de /api/data/v9.x/
        if "/api/data/" in next_link:
            # next_link viene como: "/api/data/v9.2/accounts?$select=..."
            # Necesitamos solo: "accounts?$select=..."
            parts = next_link.split(f"/api/data/{self.api_version}/")
            if len(parts) > 1:
                endpoint_with_params = parts[1]
            else:
                endpoint_with_params = next_link
        else:
            endpoint_with_params = next_link
        
        logger.debug(f"🔗 Endpoint extraído: {endpoint_with_params[:100]}...")
        
        # Construir URL manualmente para preservar el query string exacto
        token = await crm_auth_service.get_access_token()
        url = f"{self.api_base_url}/{endpoint_with_params}"
        
        # CRÍTICO: Agregar Prefer header también en nextLink para mantener paginación
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Prefer": "odata.maxpagesize=25"  # ✅ Mantener el mismo tamaño de página
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, headers=headers) as resp:
                    
                    if resp.status >= 400:
                        response_text = await resp.text()
                        logger.error(f"❌ Error en nextLink: GET {url} - HTTP {resp.status}")
                        logger.error(f"Response: {response_text}")
                        
                        try:
                            error_data = await resp.json() if response_text else {}
                            error_msg = error_data.get("error", {}).get("message", response_text)
                        except:
                            error_msg = response_text
                            
                        raise HTTPException(
                            status_code=resp.status,
                            detail=f"Error en CRM nextLink: {error_msg}"
                        )
                    
                    response = await resp.json()
                    
                    accounts = [AccountResponse(**account) for account in response.get("value", [])]
                    total_count = response.get("@odata.count", len(accounts))
                    next_link_result = response.get("@odata.nextLink")
                    
                    return AccountsListResponse(
                        count=total_count,
                        accounts=accounts,
                        next_link=next_link_result
                    )
                        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Error de conexión CRM nextLink: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error de conexión con Dynamics 365: {str(e)}"
            )
    
    async def get_account_by_id(self, account_id: str) -> AccountResponse:
        """Obtiene una cuenta específica por su ID."""
        response = await self._make_request("GET", f"accounts({account_id})")
        return AccountResponse(**response)
    
    async def create_account(self, account_data: AccountCreateRequest) -> CRMOperationResponse:
        """Crea una nueva cuenta en Dynamics 365."""
        
        d365_data = {"name": account_data.name}
        
        # Mapear campos opcionales
        field_mapping = {
            "accountnumber": "accountnumber",
            "telephone1": "telephone1", 
            "emailaddress1": "emailaddress1",
            "websiteurl": "websiteurl",
            "address1_line1": "address1_line1",
            "address1_city": "address1_city",
            "address1_stateorprovince": "address1_stateorprovince",
            "address1_postalcode": "address1_postalcode",
            "address1_country": "address1_country"
        }
        
        for field, d365_field in field_mapping.items():
            value = getattr(account_data, field, None)
            if value:
                d365_data[d365_field] = value
        
        await self._make_request("POST", "accounts", data=d365_data)
        
        return CRMOperationResponse(
            status="success",
            message="Cuenta creada exitosamente"
        )
    
    async def update_account(self, account_id: str, account_data: AccountUpdateRequest) -> CRMOperationResponse:
        """Actualiza una cuenta existente."""
        
        d365_data = {}
        field_mapping = {
            "name": "name",
            "telephone1": "telephone1",
            "emailaddress1": "emailaddress1", 
            "websiteurl": "websiteurl",
            "address1_line1": "address1_line1",
            "address1_city": "address1_city",
            "address1_country": "address1_country"
        }
        
        for field, d365_field in field_mapping.items():
            value = getattr(account_data, field, None)
            if value:
                d365_data[d365_field] = value
        
        await self._make_request("PATCH", f"accounts({account_id})", data=d365_data)
        
        return CRMOperationResponse(
            status="success",
            entity_id=account_id,
            message="Cuenta actualizada exitosamente"
        )
    
    async def delete_account(self, account_id: str) -> CRMOperationResponse:
        """Elimina una cuenta."""
        await self._make_request("DELETE", f"accounts({account_id})")
        
        return CRMOperationResponse(
            status="success",
            entity_id=account_id,
            message="Cuenta eliminada exitosamente"
        )
    
    # ========== MÉTODOS PARA CONTACTOS (CONTACTS) ==========
    
    async def get_contacts(
        self,
        top: int = 10,
        skip: int = 0,
        filter_query: Optional[str] = None,
        select_fields: Optional[str] = None,
        order_by: Optional[str] = None
    ) -> ContactsListResponse:
        """Obtiene una lista paginada de contactos de Dynamics 365."""
        
        # CRÍTICO: NO enviar $skip porque D365 no lo soporta
        # En su lugar, usamos Prefer: odata.maxpagesize header
        params = {"$count": "true"}  # Solicitar el conteo total
        
        # NO incluir $skip - D365 no lo soporta
        # if skip:
        #     params["$skip"] = skip
        
        if filter_query:
            params["$filter"] = filter_query
        if select_fields:
            params["$select"] = select_fields
        if order_by:
            params["$orderby"] = order_by
        
        # Preparar headers con Prefer para paginación
        token = await crm_auth_service.get_access_token()
        url = f"{self.api_base_url}/contacts"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Prefer": f"odata.maxpagesize={top}"  # ✅ Usar Prefer header en lugar de $top
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status == 401:
                        logger.error("❌ Token de acceso expirado o inválido")
                        raise HTTPException(status_code=401, detail="Token de acceso inválido")
                    
                    if resp.status == 400:
                        error_text = await resp.text()
                        logger.error(f"❌ Error 400 en get_contacts: {error_text}")
                        raise HTTPException(status_code=400, detail=f"Error en la petición: {error_text}")
                    
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"❌ Error {resp.status} obteniendo contactos: {error_text}")
                        raise HTTPException(
                            status_code=resp.status,
                            detail=f"Error obteniendo contactos de D365: {error_text}"
                        )
                    
                    response = await resp.json()
                    
                    contacts = [ContactResponse(**contact) for contact in response.get("value", [])]
                    total_count = response.get("@odata.count", len(contacts))
                    
                    logger.info(f"✅ {len(contacts)} contactos obtenidos, hasNextLink: {response.get('@odata.nextLink') is not None}")
                    
                    return ContactsListResponse(
                        count=total_count,
                        contacts=contacts,
                        next_link=response.get("@odata.nextLink")
                    )
                    
        except aiohttp.ClientError as e:
            logger.error(f"❌ Error de conexión obteniendo contactos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error de conexión con D365: {str(e)}")
    
    async def get_contacts_by_nextlink(self, next_link: str) -> ContactsListResponse:
        """
        Obtiene la siguiente página de contactos usando nextLink de Dynamics 365.
        
        Dynamics 365 usa server-driven paging con @odata.nextLink que incluye
        un $skiptoken (cookie de paginación). Este método usa el nextLink completo
        para obtener la siguiente página sin calcular offset manualmente.
        
        Args:
            next_link: URL completa del @odata.nextLink retornado por D365.
                      Puede ser relativa: "/api/data/v9.2/contacts?..."
                      O absoluta: "https://org.crm.dynamics.com/api/data/v9.2/contacts?..."
        
        Returns:
            ContactsListResponse con la siguiente página de contactos y el nextLink
            para la página siguiente (si existe).
            
        Note:
            - NO modificar el nextLink, usarlo tal como viene
            - NO agregar parámetros adicionales
            - El $skiptoken es interno de D365, no intentar decodificarlo
        """
        self._check_configuration()
        
        logger.debug(f"🔗 nextLink recibido: {next_link[:150]}...")
        
        # Manejar URLs absolutas (https://...) y relativas (/api/data/...)
        if next_link.startswith("http://") or next_link.startswith("https://"):
            # URL absoluta de D365 - extraer solo la parte del path y query
            # Ejemplo: "https://org.crm.dynamics.com/api/data/v9.2/contacts?..."
            from urllib.parse import urlparse
            parsed = urlparse(next_link)
            # parsed.path = "/api/data/v9.2/contacts"
            # parsed.query = "$select=...&$skiptoken=..."
            path_and_query = parsed.path
            if parsed.query:
                path_and_query += f"?{parsed.query}"
            next_link = path_and_query  # Ahora es relativo
            logger.debug(f"🔗 URL convertida a relativa: {next_link[:150]}...")
        
        # Extraer solo la parte después de /api/data/v9.x/
        if "/api/data/" in next_link:
            # next_link viene como: "/api/data/v9.2/contacts?$select=..."
            # Necesitamos solo: "contacts?$select=..."
            parts = next_link.split(f"/api/data/{self.api_version}/")
            if len(parts) > 1:
                endpoint_with_params = parts[1]
            else:
                endpoint_with_params = next_link
        else:
            endpoint_with_params = next_link
        
        logger.debug(f"🔗 Endpoint extraído: {endpoint_with_params[:100]}...")
        
        # Construir URL manualmente para preservar el query string exacto
        token = await crm_auth_service.get_access_token()
        url = f"{self.api_base_url}/{endpoint_with_params}"
        
        # CRÍTICO: Agregar Prefer header también en nextLink para mantener paginación
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Prefer": "odata.maxpagesize=25"  # ✅ Mantener el mismo page size
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"❌ Error {resp.status} en nextLink: {error_text}")
                        raise HTTPException(
                            status_code=resp.status,
                            detail=f"Error obteniendo siguiente página de contactos: {error_text}"
                        )
                    
                    response = await resp.json()
                    
                    contacts = [ContactResponse(**contact) for contact in response.get("value", [])]
                    
                    logger.info(f"✅ {len(contacts)} contactos obtenidos, hasNextLink: {response.get('@odata.nextLink') is not None}")
                    
                    return ContactsListResponse(
                        count=len(contacts),  # Count de esta página
                        contacts=contacts,
                        next_link=response.get("@odata.nextLink")  # Siguiente página
                    )
                    
        except aiohttp.ClientError as e:
            logger.error(f"❌ Error de conexión en nextLink de contactos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")
    
    async def get_contact_by_id(self, contact_id: str) -> ContactResponse:
        """Obtiene un contacto específico por su ID."""
        response = await self._make_request("GET", f"contacts({contact_id})")
        return ContactResponse(**response)
    
    async def create_contact(self, contact_data: ContactCreateRequest) -> CRMOperationResponse:
        """Crea un nuevo contacto en Dynamics 365."""
        
        d365_data = {
            "firstname": contact_data.firstname,
            "lastname": contact_data.lastname
        }
        
        # Mapear campos opcionales
        field_mapping = {
            "emailaddress1": "emailaddress1",
            "telephone1": "telephone1",
            "mobilephone": "mobilephone", 
            "jobtitle": "jobtitle"
        }
        
        for field, d365_field in field_mapping.items():
            value = getattr(contact_data, field, None)
            if value:
                d365_data[d365_field] = value
        
        await self._make_request("POST", "contacts", data=d365_data)
        
        return CRMOperationResponse(
            status="success",
            message="Contacto creado exitosamente"
        )
    
    async def update_contact(self, contact_id: str, contact_data: ContactUpdateRequest) -> CRMOperationResponse:
        """Actualiza un contacto existente."""
        
        d365_data = {}
        field_mapping = {
            "firstname": "firstname",
            "lastname": "lastname",
            "emailaddress1": "emailaddress1",
            "telephone1": "telephone1",
            "mobilephone": "mobilephone",
            "jobtitle": "jobtitle"
        }
        
        for field, d365_field in field_mapping.items():
            value = getattr(contact_data, field, None)
            if value:
                d365_data[d365_field] = value
        
        await self._make_request("PATCH", f"contacts({contact_id})", data=d365_data)
        
        return CRMOperationResponse(
            status="success",
            entity_id=contact_id,
            message="Contacto actualizado exitosamente"
        )
    
    async def delete_contact(self, contact_id: str) -> CRMOperationResponse:
        """Elimina un contacto."""
        await self._make_request("DELETE", f"contacts({contact_id})")
        
        return CRMOperationResponse(
            status="success",
            entity_id=contact_id,
            message="Contacto eliminado exitosamente"
        )
    
    # ========== MÉTODOS DE DIAGNÓSTICO ==========
    
    async def health_check(self) -> CRMHealthResponse:
        """Realiza un health check del servicio CRM."""
        return CRMHealthResponse(
            status="ok" if self.is_configured else "error",
            d365=self.base_url or "No configurado",
            api_version=self.api_version
        )
    
    async def diagnose(self) -> CRMDiagnoseResponse:
        """Ejecuta un diagnóstico completo del servicio CRM."""
        
        results = {
            "environment_variables": {},
            "token_acquisition": {},
            "d365_connectivity": {},
            "recommendations": []
        }
        
        # Verificar variables de entorno
        env_vars = {
            "CRM_TENANT_ID": getattr(settings, 'crm_tenant_id', None),
            "CRM_CLIENT_ID": getattr(settings, 'crm_client_id', None), 
            "CRM_CLIENT_SECRET": getattr(settings, 'crm_client_secret', None),
            "CRM_D365_BASE_URL": getattr(settings, 'crm_d365_base_url', None)
        }
        
        for var, value in env_vars.items():
            results["environment_variables"][var] = "✓ Set" if value else "✗ Missing"
        
        if not all(env_vars.values()):
            results["recommendations"].append("Configure todas las variables de entorno CRM requeridas")
            return CRMDiagnoseResponse(**results)
        
        # Intentar obtener token
        try:
            token = await crm_auth_service.get_access_token()
            token_info = crm_auth_service.get_token_info()
            
            results["token_acquisition"]["status"] = "✓ Success"
            results["token_acquisition"]["token_length"] = len(token)
            results["token_acquisition"]["expires_at"] = token_info["expires_at"]
            results["token_acquisition"]["expires_in_seconds"] = token_info["expires_in_seconds"]
            
        except Exception as e:
            results["token_acquisition"]["status"] = "✗ Failed"
            results["token_acquisition"]["error"] = str(e)
            results["recommendations"].append("Verificar configuración de Azure AD app registration")
            return CRMDiagnoseResponse(**results)
        
        # Probar conectividad con D365
        try:
            whoami_response = await self._make_request("GET", "WhoAmI")
            
            results["d365_connectivity"]["status"] = "✓ Connected"
            results["d365_connectivity"]["user_id"] = whoami_response.get("UserId")
            results["d365_connectivity"]["business_unit_id"] = whoami_response.get("BusinessUnitId")
            results["d365_connectivity"]["organization_id"] = whoami_response.get("OrganizationId")
            results["recommendations"].append("✅ Configuración correcta!")
            
        except Exception as e:
            results["d365_connectivity"]["status"] = "✗ Failed"
            results["d365_connectivity"]["error"] = str(e)
            results["recommendations"].append(f"Error de conectividad: {str(e)}")
        
        return CRMDiagnoseResponse(**results)


# Instancia global del servicio CRM
crm_service = CRMService()