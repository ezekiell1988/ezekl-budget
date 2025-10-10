"""
Servicio principal para integración con Dynamics 365 CRM.
Proporciona métodos para interactuar con cuentas, contactos y casos.
"""

import aiohttp
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
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Realiza una petición HTTP a la API de Dynamics 365.
        
        Args:
            method: Método HTTP (GET, POST, PATCH, DELETE)
            endpoint: Endpoint relativo (ej: "accounts", "incidents")
            data: Datos JSON para el body (POST/PATCH)
            params: Parámetros de query string
            
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
        """Obtiene una lista paginada de casos de Dynamics 365."""
        
        params = {}
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip
        if filter_query:
            params["$filter"] = filter_query
        if select_fields:
            params["$select"] = select_fields
        if order_by:
            params["$orderby"] = order_by
        
        response = await self._make_request("GET", "incidents", params=params)
        
        cases = [CaseResponse(**case) for case in response.get("value", [])]
        
        return CasesListResponse(
            count=len(cases),
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
        
        params = {}
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip
        if filter_query:
            params["$filter"] = filter_query
        if select_fields:
            params["$select"] = select_fields
        if order_by:
            params["$orderby"] = order_by
        
        response = await self._make_request("GET", "accounts", params=params)
        
        accounts = [AccountResponse(**account) for account in response.get("value", [])]
        
        return AccountsListResponse(
            count=len(accounts),
            accounts=accounts,
            next_link=response.get("@odata.nextLink")
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
        
        params = {}
        if top:
            params["$top"] = top
        if skip:
            params["$skip"] = skip
        if filter_query:
            params["$filter"] = filter_query
        if select_fields:
            params["$select"] = select_fields
        if order_by:
            params["$orderby"] = order_by
        
        response = await self._make_request("GET", "contacts", params=params)
        
        contacts = [ContactResponse(**contact) for contact in response.get("value", [])]
        
        return ContactsListResponse(
            count=len(contacts),
            contacts=contacts,
            next_link=response.get("@odata.nextLink")
        )
    
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