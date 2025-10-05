/**
 * Servicio de autenticación para Ezekl Budget
 * Maneja el flujo de login de 2 pasos, tokens JWE y estado de sesión
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError, from } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { Preferences } from '@capacitor/preferences';
import {
  AuthUser,
  AuthState,
  RequestTokenRequest,
  RequestTokenResponse,
  LoginRequest,
  LoginResponse,
  LoginStep,
  LoginWizardState
} from '../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_BASE = '/api/auth';
  private readonly TOKEN_KEY = 'ezekl_auth_token';
  private readonly USER_KEY = 'ezekl_auth_user';

  // Estado de autenticación reactivo
  private authState$ = new BehaviorSubject<AuthState>({
    isAuthenticated: false,
    user: undefined,
    token: undefined,
    expiresAt: undefined
  });

  // Estado del wizard de login
  private wizardState$ = new BehaviorSubject<LoginWizardState>({
    currentStep: LoginStep.REQUEST_TOKEN,
    isLoading: false,
    error: undefined
  });

  constructor(private http: HttpClient) {
    // Cargar estado de autenticación al inicializar
    this.loadAuthState();
  }

  /**
   * Observable del estado de autenticación
   */
  get authState(): Observable<AuthState> {
    return this.authState$.asObservable();
  }

  /**
   * Observable del estado del wizard
   */
  get wizardState(): Observable<LoginWizardState> {
    return this.wizardState$.asObservable();
  }

  /**
   * Verificar si el usuario está autenticado
   */
  get isAuthenticated(): boolean {
    const state = this.authState$.value;
    if (!state.isAuthenticated || !state.token || !state.expiresAt) {
      return false;
    }

    // Verificar si el token no ha expirado
    const now = new Date();
    return state.expiresAt > now;
  }

  /**
   * Obtener el usuario actual
   */
  get currentUser(): AuthUser | undefined {
    return this.authState$.value.user;
  }

  /**
   * Obtener el token actual
   */
  get currentToken(): string | undefined {
    return this.authState$.value.token;
  }

  /**
   * PASO 1: Solicitar token temporal
   */
  async requestToken(codeLogin: string): Promise<RequestTokenResponse> {
    this.updateWizardState({
      isLoading: true,
      error: undefined,
      codeLogin: codeLogin
    });

    try {
      const response = await this.http.post<RequestTokenResponse>(
        `${this.API_BASE}/request-token`,
        { codeLogin }
      ).toPromise();

      if (response?.success) {
        // Avanzar al siguiente paso del wizard
        this.updateWizardState({
          currentStep: LoginStep.ENTER_TOKEN,
          user: response.user as AuthUser,
          isLoading: false,
          error: undefined
        });
      } else {
        this.updateWizardState({
          isLoading: false,
          error: response?.message || 'Error solicitando token'
        });
      }

      return response!;

    } catch (error) {
      const errorMsg = this.getErrorMessage(error);
      this.updateWizardState({
        isLoading: false,
        error: errorMsg
      });
      throw new Error(errorMsg);
    }
  }

  /**
   * PASO 2: Login con token
   */
  async login(codeLogin: string, token: string): Promise<LoginResponse> {
    this.updateWizardState({
      isLoading: true,
      error: undefined
    });

    try {
      const response = await this.http.post<LoginResponse>(
        `${this.API_BASE}/login`,
        { codeLogin, token }
      ).toPromise();

      if (response?.success && response.accessToken) {
        // Guardar datos de autenticación
        await this.saveAuthData(
          response.accessToken,
          response.user as AuthUser,
          response.expiresAt!
        );

        // Limpiar wizard
        this.resetWizard();

        // Actualizar estado de autenticación
        this.updateAuthState({
          isAuthenticated: true,
          user: response.user as AuthUser,
          token: response.accessToken,
          expiresAt: new Date(response.expiresAt!)
        });
      } else {
        this.updateWizardState({
          isLoading: false,
          error: response?.message || 'Error de autenticación'
        });
      }

      return response!;

    } catch (error) {
      const errorMsg = this.getErrorMessage(error);
      this.updateWizardState({
        isLoading: false,
        error: errorMsg
      });
      throw new Error(errorMsg);
    }
  }

  /**
   * Reenviar token
   */
  async resendToken(): Promise<void> {
    const currentState = this.wizardState$.value;
    if (!currentState.codeLogin) {
      throw new Error('No hay código de login para reenviar');
    }

    await this.requestToken(currentState.codeLogin);
  }

  /**
   * Volver al paso anterior del wizard
   */
  goBackInWizard(): void {
    const currentState = this.wizardState$.value;

    if (currentState.currentStep === LoginStep.ENTER_TOKEN) {
      this.updateWizardState({
        currentStep: LoginStep.REQUEST_TOKEN,
        user: undefined,
        error: undefined
      });
    }
  }

  /**
   * Resetear wizard al estado inicial
   */
  resetWizard(): void {
    this.wizardState$.next({
      currentStep: LoginStep.REQUEST_TOKEN,
      isLoading: false,
      error: undefined,
      codeLogin: undefined,
      user: undefined
    });
  }

  /**
   * Verificar token de sesión
   */
  async verifyToken(): Promise<boolean> {
    const token = this.currentToken;
    if (!token) {
      await this.logout();
      return false;
    }

    try {
      const response = await this.http.post<any>(
        `${this.API_BASE}/verify-token`,
        { token }
      ).toPromise();

      if (response?.valid) {
        // Actualizar datos del usuario si es necesario
        if (response.user) {
          this.updateAuthState({
            ...this.authState$.value,
            user: response.user,
            expiresAt: response.expiresAt ? new Date(response.expiresAt) : undefined
          });
        }
        return true;
      } else {
        await this.logout();
        return false;
      }
    } catch (error) {
      console.error('Error verificando token:', error);
      await this.logout();
      return false;
    }
  }

  /**
   * Cerrar sesión
   */
  async logout(): Promise<void> {
    try {
      // Llamar al endpoint de logout (opcional con JWE)
      await this.http.post(`${this.API_BASE}/logout`, {}).toPromise();
    } catch (error) {
      console.error('Error en logout del servidor:', error);
      // Continuar con logout local aunque falle el servidor
    }

    // Limpiar datos locales
    await this.clearAuthData();

    // Actualizar estado
    this.updateAuthState({
      isAuthenticated: false,
      user: undefined,
      token: undefined,
      expiresAt: undefined
    });

    // Resetear wizard
    this.resetWizard();
  }

  /**
   * Auto-copiar token desde el portapapeles
   */
  async tryAutoCopyToken(): Promise<string | null> {
    try {
      // En dispositivos móviles, intentar leer del portapapeles
      if ('navigator' in window && 'clipboard' in navigator) {
        const text = await navigator.clipboard.readText();

        // Verificar si el texto parece un token de 5 dígitos
        const tokenRegex = /^\d{5}$/;
        if (tokenRegex.test(text.trim())) {
          return text.trim();
        }

        // También buscar patrones como "Tu código es: 12345"
        const codeMatch = text.match(/(?:código|token|code).*?(\d{5})/i);
        if (codeMatch) {
          return codeMatch[1];
        }
      }
    } catch (error) {
      console.log('No se pudo acceder al portapapeles:', error);
    }

    return null;
  }

  // ==============================
  // Métodos privados
  // ==============================

  private async loadAuthState(): Promise<void> {
    try {
      const [tokenResult, userResult] = await Promise.all([
        Preferences.get({ key: this.TOKEN_KEY }),
        Preferences.get({ key: this.USER_KEY })
      ]);

      if (tokenResult.value && userResult.value) {
        const token = tokenResult.value;
        const user = JSON.parse(userResult.value) as AuthUser;

        // Verificar token con el servidor
        const isValid = await this.verifyToken();

        if (isValid) {
          this.updateAuthState({
            isAuthenticated: true,
            user,
            token,
            expiresAt: undefined // Se actualiza en verifyToken
          });
        }
      }
    } catch (error) {
      console.error('Error cargando estado de autenticación:', error);
      await this.clearAuthData();
    }
  }

  private async saveAuthData(token: string, user: AuthUser, expiresAt: string): Promise<void> {
    await Promise.all([
      Preferences.set({ key: this.TOKEN_KEY, value: token }),
      Preferences.set({ key: this.USER_KEY, value: JSON.stringify(user) })
    ]);
  }

  private async clearAuthData(): Promise<void> {
    await Promise.all([
      Preferences.remove({ key: this.TOKEN_KEY }),
      Preferences.remove({ key: this.USER_KEY })
    ]);
  }

  private updateAuthState(newState: Partial<AuthState>): void {
    const currentState = this.authState$.value;
    this.authState$.next({ ...currentState, ...newState });
  }

  private updateWizardState(newState: Partial<LoginWizardState>): void {
    const currentState = this.wizardState$.value;
    this.wizardState$.next({ ...currentState, ...newState });
  }

  private getErrorMessage(error: any): string {
    if (error instanceof HttpErrorResponse) {
      if (error.error?.detail) {
        return error.error.detail;
      }
      if (error.error?.message) {
        return error.error.message;
      }
      return `Error ${error.status}: ${error.message}`;
    }

    if (error?.message) {
      return error.message;
    }

    return 'Error desconocido';
  }
}
