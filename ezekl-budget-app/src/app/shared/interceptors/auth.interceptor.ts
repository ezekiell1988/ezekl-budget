import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, filter, take, switchMap } from 'rxjs/operators';
import { AuthService } from '../../service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);

  constructor(private authService: AuthService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // No agregar token a rutas públicas
    if (this.isPublicRoute(request.url)) {
      return next.handle(request);
    }

    // Agregar token a la solicitud
    const token = this.authService.getToken();
    if (token) {
      request = this.addToken(request, token);
    }

    return next.handle(request).pipe(
      catchError((error) => {
        if (error instanceof HttpErrorResponse && error.status === 401) {
          // Token inválido o expirado
          return this.handle401Error(request, next);
        }
        
        return throwError(() => error);
      })
    );
  }

  /**
   * Agregar token al header Authorization
   */
  private addToken(request: HttpRequest<any>, token: string): HttpRequest<any> {
    return request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  /**
   * Verificar si la ruta es pública (no requiere autenticación)
   */
  private isPublicRoute(url: string): boolean {
    const publicRoutes = [
      '/auth/login-token',
      '/auth/login',
      'config.json'
    ];
    
    return publicRoutes.some(route => url.includes(route));
  }

  /**
   * Manejar error 401 - intentar refrescar token
   */
  private handle401Error(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);

      return this.authService.refreshToken().pipe(
        switchMap((response: any) => {
          this.isRefreshing = false;
          this.refreshTokenSubject.next(response.token);
          
          // Reintentar la solicitud original con el nuevo token
          return next.handle(this.addToken(request, response.token));
        }),
        catchError((err) => {
          this.isRefreshing = false;
          
          // Si falla el refresh, cerrar sesión
          this.authService.clearSession();
          
          return throwError(() => err);
        })
      );
    } else {
      // Si ya se está refrescando, esperar a que termine
      return this.refreshTokenSubject.pipe(
        filter(token => token != null),
        take(1),
        switchMap(token => {
          return next.handle(this.addToken(request, token));
        })
      );
    }
  }
}
