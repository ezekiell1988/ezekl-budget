/**
 * Interceptor HTTP para autenticación automática
 * Agrega el token JWT a todas las requests HTTP automáticamente
 */

import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Si la request no es a la API, no hacer nada
    if (!req.url.includes('/api/')) {
      return next.handle(req);
    }

    // Endpoints que NO requieren autenticación
    const publicEndpoints = [
      '/api/auth/request-token',
      '/api/auth/login',
      '/api/health',
      '/api/credentials'
    ];

    // Si es un endpoint público, no agregar token
    if (publicEndpoints.some(endpoint => req.url.includes(endpoint))) {
      return next.handle(req);
    }

    // Para endpoints protegidos, intentar agregar token si está disponible
    const token = this.authService.currentToken;

    let authReq = req;
    if (token) {
      // Clonar request y agregar Authorization header
      authReq = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`)
      });
    }

    return next.handle(authReq).pipe(
      catchError((error: HttpErrorResponse) => {
        // Si el token expiró o es inválido (401), hacer logout y redirigir
        if (error.status === 401) {
          console.warn('Error de autenticación (401), redirigiendo a login');
          this.authService.logout().then(() => {
            this.redirectToLogin();
          });
        }

        return throwError(() => error);
      })
    );
  }

  private redirectToLogin(): void {
    // Solo redirigir si no estamos ya en login
    if (!this.router.url.includes('/login')) {
      this.router.navigate(['/login'], { replaceUrl: true });
    }
  }
}
