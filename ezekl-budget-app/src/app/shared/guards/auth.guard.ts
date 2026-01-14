import { Injectable, inject } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService, LoggerService } from '../../service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  private readonly logger = inject(LoggerService).getLogger('AuthGuard');
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    const isAuth = this.authService.isAuthenticated();
    this.logger.debug('Verificando autenticación...');
    this.logger.debug('Ruta solicitada:', state.url);
    this.logger.debug('¿Autenticado?:', isAuth);
    
    if (isAuth) {
      this.logger.debug('Usuario autenticado - permitir acceso');
      // Usuario autenticado - permitir acceso
      return true;
    }

    // Usuario no autenticado - redirigir al login
    this.logger.warn('Usuario no autenticado, redirigiendo al login');
    this.logger.debug('Token existe:', this.authService.getToken() ? 'SÍ' : 'NO');
    this.logger.debug('Usuario existe:', this.authService.getCurrentUser() ? 'SÍ' : 'NO');
    
    return this.router.createUrlTree(['/login'], {
      queryParams: { returnUrl: state.url }
    });
  }
}
