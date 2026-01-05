import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient } from '@angular/common/http';
import { Title } from '@angular/platform-browser';
import { routes } from './app.routes';
import { AppSettings } from './service/app-settings.service';
import { AppVariablesService } from './service/app-variables.service';
import { AppMenuService } from './service/app-menus.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes, withComponentInputBinding()),
    provideAnimations(),
    provideHttpClient(),
    Title,
    AppSettings,
    AppVariablesService,
    AppMenuService
  ]
};
