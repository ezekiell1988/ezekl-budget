import { Injectable, signal, computed, effect, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
import { LoggerService } from './logger.service';
import {
  RequestTokenRequest,
  RequestTokenResponse,
  LoginRequest,
  LoginResponse,
  LogoutResponse,
  RefreshTokenResponse,
  VerifyTokenResponse,
  UserData
} from '../shared/models';

/**
 * Servicio de autenticación modernizado con Angular 20+ Signals
 * 
 * Características:
 * - Signals para estado reactivo
 * - Computed signals para validaciones
 * - Effects para sincronización automática con localStorage
 * - 100% compatible con backend OpenAPI
 * - Tipado estricto
 * 
 * @example
 * ```typescript
 * // Inyectar servicio
 * private authService = inject(AuthService);
 * 
 * // Usar signals
 * isLoggedIn = this.authService.isAuthenticated;
 * currentUser = this.authService.currentUser;
 * 
 * // En template
 * @if (authService.isAuthenticated()) {
 *   <p>Bienvenido {{ authService.currentUser()?.nameLogin }}</p>
 * }
 * ```
 */
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // Servicios inyectados con inject() (Angular 20+)
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly logger = inject(LoggerService).getLogger('AuthService');
  
  // API base URL
  private readonly apiUrl = `${environment.apiUrl}auth/`;

  // ========================================
  // SIGNALS (Angular 20+)
  // ========================================
  
  /** Estado del usuario autenticado */
  readonly currentUser = signal<UserData | null>(this.getUserFromStorage());
  
  /** Token de autenticación JWE */
  readonly token = signal<string | null>(this.getTokenFromStorage());
  
  /** Fecha de expiración del token */
  readonly tokenExpiresAt = signal<string | null>(localStorage.getItem('tokenExpiresAt'));
  
  /** Computed: estado de autenticación */
  readonly isAuthenticated = computed(() => {
    const token = this.token();
    if (!token) return false;
    
    const expiresAt = this.tokenExpiresAt();
    if (!expiresAt) return true; // Sin fecha de expiración, asumir válido
    
    const expirationDate = new Date(expiresAt);
    const now = new Date();
    
    return now < expirationDate; // Token válido si aún no expiró
  });
  
  /** Computed: verificar si el token expira pronto (< 5 min) */
  readonly isTokenExpiringSoon = computed(() => {
    const expiresAt = this.tokenExpiresAt();
    if (!expiresAt) return false;
    
    const expirationDate = new Date(expiresAt);
    const now = new Date();
    const fiveMinutesFromNow = new Date(now.getTime() + 5 * 60 * 1000);
    
    return expirationDate <= fiveMinutesFromNow && expirationDate > now;
  });
  
  /** Computed: verificar si el token está expirado */
  readonly isTokenExpired = computed(() => {
    const expiresAt = this.tokenExpiresAt();
    if (!expiresAt) return false;
    
    const expirationDate = new Date(expiresAt);
    const now = new Date();
    
    return now >= expirationDate;
  });

  constructor() {
    // Effect para sincronizar cambios en el usuario con localStorage
    effect(() => {
      const user = this.currentUser();
      if (user) {
        localStorage.setItem('userData', JSON.stringify(user));
      } else {
        localStorage.removeItem('userData');
      }
    });
    
    // Effect para sincronizar cambios en el token con localStorage
    effect(() => {
      const tokenValue = this.token();
      if (tokenValue) {
        localStorage.setItem('token', tokenValue);
      } else {
        localStorage.removeItem('token');
      }
    });
  }

  // ========================================
  // AUTHENTICATION FLOW
  // ========================================
  
  /**
   * Paso 1: Solicitar token temporal (PIN de 5 dígitos)
   * POST /api/v1/auth/request-token
   * 
   * @param codeLogin Código de usuario
   * @returns Observable con respuesta de solicitud de token
   */
  requestLoginToken(codeLogin: string): Observable<RequestTokenResponse> {
    const url = `${this.apiUrl}request-token`;
    const body: RequestTokenRequest = { codeLogin };

    this.logger.debug('Solicitando token para:', codeLogin);

    return this.http.post<RequestTokenResponse>(url, body).pipe(
      tap(response => {
        this.logger.debug('Respuesta solicitud token:', response);
      })
    );
  }

  /**
   * Paso 2: Login con token temporal (PIN de 5 dígitos)
   * POST /api/v1/auth/login
   * 
   * @param codeLogin Código de usuario
   * @param token PIN de 5 dígitos
   * @returns Observable con respuesta de login
   */
  loginWithToken(codeLogin: string, token: string): Observable<LoginResponse> {
    const url = `${this.apiUrl}login`;
    const body: LoginRequest = { codeLogin, token };

    this.logger.debug('Iniciando sesión con token:', { codeLogin, token: '****' });

    return this.http.post<LoginResponse>(url, body).pipe(
      tap((response: LoginResponse) => {
        this.logger.debug('Respuesta login:', { ...response, accessToken: '****' });
        
        if (response.success && response.accessToken) {
          // Actualizar signals (automáticamente sincroniza con localStorage vía effects)
          this.token.set(response.accessToken);
          this.currentUser.set(response.user);
          this.tokenExpiresAt.set(response.expiresAt);
          
          // También guardar en localStorage por si acaso
          localStorage.setItem('tokenExpiresAt', response.expiresAt);
          
          this.logger.success('Sesión iniciada correctamente');
          this.logger.debug('Usuario:', response.user.nameLogin);
          this.logger.debug('Expira:', response.expiresAt);
        }
      })
    );
  }

  /**
   * Logout - cerrar sesión
   * POST /api/v1/auth/logout
   * Requiere autenticación: Bearer token
   * 
   * @param microsoftLogout Si se debe cerrar sesión en Microsoft también
   * @returns Observable con respuesta de logout
   */
  logout(microsoftLogout: boolean = false): Observable<LogoutResponse> {
    const url = `${this.apiUrl}logout?microsoft_logout=${microsoftLogout}`;
    const headers = this.getAuthHeaders();
    
    this.logger.debug('Cerrando sesión...');
    
    return this.http.post<LogoutResponse>(url, {}, { headers }).pipe(
      tap({
        next: (response) => {
          this.logger.success('Sesión cerrada en servidor');
          
          // Limpiar estado local
          this.clearAuth();
          
          // Redirigir a Microsoft si es necesario
          if (response.redirect_required && response.microsoft_logout_url) {
            window.location.href = response.microsoft_logout_url;
          } else {
            this.router.navigate(['/login']);
          }
        },
        error: (error) => {
          this.logger.error('Error al cerrar sesión en servidor:', error);
          // Aunque falle el backend, limpiar sesión local
          this.clearAuth();
          this.router.navigate(['/login']);
        }
      })
    );
  }

  /**
   * Limpia la sesión localmente (logout offline)
   */
  clearSession(): void {
    this.clearAuth();
    this.router.navigate(['/login']);
  }

  /**
   * Verificar token y obtener información del usuario
   * GET /api/v1/auth/verify-token.json
   * Requiere autenticación: Bearer token
   * 
   * @returns Observable con datos del usuario y fechas del token
   */
  verifyToken(): Observable<VerifyTokenResponse> {
    const url = `${this.apiUrl}verify-token.json`;
    const headers = this.getAuthHeaders();
    
    this.logger.debug('Verificando token...');
    
    return this.http.get<VerifyTokenResponse>(url, { headers }).pipe(
      tap((response: VerifyTokenResponse) => {
        this.logger.success('Token válido, usuario:', response.user.nameLogin);
        
        // Actualizar usuario y fechas
        this.currentUser.set(response.user);
        
        if (response.expiresAt) {
          this.tokenExpiresAt.set(response.expiresAt);
          localStorage.setItem('tokenExpiresAt', response.expiresAt);
        }
      })
    );
  }

  /**
   * Refrescar token de autenticación (extender expiración)
   * POST /api/v1/auth/refresh-token
   * Requiere autenticación: Bearer token
   * 
   * @returns Observable con nuevo token y fecha de expiración
   */
  refreshToken(): Observable<RefreshTokenResponse> {
    const url = `${this.apiUrl}refresh-token`;
    const headers = this.getAuthHeaders();
    
    this.logger.debug('Refrescando token...');
    
    return this.http.post<RefreshTokenResponse>(url, {}, { headers }).pipe(
      tap((response: RefreshTokenResponse) => {
        this.logger.success('Token refrescado exitosamente');
        
        if (response?.success && response?.accessToken) {
          // Actualizar signals
          this.token.set(response.accessToken);
          this.tokenExpiresAt.set(response.expiresAt);
          
          // Guardar fecha de expiración
          localStorage.setItem('tokenExpiresAt', response.expiresAt);
          
          this.logger.debug('Nueva expiración:', response.expiresAt);
        }
      })
    );
  }

  // ========================================
  // MÉTODOS PÚBLICOS
  // ========================================
  
  /**
   * Obtener el token actual
   * @returns Token JWT o null
   */
  getToken(): string | null {
    return this.token();
  }

  /**
   * Obtener el usuario actual
   * @returns Datos del usuario o null
   */
  getCurrentUser(): UserData | null {
    return this.currentUser();
  }

  /**
   * Obtener headers con autenticación
   * @returns HttpHeaders con Authorization Bearer
   */
  getAuthHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  // ========================================
  // MÉTODOS PRIVADOS
  // ========================================
  
  /**
   * Leer token desde localStorage al inicializar
   */
  private getTokenFromStorage(): string | null {
    try {
      return localStorage.getItem('token');
    } catch (error) {
      this.logger.error('Error leyendo token de localStorage:', error);
      return null;
    }
  }

  /**
   * Leer usuario desde localStorage al inicializar
   */
  private getUserFromStorage(): UserData | null {
    try {
      const userData = localStorage.getItem('userData');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      this.logger.error('Error leyendo usuario de localStorage:', error);
      return null;
    }
  }

  /**
   * Limpiar toda la autenticación
   */
  private clearAuth(): void {
    this.logger.debug('Limpiando autenticación...');
    
    // Limpiar signals
    this.token.set(null);
    this.currentUser.set(null);
    this.tokenExpiresAt.set(null);
    
    // Limpiar localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('userData');
    localStorage.removeItem('tokenExpiresAt');
    
    this.logger.debug('Autenticación limpiada');
  }
}
