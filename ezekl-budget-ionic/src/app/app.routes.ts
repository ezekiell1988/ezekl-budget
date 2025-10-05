import { Routes } from '@angular/router';
import { AuthGuard, GuestGuard, AuthCheckGuard } from './guards/auth.guard';

export const routes: Routes = [
  // Ruta raíz - redirige a home directamente
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },

  // Ruta de login - solo accesible si NO está autenticado
  {
    path: 'login',
    loadComponent: () => import('./login/login.page').then(m => m.LoginPage),
    canActivate: [GuestGuard]
  },

  // Ruta home - protegida, requiere autenticación
  {
    path: 'home',
    loadComponent: () => import('./home/home.page').then(m => m.HomePage),
    canActivate: [AuthGuard]
  },

  // Ruta demo-websocket - protegida, requiere autenticación
  {
    path: 'demo-websocket',
    loadComponent: () => import('./demo-websocket/demo-websocket.page').then( m => m.DemoWebsocketPage),
    canActivate: [AuthGuard]
  },

  // Ruta wildcard - redirige a home (que a su vez verificará autenticación)
  // IMPORTANTE: Esta debe ir SIEMPRE al final
  {
    path: '**',
    redirectTo: 'home'
  }
];
