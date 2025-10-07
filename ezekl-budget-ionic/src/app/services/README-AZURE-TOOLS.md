# Azure OpenAI Tools Service

## 📋 Descripción

Servicio que gestiona las herramientas (functions/tools) disponibles para Azure OpenAI Realtime API. Permite al asistente de IA interactuar con el backend de la aplicación para ejecutar operaciones y obtener información en tiempo real.

---

## 🏗️ Arquitectura

### Function Calling Flow

```
Usuario → Chat AI → Azure OpenAI Realtime API
                         ↓
                    Decide llamar función
                         ↓
            response.function_call_arguments.done
                         ↓
              DemoRealtimePage.handleFunctionCall()
                         ↓
          AzureOpenAIToolsService.executeTool()
                         ↓
                   HTTP Request al Backend
                         ↓
                  Resultado → Azure OpenAI
                         ↓
              Respuesta al usuario con datos
```

---

## 🔧 Herramientas Disponibles

### 1. `get_accounting_accounts`

Obtiene un listado paginado de cuentas contables del catálogo.

**Descripción**: Permite al asistente consultar el catálogo de cuentas contables con capacidades de búsqueda, ordenamiento y paginación.

**Parámetros**:
- `search` (string, opcional): Término de búsqueda para filtrar por nombre
- `sort` (string, opcional): Campo y dirección de ordenamiento
  - Valores: `idAccountingAccount_asc`, `codeAccountingAccount_asc`, `codeAccountingAccount_desc`, `nameAccountingAccount_asc`, `nameAccountingAccount_desc`
  - Default: `codeAccountingAccount_asc`
- `page` (integer, opcional): Número de página (inicia en 1)
  - Default: 1
- `itemPerPage` (integer, opcional): Elementos por página
  - Rango: 1-100
  - Default: 10

**Ejemplo de Respuesta**:
```json
{
  "success": true,
  "data": {
    "total": 150,
    "accounts": [
      {
        "idAccountingAccount": 1,
        "codeAccountingAccount": "1001",
        "nameAccountingAccount": "Caja General"
      },
      {
        "idAccountingAccount": 2,
        "codeAccountingAccount": "1002",
        "nameAccountingAccount": "Caja Chica"
      }
    ],
    "message": "Se encontraron 150 cuentas contables."
  }
}
```

**Casos de Uso**:
- "¿Cuáles son las cuentas contables disponibles?"
- "Muéstrame las cuentas que contengan 'caja'"
- "Lista las primeras 20 cuentas del catálogo"
- "¿Qué cuentas contables tenemos ordenadas por nombre?"

---

## 🚀 Agregar Nuevas Herramientas

### Paso 1: Definir la Herramienta

Agregar un método que retorne la definición de la herramienta:

```typescript
private getMiNuevaHerramientaTool(): AzureOpenAITool {
  return {
    type: 'function',
    name: 'mi_nueva_herramienta',
    description: 'Descripción clara de qué hace la herramienta',
    parameters: {
      type: 'object',
      properties: {
        parametro1: {
          type: 'string',
          description: 'Descripción del parámetro'
        },
        parametro2: {
          type: 'integer',
          description: 'Otro parámetro',
          minimum: 1
        }
      },
      required: ['parametro1'] // Parámetros obligatorios
    }
  };
}
```

### Paso 2: Registrar en `getAvailableTools()`

```typescript
getAvailableTools(): AzureOpenAITool[] {
  return [
    this.getAccountingAccountsListTool(),
    this.getMiNuevaHerramientaTool() // ← Agregar aquí
  ];
}
```

### Paso 3: Implementar la Ejecución

```typescript
async executeTool(toolName: string, args: any): Promise<ToolExecutionResult> {
  console.log(`🔧 Ejecutando tool: ${toolName}`, args);

  try {
    switch (toolName) {
      case 'get_accounting_accounts':
        return await this.executeGetAccountingAccounts(args);
      
      case 'mi_nueva_herramienta': // ← Agregar case
        return await this.executeMiNuevaHerramienta(args);
      
      default:
        return {
          success: false,
          error: `Herramienta desconocida: ${toolName}`
        };
    }
  } catch (error) {
    // ... manejo de errores
  }
}
```

### Paso 4: Crear el Método de Ejecución

```typescript
private async executeMiNuevaHerramienta(args: any): Promise<ToolExecutionResult> {
  try {
    // Hacer petición HTTP (AuthInterceptor agrega token automáticamente)
    const response = await firstValueFrom(
      this.http.get<any>(`${this.apiUrl}/mi-endpoint`)
    );

    // Retornar resultado
    return {
      success: true,
      data: response
    };

  } catch (error: any) {
    console.error('❌ Error:', error);
    
    // El AuthInterceptor ya maneja 401 automáticamente
    // Solo necesitas formatear el error para el asistente
    return {
      success: false,
      error: error.error?.detail || error.message || 'Error desconocido'
    };
  }
}
```

---

## 📝 Mejores Prácticas

### 1. Descripciones Claras

Las descripciones de herramientas y parámetros deben ser claras y específicas:

✅ **Bueno**:
```typescript
description: 'Obtiene un listado paginado de cuentas contables. Útil cuando el usuario pregunta por el catálogo de cuentas o necesita buscar cuentas específicas.'
```

❌ **Malo**:
```typescript
description: 'Obtiene cuentas'
```

### 2. Validación de Parámetros

Usar los tipos y validaciones de JSON Schema:

```typescript
properties: {
  page: {
    type: 'integer',
    minimum: 1,          // ← Validación
    description: '...'
  },
  email: {
    type: 'string',
    format: 'email',     // ← Validación de formato
    description: '...'
  }
}
```

### 3. Manejo de Errores

El **AuthInterceptor** maneja automáticamente errores 401. Para otros errores:

```typescript
} catch (error: any) {
  console.error('❌ Error:', error);
  
  // Manejar errores específicos según el código HTTP
  if (error.status === 404) {
    return {
      success: false,
      error: 'Recurso no encontrado'
    };
  }
  
  if (error.status === 400) {
    return {
      success: false,
      error: 'Parámetros inválidos: ' + (error.error?.detail || 'Verifica los datos enviados')
    };
  }
  
  // Error genérico
  return {
    success: false,
    error: error.error?.detail || error.message || 'Error desconocido'
  };
}
```

**Nota**: No es necesario manejar 401 ya que el AuthInterceptor lo hace automáticamente.

### 4. Logging Apropiado

Usar logs informativos para debugging:

```typescript
console.log(`🔧 Ejecutando tool: ${toolName}`, args);
console.log(`📡 Llamando a: ${url}`);
console.log('✅ Respuesta obtenida:', response);
console.error('❌ Error:', error);
```

---

## 🔒 Seguridad

### Autenticación Automática

El proyecto utiliza un **AuthInterceptor** que automáticamente agrega el token JWT a todas las peticiones HTTP que van a `/api/`. Esto significa que:

✅ **No necesitas agregar manualmente el token** en cada herramienta
✅ **El interceptor lo hace automáticamente** si el usuario está autenticado
✅ **Maneja errores 401 automáticamente** redirigiendo al login

**Ejemplo de petición HTTP** (el token se agrega automáticamente):
```typescript
// ✅ CORRECTO - El AuthInterceptor agrega el token automáticamente
const response = await firstValueFrom(
  this.http.get<any>(`${this.apiUrl}/accounting-accounts`)
);

// ❌ INNECESARIO - No necesitas agregar el token manualmente
const headers = new HttpHeaders({
  'Authorization': `Bearer ${token}` // ← El interceptor ya hace esto
});
const response = await firstValueFrom(
  this.http.get<any>(url, { headers })
);
```

### Manejo de Errores de Autenticación

El **AuthInterceptor** intercepta errores 401 y automáticamente:
1. Hace logout del usuario
2. Redirige a la página de login
3. Limpia el token del localStorage

En tus herramientas, solo necesitas manejar el error genéricamente:
```typescript
if (error.status === 401) {
  return {
    success: false,
    error: 'Sesión expirada'
  };
}
```

### Validación de Entrada

Aunque Azure OpenAI valida según el schema, es buena práctica validar en el servicio:

```typescript
private validateToolArguments(tool: AzureOpenAITool, args: any): boolean {
  if (!tool.parameters.required) return true;

  for (const requiredParam of tool.parameters.required) {
    if (!(requiredParam in args)) {
      console.error(`❌ Parámetro requerido faltante: ${requiredParam}`);
      return false;
    }
  }

  return true;
}
```

---

## 🧪 Testing

### Prueba Manual

1. Iniciar la aplicación y conectarse al chat
2. Hacer una pregunta que requiera la herramienta:
   - "¿Cuáles son las cuentas contables?"
   - "Muéstrame cuentas que contengan 'banco'"
3. Verificar en consola:
   - `🔧 Función llamada: get_accounting_accounts`
   - `📊 Resultado de la herramienta: ...`
   - `🔄 Solicitando nueva respuesta con resultado de función`
4. Verificar que el asistente responda con los datos obtenidos

### Prueba de Errores

1. **Sin autenticación**: Cerrar sesión y probar la herramienta
2. **Parámetros inválidos**: Forzar parámetros fuera de rango
3. **Backend caído**: Detener el backend y probar

---

## 📚 Referencias

- [Azure OpenAI Realtime API - Function Calling](https://learn.microsoft.com/en-us/azure/ai-services/openai/realtime-audio-quickstart#function-calling)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [JSON Schema Reference](https://json-schema.org/understanding-json-schema/)

---

## 🎯 Próximas Herramientas

Ideas de herramientas futuras a implementar:

- `get_accounting_account_by_id`: Obtener detalles de una cuenta específica
- `create_transaction`: Crear una nueva transacción contable
- `get_transactions`: Listar transacciones con filtros
- `generate_report`: Generar reportes contables
- `get_budget_summary`: Obtener resumen de presupuesto
- `search_documents`: Buscar documentos contables
