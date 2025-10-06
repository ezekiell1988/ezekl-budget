import { Routes } from '@angular/router';
import { AuthGuard, GuestGuard, AuthCheckGuard } from './guards/auth.guard';

export const routes: Routes = [
  // Ruta raíz - redirige a login por defecto para evitar bucles
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },

  // Ruta de login - sin guards para evitar problemas de inicialización
  {
    path: 'login',
    loadComponent: () => import('./login/login.page').then(m => m.LoginPage)
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

  // Ruta accounting-accounts - protegida, requiere autenticación
  {
    path: 'accounting-accounts',
    loadComponent: () => import('./accounting-accounts/accounting-accounts.page').then( m => m.AccountingAccountsPage),
    canActivate: [AuthGuard]
  },

  // Ruta wildcard - redirige a login para evitar bucles
  {
    path: '**',
    redirectTo: 'login'
  }
];
