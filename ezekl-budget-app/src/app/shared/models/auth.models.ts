/**
 * Interfaces para autenticación - coinciden con los schemas del backend
 */

// Request para generar token de login
export interface LoginTokenRequest {
  codeLogin: string;
}

// Response de generar token
export interface LoginTokenResponse {
  success: boolean;
  message: string;
  idLogin: number;
}

// Request para login con token
export interface LoginRequest {
  idLogin: number;
  token: string;
}

// Datos del usuario
export interface UserData {
  idMerchant: number;
  idLogin: number;
  codeLogin: string;
  nameLogin: string;
  phoneLogin: string;
  emailLogin: string;
}

// Response de login exitoso
export interface LoginResponse {
  success: boolean;
  message: string;
  user: UserData;
  token: string;
  expiresAt: string;
}

// Response de logout
export interface LogoutResponse {
  success: boolean;
  message: string;
}

// Response de refresh token
export interface RefreshTokenResponse {
  success: boolean;
  message: string;
  token: string;
  expiresAt: string;
}

// Response de user info (/me)
export interface UserInfoResponse {
  success: boolean;
  user: UserData;
  expiresAt: string;
  issuedAt?: string;
}
