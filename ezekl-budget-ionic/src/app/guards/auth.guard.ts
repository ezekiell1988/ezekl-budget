/**
 * Guard de autenticación para proteger rutas
 * Redirige a login si no está autenticado o a home si ya está autenticado
 */

import { Injectable, inject } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { Observable, from, of } from 'rxjs';
import { map, take, switchMap, catchError } from 'rxjs/operators';

import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  private authService = inject(AuthService);
  private router = inject(Router);

  /**
   * Guard para rutas protegidas (requiere autenticación)
   * Redirige a /login si no está autenticado
   */
  canActivate(): Observable<boolean> {
    // Esperar la inicialización
    return from(this.authService.ensureInitialized()).pipe(
      take(1),
      switchMap(() => {
        // Verificar estado local primero (más rápido para navegación interna)
        const isAuthenticated = this.authService.isAuthenticated;
        const token = this.authService.currentToken;

        // Si no hay token inicial, ir a login directamente
        if (!token || !isAuthenticated) {
          this.router.navigate(['/login']);
          return of(false);
        }

        // Si ya está autenticado localmente, permitir navegación
        // Solo verificar con el servidor si es realmente necesario
        const currentState = this.authService.authState;
        return currentState.pipe(
          take(1),
          map(state => {
            if (state.isAuthenticated && state.token) {
              return true;
            } else {
              this.router.navigate(['/login']);
              return false;
            }
          }),
          catchError(() => {
            // En caso de error, redirigir a login
            this.router.navigate(['/login']);
            return of(false);
          })
        );
      })
    );
  }
}

@Injectable({
  providedIn: 'root'
})
export class GuestGuard implements CanActivate {
  private authService = inject(AuthService);
  private router = inject(Router);

  /**
   * Guard para rutas de invitado (solo accesibles si NO está autenticado)
   * Redirige a /home si ya está autenticado
   */
  canActivate(): Observable<boolean> {
    // Esperar la inicialización
    return from(this.authService.ensureInitialized()).pipe(
      take(1),
      switchMap(() => {
        // Verificar el estado local primero (más rápido)
        const isAuth = this.authService.isAuthenticated;
        const token = this.authService.currentToken;

        if (isAuth && token) {
          // Usuario autenticado, redirigir a home
          this.router.navigate(['/home']);
          return of(false);
        } else {
          // No autenticado, permitir acceso a login
          return of(true);
        }
      }),
      catchError(() => {
        // En caso de error, permitir acceso a login
        return of(true);
      })
    );
  }
}

@Injectable({
  providedIn: 'root'
})
export class AuthCheckGuard implements CanActivate {
  private authService = inject(AuthService);

  /**
   * Guard para verificar autenticación al inicializar la app
   * Verifica el token almacenado y actualiza el estado
   */
  async canActivate(): Promise<boolean> {
    try {
      // Verificar si hay un token válido almacenado
      await this.authService.verifyToken();
      return true;
    } catch (error) {
      console.error('Error verificando token en AuthCheckGuard:', error);
      return true; // Permitir continuar aunque falle la verificación
    }
  }
}
