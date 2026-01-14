import { HttpInterceptorFn, HttpErrorResponse, HttpRequest, HttpEvent } from '@angular/common/http';
import { inject } from '@angular/core';
import { throwError, BehaviorSubject, Observable } from 'rxjs';
import { catchError, filter, take, switchMap } from 'rxjs/operators';
import { AuthService } from '../../service/auth.service';

let isRefreshing = false;
const refreshTokenSubject = new BehaviorSubject<string | null>(null);

/**
 * Interceptor funcional de autenticación (Angular 17+)
 * - Agrega automáticamente el token Bearer a las solicitudes
 * - Maneja errores 401 refrescando el token automáticamente
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);

  // No agregar token a rutas públicas
  if (isPublicRoute(req.url)) {
    return next(req);
  }

  // Agregar token a la solicitud
  const token = authService.getToken();
  if (token) {
    req = addToken(req, token);
  }

  return next(req).pipe(
    catchError((error) => {
      if (error instanceof HttpErrorResponse && error.status === 401) {
        // Token inválido o expirado
        return handle401Error(req, next, authService);
      }
      
      return throwError(() => error);
    })
  );
};

/**
 * Agregar token al header Authorization
 */
function addToken(request: HttpRequest<unknown>, token: string): HttpRequest<unknown> {
  return request.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`
    }
  });
}

/**
 * Verificar si la ruta es pública (no requiere autenticación)
 */
function isPublicRoute(url: string): boolean {
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
function handle401Error(
  request: HttpRequest<unknown>, 
  next: (req: HttpRequest<unknown>) => Observable<HttpEvent<unknown>>, 
  authService: AuthService
): Observable<HttpEvent<unknown>> {
  if (!isRefreshing) {
    isRefreshing = true;
    refreshTokenSubject.next(null);

    return authService.refreshToken().pipe(
      switchMap((response: any) => {
        isRefreshing = false;
        refreshTokenSubject.next(response.token);
        
        // Reintentar la solicitud original con el nuevo token
        return next(addToken(request, response.token));
      }),
      catchError((err) => {
        isRefreshing = false;
        
        // Si falla el refresh, cerrar sesión
        authService.clearSession();
        
        return throwError(() => err);
      })
    );
  } else {
    // Si ya se está refrescando, esperar a que termine
    return refreshTokenSubject.pipe(
      filter((token): token is string => token != null),
      take(1),
      switchMap(token => {
        return next(addToken(request, token));
      })
    );
  }
}
