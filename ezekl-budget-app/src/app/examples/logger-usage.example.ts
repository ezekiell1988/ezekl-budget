/**
 * =====================================================
 * EJEMPLOS DE USO DEL LOGGER SERVICE
 * =====================================================
 * 
 * Este archivo muestra cómo reemplazar console.log/warn/error
 * con el LoggerService en diferentes escenarios.
 */

import { Injectable, Component, inject } from '@angular/core';
import { LoggerService } from '../service/logger.service';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs';

// =====================================================
// EJEMPLO 1: USO EN UN SERVICIO
// =====================================================

@Injectable({
  providedIn: 'root'
})
export class AuthServiceExample {
  private readonly http = inject(HttpClient);
  private readonly logger = inject(LoggerService).getLogger('AuthService');

  loginWithToken(codeLogin: string, token: string) {
    // ❌ ANTES:
    // console.log('📤 Iniciando sesión con token:', { codeLogin, token: '****' });
    
    // ✅ DESPUÉS:
    this.logger.debug('Iniciando sesión con token:', { codeLogin, token: '****' });

    return this.http.post('/api/login', { codeLogin, token }).pipe(
      tap((response: any) => {
        // ❌ ANTES:
        // console.log('📥 Respuesta login:', { ...response, accessToken: '****' });
        // console.log('✅ Sesión iniciada correctamente');
        
        // ✅ DESPUÉS:
        this.logger.debug('Respuesta login:', { ...response, accessToken: '****' });
        this.logger.success('Sesión iniciada correctamente');
      })
    );
  }

  logout() {
    // ❌ ANTES:
    // console.log('🚪 Cerrando sesión...');
    
    // ✅ DESPUÉS:
    this.logger.info('Cerrando sesión...');
  }
}

// =====================================================
// EJEMPLO 2: USO EN UN COMPONENTE
// =====================================================

@Component({
  selector: 'app-login',
  template: ''
})
export class LoginComponentExample {
  private readonly logger = inject(LoggerService).getLogger('LoginPage');

  async requestPin() {
    // ❌ ANTES:
    // console.error('Error solicitando PIN:', error);
    
    // ✅ DESPUÉS:
    try {
      // lógica...
    } catch (error) {
      this.logger.error('Error solicitando PIN:', error);
    }
  }

  async verifyPin() {
    // ❌ ANTES:
    // console.log('✅ Login exitoso, token guardado');
    // console.log('📱 Token:', response.accessToken.substring(0, 20) + '...');
    // console.log('👤 Usuario:', response.user);
    
    // ✅ DESPUÉS:
    this.logger.success('Login exitoso, token guardado');
    this.logger.debug('Token:', 'response.accessToken.substring(0, 20)...');
    this.logger.debug('Usuario:', 'response.user');

    // Opción avanzada: Usar grupos
    this.logger.groupCollapsed('Detalles del login');
    this.logger.debug('Token:', 'tokenValue');
    this.logger.debug('Usuario:', 'userData');
    this.logger.debug('Expira en:', 'expiresAt');
    this.logger.groupEnd();
  }
}

// =====================================================
// EJEMPLO 3: LOGS HTTP (INTERCEPTOR)
// =====================================================

@Injectable()
export class HttpLoggerInterceptorExample {
  private readonly logger = inject(LoggerService).getLogger('HttpInterceptor');

  intercept(req: any, next: any) {
    // ❌ ANTES:
    // console.log(`📤 ${req.method} ${req.url}`);
    
    // ✅ DESPUÉS:
    this.logger.http(req.method, req.url, req.body);

    return next.handle(req).pipe(
      tap((response: any) => {
        // ❌ ANTES:
        // console.log(`📥 ${response.status} ${req.url}`);
        
        // ✅ DESPUÉS:
        this.logger.httpResponse(response.status, req.url, response.body);
      })
    );
  }
}

// =====================================================
// EJEMPLO 4: LOGS CONDICIONALES
// =====================================================

@Injectable()
export class DataServiceExample {
  private readonly logger = inject(LoggerService).getLogger('DataService');
  
  // ❌ ANTES:
  private readonly DEBUG = false;
  
  fetchData() {
    // ❌ ANTES:
    // if (this.DEBUG) {
    //   console.log('Fetching data...');
    // }
    
    // ✅ DESPUÉS (ya no necesitas la bandera DEBUG):
    this.logger.debug('Fetching data...');
    // El logger automáticamente NO mostrará esto en producción
  }
}

// =====================================================
// EJEMPLO 5: DIFERENTES NIVELES DE LOG
// =====================================================

@Component({
  selector: 'app-example',
  template: ''
})
export class LogLevelsExample {
  private readonly logger = inject(LoggerService).getLogger('Example');

  demonstrateLevels() {
    // 🔍 DEBUG - Detalles técnicos (solo dev)
    this.logger.debug('Variable value:', { foo: 'bar' });
    
    // ℹ️ INFO - Flujo normal
    this.logger.info('User logged in successfully');
    
    // ⚠️ WARN - Algo inesperado
    this.logger.warn('Token expiring soon');
    
    // ❌ ERROR - Algo falló
    this.logger.error('Failed to load data:', new Error('Network error'));
    
    // ✅ SUCCESS - Operación exitosa
    this.logger.success('Profile updated successfully');
  }

  // Logs con tablas
  showTable() {
    const users = [
      { id: 1, name: 'Juan' },
      { id: 2, name: 'María' }
    ];
    
    this.logger.table(users);
  }

  // Logs agrupados
  showGroupedLogs() {
    this.logger.group('User Details');
    this.logger.debug('Name:', 'Juan Pérez');
    this.logger.debug('Email:', 'juan@example.com');
    this.logger.debug('Role:', 'Admin');
    this.logger.groupEnd();
  }
}

// =====================================================
// CONFIGURACIÓN GLOBAL (en main.ts o app.config.ts)
// =====================================================

/*
import { LoggerService, LogLevel } from './app/service';

// En el bootstrapApplication o ApplicationConfig
export const appConfig: ApplicationConfig = {
  providers: [
    // ... otros providers
    {
      provide: APP_INITIALIZER,
      useFactory: (logger: LoggerService) => {
        return () => {
          // Configurar logger globalmente
          logger.configure({
            minLevel: LogLevel.DEBUG, // o LogLevel.ERROR para producción
            showTimestamp: true,
            showContext: true,
            useColors: true
          });
        };
      },
      deps: [LoggerService],
      multi: true
    }
  ]
};
*/
