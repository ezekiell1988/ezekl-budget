/**
 * Modelos de autenticación - 100% compatibles con OpenAPI backend
 * Base URL: /api/v1/auth/
 * Actualizado: 14 de enero de 2026
 */

// ========================================
// REQUEST MODELS
// ========================================

/**
 * Paso 1: Solicitar token temporal (PIN)
 * POST /api/v1/auth/request-token
 */
export interface RequestTokenRequest {
  codeLogin: string;
}

/**
 * Paso 2: Login con token temporal
 * POST /api/v1/auth/login
 */
export interface LoginRequest {
  codeLogin: string;
  token: string;
}

// ========================================
// RESPONSE MODELS
// ========================================

/**
 * Response al solicitar token (Paso 1)
 */
export interface RequestTokenResponse {
  success: boolean;
  message: string;
  tokenGenerated: boolean;
}

/**
 * Datos del usuario autenticado
 */
export interface UserData {
  idLogin: number;
  codeLogin: string;
  nameLogin: string;
  phoneLogin: string | null;
  emailLogin: string | null;
  idCompany?: number | null;
  email?: string | null; // Alias de emailLogin
}

/**
 * Response de login exitoso (Paso 2)
 */
export interface LoginResponse {
  success: boolean;
  message: string;
  user: UserData;
  accessToken: string; // JWE token
  expiresAt: string; // ISO 8601 format
}

/**
 * Response de verify-token (GET /api/v1/auth/verify-token.json)
 * Requiere autenticación: Bearer token
 */
export interface VerifyTokenResponse {
  user: UserData;
  expiresAt: string | null;
  issuedAt: string | null;
}

/**
 * Response de refresh-token (POST /api/v1/auth/refresh-token)
 * Requiere autenticación: Bearer token
 */
export interface RefreshTokenResponse {
  success: boolean;
  message: string;
  accessToken: string;
  expiresAt: string;
}

/**
 * Response de logout (POST /api/v1/auth/logout)
 * Requiere autenticación: Bearer token
 */
export interface LogoutResponse {
  success: boolean;
  message: string;
  microsoft_logout_url?: string | null;
  redirect_required?: boolean;
}

/**
 * Error response genérico de autenticación
 */
export interface AuthErrorResponse {
  detail: string;
}

// ========================================
// DEPRECATED (mantener para compatibilidad)
// ========================================

/** @deprecated Usar RequestTokenRequest */
export interface LoginTokenRequest {
  codeLogin: string;
}

/** @deprecated Usar RequestTokenResponse */
export interface LoginTokenResponse {
  success: boolean;
  message: string;
  idLogin?: number;
  tokenGenerated: boolean;
}

/** @deprecated Usar VerifyTokenResponse */
export interface UserInfoResponse {
  success: boolean;
  user: UserData;
  expiresAt: string;
  issuedAt?: string;
}
