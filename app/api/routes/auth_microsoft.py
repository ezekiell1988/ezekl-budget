"""
Rutas para autenticación con Microsoft Azure AD.
Proporciona endpoints para OAuth2, asociación de cuentas y gestión de sesiones.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone
from typing import Dict, Any
import logging
import json
import base64
import uuid
from urllib.parse import urlencode, urlparse

from app.core.config import settings
from app.core.redis import redis_client
from app.models.auth import (
    LoginResponse,
    UserData,
    MicrosoftUrlRequest,
    MicrosoftUrlResponse,
)
from app.utils.auth import get_current_user, create_jwe_token, execute_stored_procedure

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/microsoft",tags=["Autenticación - Microsoft"])


# ==================== INICIAR AUTENTICACIÓN ====================

@router.post(
    "/url",
    response_model=MicrosoftUrlResponse,
    summary="Iniciar autenticación con Microsoft con URL de retorno personalizada",
    description="""Inicia el flujo de autenticación con Microsoft y retorna la URL de autenticación.
    
    Este endpoint:
    1. Recibe una URL de retorno donde se redirigirá al usuario después del login
    2. Guarda la URL en Redis con un identificador único (24 horas de expiración)
    3. Retorna la URL de Microsoft para que el cliente redirija manualmente
    4. Al completar la autenticación, Microsoft redirige al callback que redirige a la URL especificada con el token JWT
    
    Ejemplo de uso:
    ```javascript
    const response = await fetch('/auth/microsoft/url', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({redirect_url: 'https://miapp.com/callback'})
    });
    const data = await response.json();
    window.location.href = data.auth_url; // Redirigir manualmente
    ```
    
    Resultado final:
    Después de la autenticación, el usuario será redirigido a: https://miapp.com/callback?token=eyJhbGc...
    """,
    responses={
        200: {
            "model": MicrosoftUrlResponse,
            "description": "URL de autenticación generada exitosamente",
        },
        400: {"description": "URL de retorno inválida o faltante"},
        500: {"description": "Error interno del servidor"},
    },
)
async def microsoft_login_with_redirect(data: MicrosoftUrlRequest):
    """Inicia autenticación con Microsoft con URL de retorno personalizada."""
    try:
        redirect_url = data.redirect_url

        # Validar que la URL sea válida
        try:
            parsed = urlparse(redirect_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("URL inválida")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="redirect_url debe ser una URL válida (ej: https://ejemplo.com/callback)",
            )

        # Validar credenciales de Azure AD
        if not all(
            [
                settings.azure_client_id,
                settings.azure_tenant_id,
                settings.azure_client_secret,
            ]
        ):
            logger.error("Credenciales de Azure AD no configuradas")
            raise HTTPException(
                status_code=500,
                detail="Autenticación con Microsoft no está configurada",
            )

        # Generar identificador único para este flujo
        flow_id = str(uuid.uuid4())

        # Guardar URL de retorno en Redis (expira en 24 horas)
        redis_key = f"microsoft_redirect:{flow_id}"
        await redis_client.set(
            redis_key,
            {
                "redirect_url": redirect_url,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            expires_in_seconds=86400,  # 24 horas
        )

        logger.info(
            f"✅ URL de redirección guardada en Redis: {flow_id} -> {redirect_url}"
        )

        # Crear state con el flow_id para identificar este flujo
        state_data = {"flow_type": "url_redirect", "flow_id": flow_id}
        state_encoded = base64.urlsafe_b64encode(
            json.dumps(state_data).encode()
        ).decode()

        # Construir URL de autorización de Microsoft
        base_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/authorize"

        params = {
            "client_id": settings.azure_client_id,
            "response_type": "code",
            "redirect_uri": settings.effective_microsoft_redirect_uri,
            "scope": "openid profile email User.Read",
            "response_mode": "query",
            "state": state_encoded,
        }

        auth_url = f"{base_url}?{urlencode(params)}"

        # Retornar JSON con la URL (el cliente debe redirigir manualmente)
        return MicrosoftUrlResponse(
            success=True,
            message="URL de autenticación generada exitosamente",
            auth_url=auth_url,
            flow_id=flow_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en microsoft_login_with_redirect: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get(
    "",
    summary="Iniciar autenticación con Microsoft",
    description="Redirige al usuario a Microsoft Azure AD para autenticación OAuth2",
)
async def microsoft_login():
    """Endpoint para iniciar el flujo de autenticación con Microsoft."""
    try:
        # Validar que las credenciales de Azure AD estén configuradas
        if not all(
            [
                settings.azure_client_id,
                settings.azure_tenant_id,
                settings.azure_client_secret,
            ]
        ):
            logger.error("Credenciales de Azure AD no configuradas")
            raise HTTPException(
                status_code=500,
                detail="Autenticación con Microsoft no está configurada",
            )

        # Construir URL de autorización de Microsoft
        base_url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/authorize"

        # Parámetros para la autenticación OAuth2
        params = {
            "client_id": settings.azure_client_id,
            "response_type": "code",
            "redirect_uri": settings.effective_microsoft_redirect_uri,
            "scope": "openid profile email User.Read",
            "response_mode": "query",
            "state": "security_token_here",  # En producción, usar un token seguro
        }

        # Construir URL completa
        auth_url = f"{base_url}?{urlencode(params)}"

        # Redirigir al usuario a Microsoft
        return RedirectResponse(url=auth_url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al construir URL de Microsoft: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# ==================== ASOCIACIÓN DE CUENTAS ====================

@router.post(
    "/associate",
    response_model=LoginResponse,
    summary="Asociar cuenta Microsoft con usuario existente",
    description="""Asocia una cuenta de Microsoft con un usuario existente del sistema.
    
    Este endpoint:
    1. Valida que el codeLogin existe en el sistema
    2. Valida que el codeLoginMicrosoft existe y no está asociado
    3. Crea la asociación entre ambas cuentas
    4. **AUTENTICA automáticamente al usuario (igual que spLoginAuth + login())**
    5. Genera un token JWE de sesión para el usuario
    6. Retorna el token y datos del usuario
    
    **Flujo de uso:**
    - Usuario se autentica con Microsoft (callback redirige con microsoft_pending=true)
    - Frontend muestra formulario de asociación
    - Usuario ingresa su codeLogin existente
    - Frontend llama este endpoint
    - Sistema asocia cuentas y autentica automáticamente (misma respuesta que login normal)
    
    **Seguridad:**
    - Validación de existencia de ambos códigos
    - Prevención de doble asociación
    - Autenticación completa como en flujo de login normal
    - Token JWE seguro con expiración
    """,
)
async def associate_microsoft_account(data: dict):
    """
    Asocia una cuenta de Microsoft con un usuario existente y lo autentica.

    Después de asociar exitosamente, hace exactamente lo mismo que:
    - spLoginAuth.sql (validación y autenticación)
    - función login() de Python (generación de token JWE)

    Args:
        data: {"codeLogin": "ABC123", "codeLoginMicrosoft": "uuid-de-microsoft"}

    Returns:
        LoginResponse idéntica al login normal con token JWE y datos del usuario
    """
    try:
        code_login = data.get("codeLogin")
        code_login_microsoft = data.get("codeLoginMicrosoft")

        if not code_login or not code_login_microsoft:
            raise HTTPException(
                status_code=400, detail="codeLogin y codeLoginMicrosoft son requeridos"
            )

        # Preparar parámetros para el stored procedure de asociación
        association_data = {
            "codeLogin": code_login,
            "codeLoginMicrosoft": code_login_microsoft,
        }

        json_param = json.dumps(association_data)
        result = await execute_stored_procedure(
            "spLoginLoginMicrosoftAssociate", json_param
        )

        if not result.get("success"):
            error_message = result.get("message", "Error desconocido en la asociación")
            logger.error(f"Error en asociación: {error_message}")

            # Determinar tipo de error para respuesta más específica
            if "not found" in error_message.lower():
                raise HTTPException(status_code=404, detail=error_message)
            elif "already associated" in error_message.lower():
                raise HTTPException(status_code=409, detail=error_message)
            else:
                raise HTTPException(status_code=400, detail=error_message)

        # Obtener datos del usuario asociado
        user_data = result.get("userData", {})

        if not user_data:
            logger.error("No se obtuvieron datos del usuario tras la asociación")
            raise HTTPException(
                status_code=500, detail="Error obteniendo datos del usuario"
            )

        # Crear token JWE para el usuario
        jwe_token, expiry_date = create_jwe_token(user_data)

        # Guardar sesión en Redis también
        from app.services.auth_service import auth_service

        user_email = user_data.get("email")
        if user_email:
            await auth_service.save_session(
                user_id=user_email,
                user_data=user_data,
                session_type="web",
                expires_in_seconds=86400,  # 24 horas
            )

        return LoginResponse(
            success=True,
            message="Autenticación exitosa",
            user=UserData(**user_data),
            accessToken=jwe_token,
            expiresAt=expiry_date.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en asociación Microsoft: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post(
    "/associate/whatsapp",
    summary="Asociar cuenta Microsoft con usuario existente (WhatsApp)",
    description="""Endpoint específico para asociar cuenta Microsoft desde WhatsApp.
    
    Similar a /microsoft/associate pero:
    1. Valida el token temporal de WhatsApp
    2. Asocia las cuentas usando spLoginLoginMicrosoftAssociate
    3. Crea sesión en Redis para WhatsApp (no devuelve token JWE)
    4. Retorna éxito para que el frontend redirija a WhatsApp
    """,
)
async def associate_microsoft_account_whatsapp(data: dict):
    """
    Asocia cuenta Microsoft con usuario existente y crea sesión de WhatsApp.

    Args:
        data: {
            "codeLogin": "USR001",
            "codeLoginMicrosoft": "uuid-microsoft",
            "phoneNumber": "5491112345678",
            "whatsappToken": "token-temporal"
        }

    Returns:
        {"success": True, "message": "...", "user": {...}}
    """
    try:
        code_login = data.get("codeLogin")
        code_login_microsoft = data.get("codeLoginMicrosoft")
        phone_number = data.get("phoneNumber")
        whatsapp_token = data.get("whatsappToken")

        if not all([code_login, code_login_microsoft, phone_number, whatsapp_token]):
            raise HTTPException(
                status_code=400, detail="Todos los campos son requeridos"
            )

        # Validar token temporal de WhatsApp
        from app.services.whatsapp_service import whatsapp_service

        token_data = await whatsapp_service.get_phone_from_auth_token(whatsapp_token)

        if not token_data or token_data[0] != phone_number:
            raise HTTPException(
                status_code=401, detail="Token de WhatsApp inválido o expirado"
            )

        # Ejecutar SP de asociación
        association_data = {
            "codeLogin": code_login,
            "codeLoginMicrosoft": code_login_microsoft,
        }

        json_param = json.dumps(association_data)
        result = await execute_stored_procedure(
            "spLoginLoginMicrosoftAssociate", json_param
        )

        if not result.get("success"):
            error_message = result.get("message", "Error en la asociación")
            logger.error(f"Error en asociación WhatsApp: {error_message}")

            if (
                "not found" in error_message.lower()
                or "no encontrado" in error_message.lower()
            ):
                raise HTTPException(status_code=404, detail=error_message)
            elif (
                "already associated" in error_message.lower()
                or "ya está asociada" in error_message.lower()
            ):
                raise HTTPException(status_code=409, detail=error_message)
            else:
                raise HTTPException(status_code=400, detail=error_message)

        # Obtener datos del usuario asociado
        user_data = result.get("userData", {})

        if not user_data:
            raise HTTPException(
                status_code=500, detail="Error obteniendo datos del usuario"
            )

        # Guardar sesión de WhatsApp en Redis (24 horas)
        await whatsapp_service.save_whatsapp_auth(
            phone_number=phone_number, user_data=user_data, expires_in_seconds=86400
        )

        # Eliminar token temporal (ya fue usado)
        await whatsapp_service.delete_auth_token(whatsapp_token)

        logger.info(
            f"✅ Cuenta Microsoft asociada y sesión WhatsApp creada para {phone_number}"
        )

        return {
            "success": True,
            "message": "Cuenta asociada exitosamente",
            "user": user_data,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en asociación Microsoft WhatsApp: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
