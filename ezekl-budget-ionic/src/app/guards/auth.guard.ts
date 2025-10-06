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
    // Esperar a que termine la inicialización del servicio
    return from(this.authService.ensureInitialized()).pipe(
      switchMap(() => {
        // Verificación después de inicialización
        const isAuthenticated = this.authService.isAuthenticated;
        const token = this.authService.currentToken;

        // Si no hay token, redirigir a login
        if (!token || !isAuthenticated) {
          console.log('AuthGuard: Sin autenticación, redirigiendo a login');
          this.router.navigate(['/login'], { replaceUrl: true });
          return of(false);
        }

        // Si hay token, permitir acceso
        console.log('AuthGuard: Usuario autenticado, permitiendo acceso');
        return of(true);
      }),
      catchError(error => {
        console.error('AuthGuard: Error en verificación:', error);
        this.router.navigate(['/login'], { replaceUrl: true });
        return of(false);
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
    // Esperar a que termine la inicialización del servicio
    return from(this.authService.ensureInitialized()).pipe(
      switchMap(() => {
        // Verificación después de inicialización
        const isAuth = this.authService.isAuthenticated;
        const token = this.authService.currentToken;

        if (isAuth && token) {
          // Usuario autenticado, redirigir a home
          console.log('GuestGuard: Usuario ya autenticado, redirigiendo a home');
          this.router.navigate(['/home'], { replaceUrl: true });
          return of(false);
        } else {
          // No autenticado, permitir acceso a login
          console.log('GuestGuard: Usuario no autenticado, permitiendo acceso a login');
          return of(true);
        }
      }),
      catchError(error => {
        console.error('GuestGuard: Error en verificación:', error);
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
   * Guard simplificado - siempre permite acceso sin verificación compleja
   */
  canActivate(): boolean {
    // Permitir siempre el acceso para evitar bloqueos
    return true;
  }
}
