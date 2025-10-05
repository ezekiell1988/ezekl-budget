/**
 * Modelos y tipos para el sistema de autenticación
 */

// Usuario autenticado
export interface AuthUser {
  idLogin: number;
  codeLogin: string;
  nameLogin: string;
  phoneLogin?: string;
  emailLogin: string;
}

// Request para solicitar token
export interface RequestTokenRequest {
  codeLogin: string;
}

// Response de solicitud de token
export interface RequestTokenResponse {
  success: boolean;
  message: string;
  user?: AuthUser;
  tokenGenerated?: boolean;
}

// Request para login con token
export interface LoginRequest {
  codeLogin: string;
  token: string;
}

// Response de login
export interface LoginResponse {
  success: boolean;
  message: string;
  user?: AuthUser;
  accessToken?: string; // JWE token
  expiresAt?: string; // ISO date string
}

// Response para refresh de token
export interface RefreshResponse {
  success: boolean;
  message?: string;
  accessToken?: string;
  user?: AuthUser;
  expiresAt?: string;
  newExpiresAt?: string;
}

// Estado de autenticación
export interface AuthState {
  isAuthenticated: boolean;
  user?: AuthUser;
  token?: string;
  expiresAt?: Date;
}

// Pasos del wizard de login
export enum LoginStep {
  REQUEST_TOKEN = 'request-token',
  ENTER_TOKEN = 'enter-token'
}

// Estado del wizard de login
export interface LoginWizardState {
  currentStep: LoginStep;
  codeLogin?: string;
  user?: AuthUser;
  isLoading: boolean;
  error?: string;
}
