/**
 * Servicio de autenticación para Ezekl Budget
 * Maneja el flujo de login de 2 pasos, tokens JWE y estado de sesión
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError, from, firstValueFrom } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { Preferences } from '@capacitor/preferences';
import {
  AuthUser,
  AuthState,
  RequestTokenRequest,
  RequestTokenResponse,
  LoginRequest,
  LoginResponse,
  RefreshResponse,
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

  // Promesa de inicialización
  private initPromise: Promise<void>;

  constructor(private http: HttpClient) {
    // Cargar estado de autenticación al inicializar
    this.initPromise = this.loadAuthState();
  }

  /**
   * Esperar a que termine la inicialización
   */
  async ensureInitialized(): Promise<void> {
    await this.initPromise;
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
    if (!state.isAuthenticated || !state.token) {
      return false;
    }

    // Si hay expiresAt, verificar que no haya expirado
    if (state.expiresAt) {
      const now = new Date();
      return state.expiresAt > now;
    }

    // Si no hay expiresAt, confiar en el flag isAuthenticated
    return true;
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
      const response = await firstValueFrom(
        this.http.post<RequestTokenResponse>(
          `${this.API_BASE}/request-token`,
          { codeLogin }
        )
      );

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
      const response = await firstValueFrom(
        this.http.post<LoginResponse>(
          `${this.API_BASE}/login`,
          { codeLogin, token }
        )
      );

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
      const response = await firstValueFrom(
        this.http.get<any>(
          `${this.API_BASE}/verify-token`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        )
      );

      if (response?.user) {
        // Actualizar estado como autenticado
        this.updateAuthState({
          ...this.authState$.value,
          isAuthenticated: true,
          user: response.user,
          expiresAt: response.expiresAt ? new Date(response.expiresAt) : undefined
        });
        return true;
      } else {
        await this.clearAuthData();
        return false;
      }
    } catch (error) {
      console.error('Error verificando token:', error);
      await this.logout();
      return false;
    }
  }

  /**
   * Verificar si el token necesita renovación (dentro de 1 hora de expirar)
   */
  shouldRefreshToken(): boolean {
    const state = this.authState$.value;
    if (!state.isAuthenticated || !state.expiresAt) {
      return false;
    }

    const now = new Date();
    const oneHourFromNow = new Date(now.getTime() + (60 * 60 * 1000)); // +1 hora

    // Renovar si expira dentro de 1 hora
    return state.expiresAt <= oneHourFromNow;
  }

  /**
   * Extender tiempo de expiración del token actual
   */
  async refreshToken(): Promise<boolean> {
    const token = this.currentToken;
    if (!token) {
      await this.logout();
      return false;
    }

    try {
      const response = await firstValueFrom(
        this.http.post<RefreshResponse>(
          `${this.API_BASE}/refresh-token`,
          {},
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        )
      );

      if (response?.success && response.accessToken) {
        // Guardar nuevo token
        await this.saveAuthData(
          response.accessToken,
          response.user as AuthUser,
          response.expiresAt!
        );

        // Actualizar estado con nuevo token
        this.updateAuthState({
          isAuthenticated: true,
          user: response.user as AuthUser,
          token: response.accessToken,
          expiresAt: new Date(response.expiresAt!)
        });

        return true;
      } else {
        await this.logout();
        return false;
      }
    } catch (error) {
      console.error('Error extendiendo token:', error);
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
      await firstValueFrom(
        this.http.post(`${this.API_BASE}/logout`, {})
      );
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
      // Error accessing clipboard
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

        // Verificar token con el servidor SIN cambiar el estado intermedio
        try {
          const response = await firstValueFrom(
            this.http.get<any>(
              `${this.API_BASE}/verify-token`,
              {
                headers: {
                  'Authorization': `Bearer ${token}`
                }
              }
            )
          );

          if (response?.user) {
            // Token válido - actualizar estado como autenticado
            this.updateAuthState({
              isAuthenticated: true,
              user: response.user,
              token: token,
              expiresAt: response.expiresAt ? new Date(response.expiresAt) : undefined
            });
            console.log('AuthService: Sesión restaurada exitosamente');
          } else {
            // Token inválido - limpiar datos
            await this.clearAuthData();
            this.updateAuthState({
              isAuthenticated: false,
              user: undefined,
              token: undefined,
              expiresAt: undefined
            });
            console.log('AuthService: Token inválido, limpiando sesión');
          }
        } catch (error) {
          console.error('AuthService: Error verificando token:', error);
          await this.clearAuthData();
          this.updateAuthState({
            isAuthenticated: false,
            user: undefined,
            token: undefined,
            expiresAt: undefined
          });
        }
      } else {
        // No hay datos guardados
        this.updateAuthState({
          isAuthenticated: false,
          user: undefined,
          token: undefined,
          expiresAt: undefined
        });
        console.log('AuthService: No hay sesión guardada');
      }
    } catch (error) {
      console.error('Error cargando estado de autenticación:', error);
      await this.clearAuthData();
      this.updateAuthState({
        isAuthenticated: false,
        user: undefined,
        token: undefined,
        expiresAt: undefined
      });
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
