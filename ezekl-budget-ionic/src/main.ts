import { bootstrapApplication } from '@angular/platform-browser';
import { RouteReuseStrategy, provideRouter, withPreloading, PreloadAllModules } from '@angular/router';
import { LocationStrategy, HashLocationStrategy } from '@angular/common';
import { IonicRouteStrategy, provideIonicAngular } from '@ionic/angular/standalone';
import { provideHttpClient, withInterceptorsFromDi, HTTP_INTERCEPTORS } from '@angular/common/http';
import { addIcons } from 'ionicons';
import {
  businessOutline,
  personOutline,
  documentTextOutline,
  medicalOutline,
  alertCircleOutline,
  buildOutline,
  clipboardOutline,
  folderOutline,
  settingsOutline,
  refreshOutline,
  add,
  eyeOutline,
  createOutline,
  trashOutline,
  closeOutline,
  saveOutline
} from 'ionicons/icons';

import { routes } from './app/app.routes';
import { AppComponent } from './app/app.component';
import { AuthInterceptor } from './app/interceptors/auth.interceptor';

// Suprimir warning de iconos duplicados de Ionicons
// Este warning ocurre cuando Ionic registra iconos por defecto que también registramos manualmente
const originalConsoleWarn = console.warn;
console.warn = function(...args: any[]) {
  if (args[0]?.includes?.('Multiple icons were mapped to name')) {
    return; // Ignorar este warning específico
  }
  originalConsoleWarn.apply(console, args);
};

// Registrar iconos globalmente
addIcons({
  'business-outline': businessOutline,
  'person-outline': personOutline,
  'document-text-outline': documentTextOutline,
  'medical-outline': medicalOutline,
  'alert-circle-outline': alertCircleOutline,
  'build-outline': buildOutline,
  'clipboard-outline': clipboardOutline,
  'folder-outline': folderOutline,
  'settings-outline': settingsOutline,
  'refresh-outline': refreshOutline,
  'add': add,
  'eye-outline': eyeOutline,
  'create-outline': createOutline,
  'trash-outline': trashOutline,
  'close-outline': closeOutline,
  'save-outline': saveOutline
});

bootstrapApplication(AppComponent, {
  providers: [
    { provide: RouteReuseStrategy, useClass: IonicRouteStrategy },
    { provide: LocationStrategy, useClass: HashLocationStrategy },
    provideIonicAngular(),
    provideRouter(routes, withPreloading(PreloadAllModules)),
    provideHttpClient(withInterceptorsFromDi()),
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    },
  ],
});
