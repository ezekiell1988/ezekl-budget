"""
Endpoints para integración con Microsoft Copilot Studio.
Proporciona autenticación y comunicación con el agente usando Direct Line.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
import httpx
import os
from dotenv import load_dotenv

from app.utils.auth import get_current_user
from app.models.auth import CurrentUser

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logger = logging.getLogger(__name__)

# Router para endpoints de Copilot Studio
router = APIRouter(prefix="/copilot", tags=["Copilot Studio"])

# Configuración de Copilot Studio desde variables de entorno
COPILOT_ENVIRONMENT_ID = os.getenv("COPILOT_ENVIRONMENT_ID", "")
COPILOT_SCHEMA_NAME = os.getenv("COPILOT_SCHEMA_NAME", "")
COPILOT_TENANT_ID = os.getenv("COPILOT_TENANT_ID", "")
COPILOT_AGENT_APP_ID = os.getenv("COPILOT_AGENT_APP_ID", "")
COPILOT_CLIENT_SECRET = os.getenv("COPILOT_CLIENT_SECRET", "")

# Endpoints
TOKEN_ENDPOINT = f"https://login.microsoftonline.com/{COPILOT_TENANT_ID}/oauth2/v2.0/token"

# Endpoint del SDK de Copilot Studio (conversaciones autenticadas)
# Basado en la cadena de conexión: https://3c48723d81b5473a9006a54c8652fe.7c.environment.api.powerplatform.com/copilotstudio/dataverse-backed/authenticated/bots/cr389_agent_ROzgg7/conversations
COPILOT_SDK_ENDPOINT = f"https://{COPILOT_ENVIRONMENT_ID}.7c.environment.api.powerplatform.com/copilotstudio/dataverse-backed/authenticated/bots/{COPILOT_SCHEMA_NAME}/conversations"


async def get_access_token() -> str:
    """
    Obtiene un access token de Microsoft Entra ID para el agente de Copilot Studio.
    
    Returns:
        str: Access token válido
        
    Raises:
        HTTPException: Si no se puede obtener el token
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TOKEN_ENDPOINT,
                data={
                    "grant_type": "client_credentials",
                    "client_id": COPILOT_AGENT_APP_ID,
                    "client_secret": COPILOT_CLIENT_SECRET,
                    "scope": "https://api.powerplatform.com/.default"
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"Error al obtener access token: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al obtener access token: {response.status_code}"
                )
            
            data = response.json()
            return data.get("access_token", "")
            
    except httpx.TimeoutException:
        logger.error("Timeout al obtener access token")
        raise HTTPException(
            status_code=504,
            detail="Timeout al obtener access token"
        )
    except httpx.RequestError as e:
        logger.error(f"Error de red al obtener access token: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Error de red al obtener access token"
        )


@router.get(
    "/copilot/token",
    summary="Obtener token de Copilot Studio (Privado)",
    description="""Genera un token de autenticación para el agente de Copilot Studio.
    
    🔒 **Este endpoint requiere autenticación.**
    
    Este endpoint genera un token temporal que permite al cliente conectarse 
    de forma segura con el agente de Copilot Studio usando el SDK de Power Platform.
    
    **Seguridad:**
    - Requiere token JWE válido en header Authorization
    - Genera token temporal usando OAuth2 con Power Platform API
    - No expone las credenciales del agente al cliente
    
    **Información devuelta:**
    - Token temporal de conversación
    - ID de conversación
    - URL de streaming WebSocket (si aplica)
    - Duración de validez del token
    
    **Casos de uso:**
    - Establecer conexión con agente de Copilot Studio
    - Chat en tiempo real con bot personalizado
    - Integración segura con Copilot Studio SDK
    """,
    responses={
        200: {
            "description": "Token generado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "conversationId": "abc123def456",
                        "streamUrl": "wss://...",
                        "expires_in": 3600
                    }
                }
            },
        },
        401: {"description": "No autenticado"},
        500: {"description": "Error al generar token"},
    },
)
async def get_directline_token(current_user: CurrentUser = Depends(get_current_user)):
    """
    Genera un token de conversación para autenticación con Copilot Studio SDK.
    
    Args:
        current_user: Usuario autenticado (inyectado por Depends)

    Returns:
        dict: Token de conversación y datos asociados
    """
    logger.info("=" * 80)
    logger.info("🚀 INICIO - Solicitud de token de Copilot Studio")
    logger.info("=" * 80)
    
    try:
        # Validar configuración
        logger.info("🔍 PASO 1: Validando configuración de variables de entorno...")
        logger.info(f"   - COPILOT_ENVIRONMENT_ID: {'✅ Configurado' if COPILOT_ENVIRONMENT_ID else '❌ Falta'}")
        logger.info(f"   - COPILOT_TENANT_ID: {'✅ Configurado' if COPILOT_TENANT_ID else '❌ Falta'}")
        logger.info(f"   - COPILOT_AGENT_APP_ID: {'✅ Configurado' if COPILOT_AGENT_APP_ID else '❌ Falta'}")
        logger.info(f"   - COPILOT_CLIENT_SECRET: {'✅ Configurado' if COPILOT_CLIENT_SECRET else '❌ Falta'}")
        logger.info(f"   - COPILOT_SCHEMA_NAME: {'✅ Configurado' if COPILOT_SCHEMA_NAME else '❌ Falta'}")
        
        if not all([COPILOT_ENVIRONMENT_ID, COPILOT_TENANT_ID, COPILOT_AGENT_APP_ID, COPILOT_CLIENT_SECRET, COPILOT_SCHEMA_NAME]):
            logger.error("❌ ERROR: Configuración incompleta de Copilot Studio")
            raise HTTPException(
                status_code=500,
                detail="Configuración incompleta de Copilot Studio. Verifica las variables de entorno."
            )
        
        logger.info("✅ Configuración validada correctamente")

        # Obtener access token de Microsoft Entra ID
        logger.info("🔍 PASO 2: Obteniendo access token de Microsoft Entra ID...")
        logger.info(f"   - Token Endpoint: {TOKEN_ENDPOINT}")
        logger.info(f"   - Client ID: {COPILOT_AGENT_APP_ID}")
        logger.info(f"   - Scope: https://api.powerplatform.com/.default")
        
        access_token = await get_access_token()
        
        if not access_token:
            logger.error("❌ ERROR: No se pudo obtener access token")
            raise HTTPException(
                status_code=500,
                detail="No se pudo obtener access token"
            )

        logger.info(f"✅ Access token obtenido exitosamente (longitud: {len(access_token)} caracteres)")
        
        # Información del usuario
        logger.info("� PASO 3: Información del usuario autenticado...")
        logger.info(f"   - Usuario: {current_user.get('nameLogin', 'Desconocido')}")
        logger.info(f"   - Email: {current_user.get('email', 'No disponible')}")
        
        # Preparar request a Copilot Studio
        logger.info("🔍 PASO 4: Preparando request a Copilot Studio SDK...")
        logger.info(f"   - Endpoint: {COPILOT_SDK_ENDPOINT}")
        logger.info(f"   - Método: POST")
        logger.info(f"   - API Version: 2022-03-01-preview")
        logger.info(f"   - Authorization: Bearer {access_token[:20]}...")

        # Crear conversación usando el SDK de Copilot Studio
        async with httpx.AsyncClient() as client:
            logger.info("📡 Enviando request a Copilot Studio...")
            
            response = await client.post(
                COPILOT_SDK_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                params={"api-version": "2022-03-01-preview"},
                json={},
                timeout=10.0
            )

            logger.info(f"📡 Respuesta recibida - Status Code: {response.status_code}")
            logger.info(f"📄 Response Headers:")
            for key, value in response.headers.items():
                logger.info(f"   - {key}: {value}")
            
            if response.status_code not in [200, 201]:
                error_detail = ""
                try:
                    error_data = response.json()
                    logger.error(f"❌ Error JSON: {error_data}")
                    error_detail = f" - Detalle: {error_data}"
                except:
                    error_text = response.text[:500]
                    logger.error(f"❌ Error Texto: {error_text}")
                    error_detail = f" - Texto: {error_text}"
                
                logger.error("=" * 80)
                logger.error(f"❌ FALLO - Error al crear conversación: {response.status_code}")
                logger.error("=" * 80)
                
                # Mensaje de ayuda según el error
                if response.status_code == 401:
                    help_msg = "El access token no tiene los permisos correctos. Verifica Azure AD API Permissions."
                elif response.status_code == 403:
                    help_msg = "Acceso denegado. Verifica que el agente tenga autenticación manual habilitada."
                elif response.status_code == 404:
                    help_msg = "Endpoint no encontrado. Verifica COPILOT_ENVIRONMENT_ID y COPILOT_SCHEMA_NAME."
                elif response.status_code == 405:
                    help_msg = "Método no permitido. El agente necesita 'Autenticación Manual' habilitada y publicada."
                else:
                    help_msg = "Error desconocido. Revisa los logs anteriores."
                
                logger.error(f"💡 AYUDA: {help_msg}")
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al crear conversación con Copilot Studio: {response.status_code}. {help_msg}{error_detail}"
                )

            data = response.json()
            logger.info("✅ Conversación creada exitosamente")
            logger.info(f"   - Conversation ID: {data.get('conversationId', 'N/A')}")
            logger.info(f"   - Token presente: {'✅ Sí' if data.get('token') else '❌ No'}")
            logger.info(f"   - Stream URL presente: {'✅ Sí' if data.get('streamUrl') else '❌ No'}")
            logger.info(f"   - Expires in: {data.get('expires_in', 'N/A')} segundos")
            
            logger.info("=" * 80)
            logger.info("🎉 ÉXITO - Token de Copilot Studio generado correctamente")
            logger.info("=" * 80)

            return {
                "token": data.get("token"),
                "conversationId": data.get("conversationId"),
                "streamUrl": data.get("streamUrl"),
                "expires_in": data.get("expires_in", 3600),
            }

    except httpx.TimeoutException:
        logger.error("=" * 80)
        logger.error("⏱️ TIMEOUT - Timeout al conectar con Copilot Studio SDK")
        logger.error(f"   - Endpoint: {COPILOT_SDK_ENDPOINT}")
        logger.error(f"   - Tiempo límite: 10 segundos")
        logger.error("=" * 80)
        raise HTTPException(
            status_code=504,
            detail="Timeout al conectar con Copilot Studio (10s)"
        )
    except httpx.RequestError as e:
        logger.error("=" * 80)
        logger.error(f"🌐 ERROR DE RED - Error al conectar con Copilot Studio")
        logger.error(f"   - Tipo de error: {type(e).__name__}")
        logger.error(f"   - Mensaje: {str(e)}")
        logger.error(f"   - Endpoint intentado: {COPILOT_SDK_ENDPOINT}")
        logger.error("=" * 80)
        raise HTTPException(
            status_code=503,
            detail=f"Error de red al conectar con Copilot Studio: {type(e).__name__} - {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"💥 ERROR INESPERADO - {type(e).__name__}")
        logger.error(f"   - Mensaje: {str(e)}")
        logger.error(f"   - Tipo: {type(e)}")
        logger.error("=" * 80)
        import traceback
        logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al generar token: {type(e).__name__} - {str(e)}"
        )
