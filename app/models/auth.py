"""
Modelos Pydantic para autenticación del sistema Ezekl Budget.
Contiene todas las estructuras de datos para el flujo de login de 2 pasos con JWE.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class RequestTokenRequest(BaseModel):
    """
    Modelo para solicitar un token temporal de acceso.
    
    Primer paso del flujo de autenticación de 2 pasos.
    """
    
    codeLogin: str = Field(
        description="Código de usuario único en el sistema",
        min_length=1,
        max_length=50,
        examples=["S", "admin", "user123"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "codeLogin": "S"
            }
        }


class RequestTokenResponse(BaseModel):
    """
    Modelo de respuesta para la solicitud de token temporal.
    
    Confirma si se generó y envió el token por email.
    """
    
    success: bool = Field(
        description="Indica si el token fue generado y enviado exitosamente",
        examples=[True, False]
    )
    
    message: str = Field(
        description="Mensaje descriptivo del resultado",
        examples=[
            "Token enviado por email exitosamente",
            "Código de usuario no encontrado",
            "Error generando token"
        ]
    )
    
    tokenGenerated: bool = Field(
        description="Indica específicamente si se generó un token válido",
        examples=[True, False]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Token enviado por email exitosamente",
                "tokenGenerated": True
            }
        }


class LoginRequest(BaseModel):
    """
    Modelo para el login con token temporal.
    
    Segundo paso del flujo de autenticación de 2 pasos.
    """
    
    codeLogin: str = Field(
        description="Código de usuario único en el sistema",
        min_length=1,
        max_length=50,
        examples=["S", "admin", "user123"]
    )
    
    token: str = Field(
        description="Token temporal de 5 dígitos recibido por email",
        min_length=5,
        max_length=5,
        pattern=r"^\d{5}$",
        examples=["12345", "67890", "47422"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "codeLogin": "S",
                "token": "47422"
            }
        }


class UserData(BaseModel):
    """
    Modelo para los datos del usuario autenticado.
    
    Representa la información básica del usuario que se incluye en los tokens
    y se retorna en las respuestas de autenticación.
    """
    
    idLogin: int = Field(
        description="ID único del usuario en la base de datos",
        examples=[1, 2, 100]
    )
    
    codeLogin: str = Field(
        description="Código de usuario único",
        examples=["S", "admin", "user123"]
    )
    
    nameLogin: str = Field(
        description="Nombre completo del usuario",
        examples=["Ezequiel Baltodano Cubillo", "Admin User", "Juan Pérez"]
    )
    
    phoneLogin: Optional[str] = Field(
        default=None,
        description="Número de teléfono del usuario",
        examples=["50683681485", "+1234567890", None]
    )
    
    emailLogin: Optional[str] = Field(
        default=None,
        description="Dirección de email del usuario",
        examples=["ezekiell1988@hotmail.com", "admin@ezekl.com", None]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "idLogin": 1,
                "codeLogin": "S",
                "nameLogin": "Ezequiel Baltodano Cubillo",
                "phoneLogin": "50683681485",
                "emailLogin": "ezekiell1988@hotmail.com"
            }
        }


class LoginResponse(BaseModel):
    """
    Modelo de respuesta para el login exitoso.
    
    Contiene el token JWE de sesión y los datos del usuario autenticado.
    """
    
    success: bool = Field(
        description="Indica si la autenticación fue exitosa",
        examples=[True, False]
    )
    
    message: str = Field(
        description="Mensaje descriptivo del resultado",
        examples=[
            "Autenticación exitosa",
            "Credenciales inválidas o token expirado",
            "Error en datos de autenticación"
        ]
    )
    
    user: Optional[UserData] = Field(
        default=None,
        description="Datos del usuario autenticado (solo si success=True)"
    )
    
    accessToken: Optional[str] = Field(
        default=None,
        description="Token JWE de sesión para autenticación posterior (solo si success=True)",
        examples=["eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2R0NNIn0..."]
    )
    
    expiresAt: Optional[str] = Field(
        default=None,
        description="Fecha y hora de expiración del token en formato ISO 8601 (solo si success=True)",
        examples=["2025-10-06T18:58:58.368145+00:00"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "examples": [
                {
                    "description": "Login exitoso",
                    "value": {
                        "success": True,
                        "message": "Autenticación exitosa",
                        "user": {
                            "idLogin": 1,
                            "codeLogin": "S",
                            "nameLogin": "Ezequiel Baltodano Cubillo",
                            "phoneLogin": "50683681485",
                            "emailLogin": "ezekiell1988@hotmail.com"
                        },
                        "accessToken": "eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2R0NNIn0...",
                        "expiresAt": "2025-10-06T18:58:58.368145+00:00"
                    }
                },
                {
                    "description": "Login fallido",
                    "value": {
                        "success": False,
                        "message": "Credenciales inválidas o token expirado"
                    }
                }
            ]
        }


class VerifyTokenResponse(BaseModel):
    """
    Modelo de respuesta para la verificación de token (endpoint privado).
    
    Contiene los datos del usuario autenticado y información del token.
    """
    
    user: UserData = Field(
        description="Datos completos del usuario autenticado"
    )
    
    expiresAt: Optional[str] = Field(
        default=None,
        description="Fecha y hora de expiración del token en formato ISO 8601",
        examples=["2025-10-06T18:58:58+00:00"]
    )
    
    issuedAt: Optional[str] = Field(
        default=None,
        description="Fecha y hora de emisión del token en formato ISO 8601",
        examples=["2025-10-05T18:58:58+00:00"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "user": {
                    "idLogin": 1,
                    "codeLogin": "S",
                    "nameLogin": "Ezequiel Baltodano Cubillo",
                    "phoneLogin": "50683681485",
                    "emailLogin": "ezekiell1988@hotmail.com"
                },
                "expiresAt": "2025-10-06T18:58:58+00:00",
                "issuedAt": "2025-10-05T18:58:58+00:00"
            }
        }


class LogoutResponse(BaseModel):
    """
    Modelo de respuesta para el logout.
    
    Confirma que la sesión fue cerrada exitosamente.
    """
    
    success: bool = Field(
        description="Indica si el logout fue procesado exitosamente",
        examples=[True]
    )
    
    message: str = Field(
        description="Mensaje confirmando el cierre de sesión",
        examples=["Sesión cerrada exitosamente"]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Sesión cerrada exitosamente"
            }
        }


# Modelos para errores comunes de autenticación
class AuthErrorResponse(BaseModel):
    """
    Modelo de respuesta para errores de autenticación.
    
    Usado en casos de tokens inválidos, expirados, o errores de formato.
    """
    
    detail: str = Field(
        description="Mensaje detallado del error",
        examples=[
            "Token de autorización requerido",
            "Formato de autorización inválido. Use: Bearer <token>",
            "Esquema de autorización inválido. Use: Bearer <token>",
            "Token inválido o expirado",
            "Datos de usuario no encontrados en token"
        ]
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "detail": "Token inválido o expirado"
            }
        }
