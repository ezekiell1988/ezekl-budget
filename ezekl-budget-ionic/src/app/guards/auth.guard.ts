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
    // Esperar la inicialización y verificar con el servidor
    return from(this.authService.ensureInitialized()).pipe(
      take(1),
      switchMap(() => {
        const token = this.authService.currentToken;
        // Si no hay token inicial, ir a login directamente
        if (!token) {
          this.router.navigate(['/login']);
          return of(false);
        }

        // Verificar token con el servidor
        return from(this.authService.verifyToken()).pipe(
          map(isValid => {
            if (isValid) {
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
      map(() => {
        const isAuth = this.authService.isAuthenticated;
        // Verificar el estado local primero (más rápido)
        if (isAuth) {
          // Usuario autenticado, redirigir a home
          this.router.navigate(['/home']);
          return false;
        } else {
          // No autenticado, permitir acceso a login
          return true;
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
