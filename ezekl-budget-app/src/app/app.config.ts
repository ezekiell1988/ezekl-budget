import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient } from '@angular/common/http';
import { Title } from '@angular/platform-browser';
import { provideIonicAngular } from '@ionic/angular/standalone';
import { routes } from './app.routes';
import { AppSettings } from './service/app-settings.service';
import { AppVariablesService } from './service/app-variables.service';
import { AppMenuService } from './service/app-menus.service';
import { PlatformDetectorService } from './service/platform-detector.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes, withComponentInputBinding()),
    provideAnimations(),
    provideHttpClient(),
    provideIonicAngular({
      // Configuración de Ionic
      mode: 'ios', // Usar estilo iOS para consistencia
      animated: true,
      // Configurar la ruta de assets de Ionicons
      innerHTMLTemplatesEnabled: true,
      // Los iconos se cargarán desde CDN de Ionicons
    }),
    Title,
    AppSettings,
    AppVariablesService,
    AppMenuService,
    PlatformDetectorService
  ]
};
