# 🔍 LoggerService - Sistema de Logging Centralizado

Sistema de logging profesional para Angular 20+ que controla automáticamente los logs según el environment (desarrollo/producción).

## 📋 Tabla de Contenido

- [¿Por qué usar LoggerService?](#por-qué-usar-loggerservice)
- [Instalación](#instalación)
- [Uso Básico](#uso-básico)
- [Niveles de Log](#niveles-de-log)
- [Configuración](#configuración)
- [Ejemplos Avanzados](#ejemplos-avanzados)
- [Migración desde console.log](#migración-desde-consolelog)

---

## 🎯 ¿Por qué usar LoggerService?

### ❌ Problema Anterior

```typescript
// Logs por todas partes sin control
console.log('✅ Login exitoso');
console.error('❌ Error:', error);
console.log('Debug info:', data);

// En producción TODOS estos logs se muestran 😱
// No hay forma fácil de deshabilitarlos
```

### ✅ Solución con LoggerService

```typescript
// Un solo logger centralizado
this.logger.success('Login exitoso');
this.logger.error('Error:', error);
this.logger.debug('Debug info:', data); // ← NO se muestra en producción 🎉
```

### Ventajas

✅ **Control automático** - Logs se deshabilitan en producción  
✅ **Consistencia** - Mismo formato en toda la app  
✅ **Contexto** - Saber QUÉ componente/servicio generó el log  
✅ **Timestamps** - Cuándo ocurrió cada log  
✅ **Niveles** - debug, info, warn, error, success  
✅ **Colores** - Fácil identificación visual  
✅ **Performance** - Zero overhead en producción  

---

## 📦 Instalación

### 1. Archivo ya creado

El servicio ya está en:
```
src/app/service/logger.service.ts
```

### 2. Ya exportado desde el barrel

```typescript
// src/app/service/index.ts
export { LoggerService, LogLevel, type LoggerConfig } from './logger.service';
```

### 3. Configuración en environments

#### Development (`environment.ts`)

```typescript
export const environment = {
  production: false,
  apiUrl: 'api/v1/',
  
  logging: {
    enabled: true,        // ✅ Todos los logs habilitados
    showTimestamp: true,
    showContext: true,
    useColors: true
  }
};
```

#### Production (`environment.prod.ts`)

```typescript
export const environment = {
  production: true,
  apiUrl: 'api/v1/',
  
  logging: {
    enabled: false,       // ❌ Solo errores críticos
    showTimestamp: false,
    showContext: false,
    useColors: false
  }
};
```

---

## 🚀 Uso Básico

### En un Componente

```typescript
import { Component, inject } from '@angular/core';
import { LoggerService } from '../../service';

@Component({
  selector: 'app-login',
  templateUrl: './login.html'
})
export class LoginPage {
  // Crear logger con contexto del componente
  private readonly logger = inject(LoggerService).getLogger('LoginPage');

  ngOnInit() {
    this.logger.info('Componente inicializado');
  }

  async login() {
    this.logger.debug('Intentando login...');
    
    try {
      const response = await this.authService.login();
      this.logger.success('Login exitoso');
    } catch (error) {
      this.logger.error('Error en login:', error);
    }
  }
}
```

### En un Servicio

```typescript
import { Injectable, inject } from '@angular/core';
import { LoggerService } from './logger.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly logger = inject(LoggerService).getLogger('AuthService');

  loginWithToken(code: string, token: string) {
    this.logger.debug('Iniciando sesión con token');
    
    return this.http.post('/api/login', { code, token }).pipe(
      tap(response => {
        this.logger.success('Sesión iniciada correctamente');
        this.logger.debug('Usuario:', response.user);
      }),
      catchError(error => {
        this.logger.error('Error en login:', error);
        return throwError(() => error);
      })
    );
  }
}
```

---

## 📊 Niveles de Log

### 🔍 DEBUG - Detalles técnicos

```typescript
this.logger.debug('Variable value:', { foo: 'bar' });
this.logger.debug('Token recibido:', token.substring(0, 20) + '...');
```

**Cuándo usar:** Información técnica detallada útil solo durante desarrollo.  
**En producción:** ❌ NO se muestra

---

### ℹ️ INFO - Flujo normal

```typescript
this.logger.info('Componente inicializado');
this.logger.info('Usuario navegó a:', route);
```

**Cuándo usar:** Eventos normales del flujo de la aplicación.  
**En producción:** ⚠️ Se muestra (usar con moderación)

---

### ⚠️ WARN - Advertencias

```typescript
this.logger.warn('Token expirando en 5 minutos');
this.logger.warn('API respondió con status 404');
```

**Cuándo usar:** Algo inesperado pero no crítico.  
**En producción:** ✅ Se muestra

---

### ❌ ERROR - Errores

```typescript
this.logger.error('Error cargando datos:', error);
this.logger.error('Autenticación fallida');
```

**Cuándo usar:** Errores que requieren atención.  
**En producción:** ✅ Se muestra

---

### ✅ SUCCESS - Operaciones exitosas

```typescript
this.logger.success('Login exitoso');
this.logger.success('Datos guardados correctamente');
```

**Cuándo usar:** Confirmar operaciones importantes completadas.  
**En producción:** ℹ️ Se muestra como INFO

---

## ⚙️ Configuración

### Opción 1: Usar defaults (Recomendado)

El logger ya viene configurado automáticamente:
- **Development:** Todos los logs habilitados
- **Production:** Solo errores críticos

No necesitas hacer nada más. 🎉

---

### Opción 2: Configuración personalizada

Si necesitas ajustar el comportamiento:

```typescript
import { LoggerService, LogLevel } from './service';

export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: (logger: LoggerService) => {
        return () => {
          logger.configure({
            minLevel: LogLevel.DEBUG,    // Nivel mínimo
            showTimestamp: true,         // Mostrar hora
            showContext: true,           // Mostrar componente/servicio
            useColors: true              // Colores en consola
          });
        };
      },
      deps: [LoggerService],
      multi: true
    }
  ]
};
```

---

## 🎓 Ejemplos Avanzados

### Logs HTTP

```typescript
// Antes de la petición
this.logger.http('POST', '/api/login', requestBody);

// Después de la respuesta
this.logger.httpResponse(200, '/api/login', responseBody);
```

**Output en consola:**
```
[10:30:45.123] [AuthService] 📤 POST /api/login { code: "user123" }
[10:30:45.456] [AuthService] 📥 200 /api/login { success: true }
```

---

### Logs Agrupados

```typescript
this.logger.group('Detalles del Usuario');
this.logger.debug('ID:', user.id);
this.logger.debug('Nombre:', user.name);
this.logger.debug('Email:', user.email);
this.logger.debug('Rol:', user.role);
this.logger.groupEnd();
```

**Output en consola:**
```
▼ [10:30:45] [UserService] 📁 Detalles del Usuario
    [10:30:45] [UserService] 🔍 ID: 123
    [10:30:45] [UserService] 🔍 Nombre: Juan Pérez
    [10:30:45] [UserService] 🔍 Email: juan@example.com
    [10:30:45] [UserService] 🔍 Rol: Admin
```

---

### Logs en Tabla

```typescript
const users = [
  { id: 1, name: 'Juan', role: 'Admin' },
  { id: 2, name: 'María', role: 'User' }
];

this.logger.table(users);
```

**Output en consola:**
```
┌─────────┬────┬─────────┬─────────┐
│ (index) │ id │  name   │  role   │
├─────────┼────┼─────────┼─────────┤
│    0    │ 1  │ 'Juan'  │ 'Admin' │
│    1    │ 2  │ 'María' │ 'User'  │
└─────────┴────┴─────────┴─────────┘
```

---

## 🔄 Migración desde console.log

### Búsqueda y Reemplazo

Usa VS Code para buscar todos los `console.` y reemplazarlos:

#### 1. Buscar en archivos

```
Ctrl/Cmd + Shift + F
```

Buscar: `console\.(log|warn|error|info)`

#### 2. Reemplazos comunes

| Antes | Después |
|-------|---------|
| `console.log('Info')` | `this.logger.info('Info')` |
| `console.debug('Debug')` | `this.logger.debug('Debug')` |
| `console.warn('Warning')` | `this.logger.warn('Warning')` |
| `console.error('Error')` | `this.logger.error('Error')` |
| `console.log('✅ Success')` | `this.logger.success('Success')` |

#### 3. Agregar logger al componente/servicio

```typescript
// Al inicio de la clase
private readonly logger = inject(LoggerService).getLogger('NombreClase');
```

---

### Ejemplo Completo de Migración

#### ❌ ANTES

```typescript
export class LoginPage {
  async login() {
    console.log('Intentando login...');
    
    try {
      const response = await this.authService.login();
      console.log('✅ Login exitoso');
      console.log('Token:', response.token);
      console.log('Usuario:', response.user);
    } catch (error) {
      console.error('❌ Error en login:', error);
    }
  }
}
```

#### ✅ DESPUÉS

```typescript
export class LoginPage {
  private readonly logger = inject(LoggerService).getLogger('LoginPage');

  async login() {
    this.logger.debug('Intentando login...');
    
    try {
      const response = await this.authService.login();
      this.logger.success('Login exitoso');
      this.logger.debug('Token:', response.token);
      this.logger.debug('Usuario:', response.user);
    } catch (error) {
      this.logger.error('Error en login:', error);
    }
  }
}
```

---

## 📝 Buenas Prácticas

### ✅ DO - Hacer

```typescript
// 1. Usar el contexto correcto
private readonly logger = inject(LoggerService).getLogger('AuthService');

// 2. Usar el nivel apropiado
this.logger.debug('Variable interna:', data);  // Solo dev
this.logger.error('Error crítico:', error);    // Prod también

// 3. Logs descriptivos
this.logger.info('Usuario autenticado:', user.email);

// 4. Agrupar logs relacionados
this.logger.group('Procesando pedido');
this.logger.debug('Items:', order.items);
this.logger.debug('Total:', order.total);
this.logger.groupEnd();
```

### ❌ DON'T - No hacer

```typescript
// 1. NO usar console directamente
console.log('Algo');  // ❌

// 2. NO usar INFO para debugging
this.logger.info('Variable x =', x);  // ❌ Usar debug()

// 3. NO loggear datos sensibles
this.logger.debug('Password:', password);  // ❌ ¡Peligro!

// 4. NO loggear TODO en producción
this.logger.info('Click en botón');  // ❌ Demasiado ruido
```

---

## 🎨 Output en Consola

### Development (con colores)

```
[10:30:45.123] [LoginPage] 🔍 Intentando login...
[10:30:45.456] [AuthService] 📤 POST /api/login
[10:30:45.789] [AuthService] 📥 200 /api/login
[10:30:45.890] [LoginPage] ✅ Login exitoso
[10:30:45.891] [LoginPage] 🔍 Token: eyJhbGc...
[10:30:45.892] [LoginPage] 🔍 Usuario: { id: 123, name: "Juan" }
[10:30:45.950] [LoginPage] ℹ️ Navegando a: /home
```

### Production (sin colores, solo errores)

```
[AuthService] ❌ Error en autenticación: Unauthorized
```

---

## 🏁 Checklist de Implementación

- [x] ✅ LoggerService creado en `service/logger.service.ts`
- [x] ✅ Exportado desde `service/index.ts`
- [x] ✅ Configuración agregada en `environment.ts`
- [x] ✅ Configuración agregada en `environment.prod.ts`
- [ ] 🔄 Migrar `console.log` a `logger.debug()`
- [ ] 🔄 Migrar `console.error` a `logger.error()`
- [ ] 🔄 Migrar `console.warn` a `logger.warn()`
- [ ] 🔄 Agregar logger en componentes/servicios nuevos
- [ ] 🔄 Probar en development (logs visibles)
- [ ] 🔄 Probar build producción (logs ocultos)

---

## 📚 Recursos Adicionales

- [Archivo de ejemplos](../examples/logger-usage.example.ts)
- [LoginPage refactorizado](../pages/login/login.ts)
- [AuthService refactorizado](../service/auth.service.ts) (pendiente)

---

## 🤝 Contribuir

Si encuentras formas de mejorar el logger:
1. Actualiza `logger.service.ts`
2. Actualiza este README
3. Agrega ejemplos en `logger-usage.example.ts`

---

## 📄 Licencia

Mismo que el proyecto principal.

---

**¿Preguntas?** Revisa los ejemplos en [`logger-usage.example.ts`](../examples/logger-usage.example.ts)
