/**
 * Servicio de herramientas (tools) para Azure OpenAI Realtime API
 * Define las funciones disponibles que el asistente puede llamar
 */
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

/**
 * Definición de una herramienta de Azure OpenAI
 */
export interface AzureOpenAITool {
  type: 'function';
  name: string;
  description: string;
  parameters: {
    type: 'object';
    properties: Record<string, any>;
    required?: string[];
  };
}

/**
 * Resultado de la ejecución de una herramienta
 */
export interface ToolExecutionResult {
  success: boolean;
  data?: any;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AzureOpenAIToolsService {

  private apiUrl = '/api'; // Base URL del backend

  constructor(private http: HttpClient) {}

  /**
   * Obtiene todas las herramientas disponibles para Azure OpenAI
   * Estas se envían en la configuración de la sesión
   */
  getAvailableTools(): AzureOpenAITool[] {
    return [
      this.getAccountingAccountsListTool()
    ];
  }

  /**
   * Ejecuta una herramienta específica basada en su nombre y argumentos
   */
  async executeTool(toolName: string, args: any): Promise<ToolExecutionResult> {
    console.log(`🔧 Ejecutando tool: ${toolName}`, args);

    try {
      switch (toolName) {
        case 'get_accounting_accounts':
          return await this.executeGetAccountingAccounts(args);
        
        default:
          return {
            success: false,
            error: `Herramienta desconocida: ${toolName}`
          };
      }
    } catch (error) {
      console.error(`❌ Error ejecutando tool ${toolName}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error desconocido'
      };
    }
  }

  // ==================== DEFINICIONES DE HERRAMIENTAS ====================

  /**
   * Herramienta: Obtener listado de cuentas contables
   * Permite al asistente consultar el catálogo de cuentas contables
   */
  private getAccountingAccountsListTool(): AzureOpenAITool {
    return {
      type: 'function',
      name: 'get_accounting_accounts',
      description: 'Obtiene un listado paginado de cuentas contables del catálogo. Permite buscar, ordenar y paginar resultados. Útil cuando el usuario pregunta por cuentas contables, el plan de cuentas, o necesita información sobre cuentas específicas.',
      parameters: {
        type: 'object',
        properties: {
          search: {
            type: 'string',
            description: 'Término de búsqueda para filtrar cuentas por nombre (búsqueda parcial). Ejemplo: "caja" encontrará "Caja General", "Caja Chica", etc.'
          },
          sort: {
            type: 'string',
            enum: [
              'idAccountingAccount_asc',
              'codeAccountingAccount_asc',
              'codeAccountingAccount_desc',
              'nameAccountingAccount_asc',
              'nameAccountingAccount_desc'
            ],
            description: 'Campo y dirección de ordenamiento. Por defecto se ordena por código ascendente.',
            default: 'codeAccountingAccount_asc'
          },
          page: {
            type: 'integer',
            description: 'Número de página a obtener (inicia en 1)',
            minimum: 1,
            default: 1
          },
          itemPerPage: {
            type: 'integer',
            description: 'Cantidad de elementos por página',
            minimum: 1,
            maximum: 100,
            default: 10
          }
        },
        required: [] // Todos los parámetros son opcionales
      }
    };
  }

  // ==================== IMPLEMENTACIONES DE HERRAMIENTAS ====================

  /**
   * Implementación: Obtener cuentas contables
   */
  private async executeGetAccountingAccounts(args: any): Promise<ToolExecutionResult> {
    try {
      // Construir query params
      const params: any = {};
      
      if (args.search) params.search = args.search;
      if (args.sort) params.sort = args.sort;
      if (args.page) params.page = args.page;
      if (args.itemPerPage) params.itemPerPage = args.itemPerPage;

      // Obtener token del localStorage
      const token = localStorage.getItem('auth_token');
      if (!token) {
        return {
          success: false,
          error: 'No hay sesión activa. El usuario debe iniciar sesión primero.'
        };
      }

      // Headers con autenticación
      const headers = new HttpHeaders({
        'Authorization': `Bearer ${token}`
      });

      // Construir URL con query params
      const queryString = new URLSearchParams(params).toString();
      const url = `${this.apiUrl}/accounting-accounts${queryString ? '?' + queryString : ''}`;

      console.log(`📡 Llamando a: ${url}`);

      // Ejecutar petición HTTP
      const response = await firstValueFrom(
        this.http.get<any>(url, { headers })
      );

      console.log('✅ Respuesta obtenida:', response);

      // Formatear respuesta para el asistente
      return {
        success: true,
        data: {
          total: response.total || 0,
          accounts: response.data || [],
          message: `Se encontraron ${response.total || 0} cuentas contables.`
        }
      };

    } catch (error: any) {
      console.error('❌ Error en executeGetAccountingAccounts:', error);
      
      // Manejar errores HTTP específicos
      if (error.status === 401) {
        return {
          success: false,
          error: 'Sesión expirada. El usuario debe iniciar sesión nuevamente.'
        };
      }

      return {
        success: false,
        error: error.error?.detail || error.message || 'Error al obtener cuentas contables'
      };
    }
  }

  // ==================== UTILIDADES ====================

  /**
   * Valida que los argumentos de una herramienta cumplan con el schema
   */
  private validateToolArguments(tool: AzureOpenAITool, args: any): boolean {
    // Validación básica - puede expandirse según necesidad
    if (!tool.parameters.required) return true;

    for (const requiredParam of tool.parameters.required) {
      if (!(requiredParam in args)) {
        console.error(`❌ Parámetro requerido faltante: ${requiredParam}`);
        return false;
      }
    }

    return true;
  }

  /**
   * Obtiene una herramienta por su nombre
   */
  getToolByName(toolName: string): AzureOpenAITool | undefined {
    return this.getAvailableTools().find(tool => tool.name === toolName);
  }

  /**
   * Obtiene los nombres de todas las herramientas disponibles
   */
  getToolNames(): string[] {
    return this.getAvailableTools().map(tool => tool.name);
  }
}
