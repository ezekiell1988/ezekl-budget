# Demo Copilot - Integración con Copilot Studio

## 📋 Descripción

Implementación de un chat en tiempo real que se conecta a un agente de Microsoft Copilot Studio usando Direct Line API. Permite conversaciones por texto con el agente personalizado.

---

## 🏗️ Arquitectura de la Solución

### Tecnologías Utilizadas

- **Frontend**: Ionic 8.0.0 + Angular 20.0.0 (Standalone Components)
- **Backend**: FastAPI (endpoint para token de Direct Line)
- **Microsoft**: Direct Line API v3
- **Copilot Studio**: Agente personalizado

---

## ⚙️ Configuración del Agente

### Datos del Agente Copilot Studio

La configuración del agente está centralizada en el objeto `copilotConfig`:

```typescript
private readonly copilotConfig = {
  environmentId: '3c48723d-81b5-473a-9006-a54c8652fe7c',
  tenantId: '2f80d4e1-da0e-4b6d-84da-30f67e280e4b',
  botId: '821348e9-0a4b-4805-9085-492c217c0bd0',
  schemaName: 'cr389_agent_ROzgg7',
  directLineEndpoint: 'https://directline.botframework.com/v3/directline',
};
```

**Nota:** La autenticación se maneja en el backend usando OAuth2 con Microsoft Entra ID.

---

## 🔐 Seguridad - Autenticación con Copilot Studio

**⚠️ IMPORTANTE**: La autenticación se maneja de forma segura en el backend usando OAuth2 con Microsoft Entra ID.

### Variables de Entorno Requeridas (Backend)

Agrega estas variables al archivo `.env` en la raíz del proyecto backend:

```env
# Microsoft Copilot Studio Configuration
COPILOT_ENVIRONMENT_ID=<tu-environment-id>
COPILOT_SCHEMA_NAME=<tu-schema-name>
COPILOT_TENANT_ID=<tu-tenant-id>
COPILOT_AGENT_APP_ID=<tu-agent-app-id>
COPILOT_CLIENT_SECRET=<tu-client-secret>
```

### Flujo de Autenticación

1. **Frontend** solicita token al backend: `GET /api/copilot/token`
2. **Backend** obtiene access token de Microsoft Entra ID usando client credentials
3. **Backend** usa el access token para iniciar conversación con Direct Line
4. **Backend** devuelve token de Direct Line + conversationId al frontend
5. **Frontend** usa el token para comunicarse con el agente

---

## 🚀 Cómo Usar

### 1. Configurar Backend

Crea el endpoint para generar tokens de Direct Line (ver sección anterior).

### 2. Agregar Ruta

La ruta ya está lista para ser agregada a `app.routes.ts`:

```typescript
{
  path: 'demo-copilot',
  loadComponent: () => import('./demo-copilot/demo-copilot.page').then( m => m.DemoCopilotPage),
  canActivate: [AuthGuard]
},
```

### 3. Navegar a la Página

```typescript
this.router.navigate(['/demo-copilot']);
```

---

## 📦 Interfaces y Modelos

### `ChatMessage`
```typescript
interface ChatMessage {
  id: string;          // ID único del mensaje
  role: 'user' | 'bot'; // Rol del emisor
  text: string;        // Contenido del mensaje
  timestamp: string;   // Timestamp ISO 8601
}
```

### `DirectLineToken`
```typescript
interface DirectLineToken {
  token: string;           // Token de acceso
  conversationId?: string; // ID de la conversación (opcional)
}
```

---

## 🔄 Flujo de Comunicación

1. **Conexión Inicial**:
   - Genera token de Direct Line (backend)
   - Inicia conversación con Direct Line API
   - Obtiene `conversationId` y `streamUrl`

2. **Envío de Mensajes**:
   - Usuario escribe mensaje
   - Se envía a Direct Line API
   - Direct Line lo envía al agente de Copilot Studio

3. **Recepción de Respuestas**:
   - Polling cada 2 segundos
   - Obtiene nuevos mensajes con `watermark`
   - Muestra respuestas del bot

---

## 🔧 Variables de Estado

```typescript
// Conexión
isConnected: boolean = false;
isConnecting: boolean = false;
connectionStatusText: string = 'Desconectado';

// Mensajes
messages: ChatMessage[] = [];
messageText: string = '';
isBotTyping: boolean = false;

// Direct Line
private token: string = '';
private conversationId: string = '';
private streamUrl: string = '';
private watermark: string = '';
private pollingInterval: any = null;
```

---

## 🎨 Estilos

El componente usa un diseño similar a WhatsApp con componentes Ionic:
- Mensajes del usuario alineados a la derecha (azul)
- Mensajes del bot alineados a la izquierda (gris)
- Indicador de escritura cuando el bot está procesando
- Responsive design para móvil y desktop

---

## 📚 Referencias

- [Direct Line API v3](https://docs.microsoft.com/en-us/azure/bot-service/rest-api/bot-framework-rest-direct-line-3-0-concepts)
- [Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/)
- [Bot Framework](https://dev.botframework.com/)
