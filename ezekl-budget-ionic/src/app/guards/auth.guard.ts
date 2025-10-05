/**
 * Guard de autenticación para proteger rutas
 * Redirige a login si no está autenticado o a home si ya está autenticado
 */

import { Injectable, inject } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';

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
    return this.authService.authState.pipe(
      take(1),
      map(state => {
        if (state.isAuthenticated && this.authService.isAuthenticated) {
          return true;
        } else {
          console.log('🔒 Acceso denegado: Usuario no autenticado');
          this.router.navigate(['/login']);
          return false;
        }
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
    return this.authService.authState.pipe(
      take(1),
      map(state => {
        if (!state.isAuthenticated || !this.authService.isAuthenticated) {
          return true;
        } else {
          console.log('🏠 Redirigiendo a home: Usuario ya autenticado');
          this.router.navigate(['/home']);
          return false;
        }
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
