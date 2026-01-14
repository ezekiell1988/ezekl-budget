import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../../service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    const isAuth = this.authService.isAuthenticated();
    console.log('🔐 AuthGuard - Verificando autenticación...');
    console.log('📍 Ruta solicitada:', state.url);
    console.log('✅ ¿Autenticado?:', isAuth);
    
    if (isAuth) {
      console.log('✅ Usuario autenticado - permitir acceso');
      // Usuario autenticado - permitir acceso
      return true;
    }

    // Usuario no autenticado - redirigir al login
    console.warn('❌ Usuario no autenticado, redirigiendo al login');
    console.warn('🔍 Token existe:', this.authService.getToken() ? 'SÍ' : 'NO');
    console.warn('👤 Usuario existe:', this.authService.getCurrentUser() ? 'SÍ' : 'NO');
    
    return this.router.createUrlTree(['/login'], {
      queryParams: { returnUrl: state.url }
    });
  }
}
