import { Routes } from '@angular/router';
import { AuthGuard, GuestGuard, AuthCheckGuard } from './guards/auth.guard';

export const routes: Routes = [
  // Ruta raíz - redirige inteligentemente según autenticación
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },

  // Ruta de login - protegida por GuestGuard para redirigir si ya está autenticado
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

  // Ruta demo-realtime - chat en tiempo real con Azure OpenAI
  {
    path: 'demo-realtime',
    loadComponent: () => import('./demo-realtime/demo-realtime.page').then( m => m.DemoRealtimePage),
    canActivate: [AuthGuard]
  },

  // Ruta demo-copilot - chat con agente de Copilot Studio
  {
    path: 'demo-copilot',
    loadComponent: () => import('./demo-copilot/demo-copilot.page').then( m => m.DemoCopilotPage),
    canActivate: [AuthGuard]
  },

  // Ruta accounting-accounts - protegida, requiere autenticación
  {
    path: 'accounting-accounts',
    loadComponent: () => import('./accounting-accounts/accounting-accounts.page').then( m => m.AccountingAccountsPage),
    canActivate: [AuthGuard]
  },

  // Ruta companies - protegida, requiere autenticación
  {
    path: 'companies',
    loadComponent: () => import('./companies/companies.page').then( m => m.CompaniesPage),
    canActivate: [AuthGuard]
  },

  // Ruta exam-question - protegida, requiere autenticación
  {
    path: 'exam-question',
    loadComponent: () => import('./exam-question/exam-question.page').then( m => m.ExamQuestionPage),
    canActivate: [AuthGuard]
  },

  // Ruta exam-review - repaso de preguntas sin PDF
  {
    path: 'exam-review',
    loadComponent: () => import('./exam-review/exam-review.page').then( m => m.ExamReviewPage),
    canActivate: [AuthGuard]
  },

  // Ruta CRM - protegida, con sub-rutas para tabs
  {
    path: 'crm',
    loadComponent: () => import('./crm/crm.page').then(m => m.CrmPage),
    canActivate: [AuthGuard],
    children: [
      {
        path: '',
        redirectTo: 'cases',
        pathMatch: 'full'
      },
      {
        path: 'cases',
        loadComponent: () => import('./crm/cases/cases.page').then(m => m.CasesPage)
      },
      {
        path: 'accounts',
        loadComponent: () => import('./crm/accounts/accounts.page').then(m => m.AccountsPage)
      },
      {
        path: 'contacts',
        loadComponent: () => import('./crm/contacts/contacts.page').then(m => m.ContactsPage)
      },
      {
        path: 'system',
        loadComponent: () => import('./crm/system/system.page').then(m => m.SystemPage)
      }
    ]
  },

  // Ruta wildcard - redirige a login para evitar bucles
  {
    path: '**',
    redirectTo: 'login'
  }
];
