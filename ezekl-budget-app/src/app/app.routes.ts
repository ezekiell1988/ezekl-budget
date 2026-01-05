import { Routes } from '@angular/router';
import { HomePage, ErrorPage } from './pages';

export const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomePage, data: { title: 'Home'} },
  { path: '**', component: ErrorPage, data: { title: '404 Error'} }
];
