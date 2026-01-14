import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
import {
  LoginTokenRequest,
  LoginTokenResponse,
  LoginRequest,
  LoginResponse,
  LogoutResponse,
  RefreshTokenResponse,
  UserInfoResponse,
  UserData
} from '../shared/models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  
  // Flag para debug (activar solo cuando se necesite investigar problemas de auth)
  private readonly DEBUG_AUTH = false;

  // BehaviorSubject para mantener el estado de autenticación
  private currentUserSubject = new BehaviorSubject<UserData | null>(this.getUserFromStorage());
  public currentUser$ = this.currentUserSubject.asObservable();

  private tokenSubject = new BehaviorSubject<string | null>(this.getTokenFromStorage());
  public token$ = this.tokenSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  /**
   * Paso 1: Solicitar token de 5 dígitos
   * POST /{merchant_id}/v1/auth/login-token
   */
  requestLoginToken(codeLogin: string): Observable<LoginTokenResponse> {
    const url = `${this.apiUrl}auth/login-token`;
    const body: LoginTokenRequest = { codeLogin };

    return this.http.post<LoginTokenResponse>(url, body);
  }

  /**
   * Paso 2: Login con token de 5 dígitos
   * POST /{merchant_id}/v1/auth/login
   */
  loginWithToken(idLogin: number, token: string): Observable<LoginResponse> {
    const url = `${this.apiUrl}auth/login`;
    const body: LoginRequest = { idLogin, token };

    return this.http.post<LoginResponse>(url, body).pipe(
      tap((response: LoginResponse) => {
        if (response.success) {
          // Guardar token y usuario en localStorage
          this.saveToken(response.token);
          this.saveUser(response.user);

          // Guardar fecha de expiración
          if (response.expiresAt) {
            localStorage.setItem('tokenExpiresAt', response.expiresAt);
          }

          // Actualizar BehaviorSubjects
          this.tokenSubject.next(response.token);
          this.currentUserSubject.next(response.user);
        }
      })
    );
  }

  /**
   * Logout - elimina token y usuario
   * POST /{merchant_id}/v1/auth/logout
   */
  logout(): Observable<LogoutResponse> {
    const url = `${this.apiUrl}auth/logout`;
    const headers = this.getAuthHeaders();
    
    return this.http.post<LogoutResponse>(url, {}, { headers }).pipe(
      tap({
        next: () => {
          this.clearAuth();
          this.router.navigate(['/login']);
        },
        error: () => {
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
   * Obtener información del usuario autenticado
   * GET /{merchant_id}/v1/auth/me
   */
  getUserInfo(): Observable<UserInfoResponse> {
    const url = `${this.apiUrl}auth/me`;
    const headers = this.getAuthHeaders();
    
    return this.http.get<UserInfoResponse>(url, { headers }).pipe(
      tap((response: UserInfoResponse) => {
        if (response?.success && response?.user) {
          // Actualizar usuario en localStorage y BehaviorSubject
          this.saveUser(response.user);
          this.currentUserSubject.next(response.user);
        }
      })
    );
  }

  /**
   * Refrescar token de autenticación
   * POST /{merchant_id}/v1/auth/refresh
   */
  refreshToken(): Observable<RefreshTokenResponse> {
    const url = `${this.apiUrl}auth/refresh`;
    const headers = this.getAuthHeaders();
    
    return this.http.post<RefreshTokenResponse>(url, {}, { headers }).pipe(
      tap((response: RefreshTokenResponse) => {
        if (response?.success && response?.token) {
          // Actualizar token en localStorage y BehaviorSubject
          this.saveToken(response.token);
          this.tokenSubject.next(response.token);

          // Guardar fecha de expiración si viene
          if (response.expiresAt) {
            localStorage.setItem('tokenExpiresAt', response.expiresAt);
          }
        }
      })
    );
  }

  /**
   * Verificar si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    const token = this.getTokenFromStorage();
    if (!token) {
      if (this.DEBUG_AUTH) console.log('❌ isAuthenticated: No hay token');
      return false;
    }
    
    // Verificar si el token está expirado
    if (this.isTokenExpired()) {
      if (this.DEBUG_AUTH) console.warn('⏰ Token expirado detectado en isAuthenticated');
      return false;
    }
    
    if (this.DEBUG_AUTH) console.log('✅ isAuthenticated: Token válido');
    return true;
  }

  /**
   * Verificar si el token está expirado
   */
  isTokenExpired(): boolean {
    const expiresAt = localStorage.getItem('tokenExpiresAt');
    if (!expiresAt) {
      return false; // Si no hay fecha de expiración, asumir que es válido
    }
    
    const expirationDate = new Date(expiresAt);
    const now = new Date();
    
    return now >= expirationDate;
  }

  /**
   * Verificar si el token está próximo a expirar (menos de 5 minutos)
   */
  isTokenExpiringSoon(): boolean {
    const expiresAt = localStorage.getItem('tokenExpiresAt');
    if (!expiresAt) {
      return false;
    }
    
    const expirationDate = new Date(expiresAt);
    const now = new Date();
    const fiveMinutesFromNow = new Date(now.getTime() + 5 * 60 * 1000);
    
    return expirationDate <= fiveMinutesFromNow;
  }

  /**
   * Obtener el token actual
   */
  getToken(): string | null {
    return this.getTokenFromStorage();
  }

  /**
   * Obtener el usuario actual
   */
  getCurrentUser(): UserData | null {
    return this.getUserFromStorage();
  }

  /**
   * Obtener headers con autenticación
   */
  getAuthHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  // --- Métodos privados para manejo de localStorage ---

  private saveToken(token: string): void {
    if (this.DEBUG_AUTH) console.log('💾 Guardando token en localStorage');
    localStorage.setItem('token', token);
    // Verificar que se guardó
    if (this.DEBUG_AUTH) {
      const saved = localStorage.getItem('token');
      console.log('✅ Token guardado:', saved ? 'SÍ' : 'NO');
    }
  }

  private saveUser(user: UserData): void {
    if (this.DEBUG_AUTH) console.log('💾 Guardando usuario en localStorage');
    localStorage.setItem('userData', JSON.stringify(user));
    // Verificar que se guardó
    if (this.DEBUG_AUTH) {
      const saved = localStorage.getItem('userData');
      console.log('✅ Usuario guardado:', saved ? 'SÍ' : 'NO');
    }
  }

  private getTokenFromStorage(): string | null {
    const token = localStorage.getItem('token');
    if (this.DEBUG_AUTH) console.log('🔍 Leyendo token de localStorage:', token ? 'EXISTE' : 'NO EXISTE');
    return token;
  }

  private getUserFromStorage(): UserData | null {
    const userData = localStorage.getItem('userData');
    if (this.DEBUG_AUTH) console.log('🔍 Leyendo usuario de localStorage:', userData ? 'EXISTE' : 'NO EXISTE');
    return userData ? JSON.parse(userData) : null;
  }

  private clearAuth(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('userData');
    localStorage.removeItem('tokenExpiresAt');
    this.tokenSubject.next(null);
    this.currentUserSubject.next(null);
  }
}
