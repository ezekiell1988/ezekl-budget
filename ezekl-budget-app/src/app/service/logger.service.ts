import { Injectable, inject, isDevMode } from '@angular/core';

/**
 * Niveles de logging disponibles
 */
export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  NONE = 4
}

/**
 * Configuración del logger
 */
export interface LoggerConfig {
  /** Nivel mínimo de logging (por defecto INFO en dev, ERROR en prod) */
  minLevel: LogLevel;
  /** Habilitar timestamps en los logs */
  showTimestamp: boolean;
  /** Habilitar el nombre del contexto/módulo en los logs */
  showContext: boolean;
  /** Color de los logs en consola */
  useColors: boolean;
}

/**
 * Servicio de logging centralizado con soporte para Angular 20+
 * 
 * Características:
 * - Control global de logs por environment
 * - Niveles de logging (debug, info, warn, error)
 * - Contexto por módulo/componente
 * - Timestamps opcionales
 * - Colores en consola
 * - Zero logs en producción por defecto
 * 
 * @example
 * ```typescript
 * // En un componente
 * private logger = inject(LoggerService).getLogger('LoginComponent');
 * 
 * this.logger.debug('Usuario ingresó:', usuario);
 * this.logger.info('Login exitoso');
 * this.logger.warn('Token expirando pronto');
 * this.logger.error('Error en autenticación:', error);
 * 
 * // En un servicio
 * private logger = inject(LoggerService).getLogger('AuthService');
 * ```
 */
@Injectable({
  providedIn: 'root'
})
export class LoggerService {
  private config: LoggerConfig = {
    minLevel: isDevMode() ? LogLevel.DEBUG : LogLevel.ERROR,
    showTimestamp: true,
    showContext: true,
    useColors: true
  };

  /**
   * Configurar el logger globalmente
   * @param config Configuración parcial o completa
   */
  configure(config: Partial<LoggerConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Crear un logger con contexto específico
   * @param context Nombre del componente/servicio (ej: 'LoginPage', 'AuthService')
   * @returns Logger con contexto
   */
  getLogger(context: string): Logger {
    return new Logger(context, this.config);
  }

  /**
   * Logger global sin contexto (no recomendado, mejor usar getLogger)
   */
  debug(...args: any[]): void {
    this.getLogger('Global').debug(...args);
  }

  info(...args: any[]): void {
    this.getLogger('Global').info(...args);
  }

  warn(...args: any[]): void {
    this.getLogger('Global').warn(...args);
  }

  error(...args: any[]): void {
    this.getLogger('Global').error(...args);
  }
}

/**
 * Logger con contexto específico
 */
export class Logger {
  constructor(
    private readonly context: string,
    private readonly config: LoggerConfig
  ) {}

  /**
   * Log de debug (detalles técnicos, solo en desarrollo)
   */
  debug(...args: any[]): void {
    this.log(LogLevel.DEBUG, '🔍', 'debug', '#6c757d', args);
  }

  /**
   * Log informativo (flujo normal de la app)
   */
  info(...args: any[]): void {
    this.log(LogLevel.INFO, 'ℹ️', 'info', '#0dcaf0', args);
  }

  /**
   * Advertencia (algo inesperado pero no crítico)
   */
  warn(...args: any[]): void {
    this.log(LogLevel.WARN, '⚠️', 'warn', '#ffc107', args);
  }

  /**
   * Error (algo salió mal y requiere atención)
   */
  error(...args: any[]): void {
    this.log(LogLevel.ERROR, '❌', 'error', '#dc3545', args);
  }

  /**
   * Log de éxito (operación completada correctamente)
   */
  success(...args: any[]): void {
    this.log(LogLevel.INFO, '✅', 'log', '#198754', args);
  }

  /**
   * Log de petición HTTP
   */
  http(method: string, url: string, ...args: any[]): void {
    this.log(LogLevel.DEBUG, '📤', 'debug', '#0d6efd', [`${method} ${url}`, ...args]);
  }

  /**
   * Log de respuesta HTTP
   */
  httpResponse(status: number, url: string, ...args: any[]): void {
    const icon = status >= 200 && status < 300 ? '📥' : '⚠️';
    const level = status >= 400 ? LogLevel.WARN : LogLevel.DEBUG;
    this.log(level, icon, 'debug', '#0d6efd', [`${status} ${url}`, ...args]);
  }

  /**
   * Método interno para procesar y mostrar logs
   */
  private log(
    level: LogLevel,
    icon: string,
    method: 'log' | 'info' | 'warn' | 'error' | 'debug',
    color: string,
    args: any[]
  ): void {
    // Verificar nivel mínimo
    if (level < this.config.minLevel) {
      return;
    }

    // Construir prefijo
    const parts: string[] = [];
    
    if (this.config.showTimestamp) {
      const timestamp = new Date().toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        fractionalSecondDigits: 3
      });
      parts.push(`[${timestamp}]`);
    }

    if (this.config.showContext) {
      parts.push(`[${this.context}]`);
    }

    parts.push(icon);

    // Construir mensaje
    const prefix = parts.join(' ');

    // Mostrar en consola con estilos
    if (this.config.useColors && typeof window !== 'undefined') {
      console[method](
        `%c${prefix}`,
        `color: ${color}; font-weight: bold;`,
        ...args
      );
    } else {
      console[method](prefix, ...args);
    }
  }

  /**
   * Crear un grupo de logs colapsable
   */
  group(label: string): void {
    if (this.config.minLevel <= LogLevel.DEBUG) {
      const prefix = this.buildPrefix();
      console.group(`${prefix} 📁 ${label}`);
    }
  }

  /**
   * Crear un grupo de logs colapsado por defecto
   */
  groupCollapsed(label: string): void {
    if (this.config.minLevel <= LogLevel.DEBUG) {
      const prefix = this.buildPrefix();
      console.groupCollapsed(`${prefix} 📁 ${label}`);
    }
  }

  /**
   * Cerrar grupo de logs
   */
  groupEnd(): void {
    if (this.config.minLevel <= LogLevel.DEBUG) {
      console.groupEnd();
    }
  }

  /**
   * Mostrar tabla en consola
   */
  table(data: any): void {
    if (this.config.minLevel <= LogLevel.DEBUG) {
      const prefix = this.buildPrefix();
      console.log(`${prefix} 📊 Tabla:`);
      console.table(data);
    }
  }

  /**
   * Construir prefijo para logs
   */
  private buildPrefix(): string {
    const parts: string[] = [];
    
    if (this.config.showTimestamp) {
      const timestamp = new Date().toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
      parts.push(`[${timestamp}]`);
    }

    if (this.config.showContext) {
      parts.push(`[${this.context}]`);
    }

    return parts.join(' ');
  }
}
