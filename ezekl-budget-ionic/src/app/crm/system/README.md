# Página de Sistema CRM

Documentación de la página de **Sistema y Diagnósticos** del módulo CRM de ezekl-budget.

## 🌟 Resumen

Esta página proporciona información en tiempo real sobre el estado del servicio CRM, diagnósticos de conectividad y herramientas administrativas para la integración con Dynamics 365.

## ✅ Funcionalidades Implementadas

### 📊 **Health Check**
- **Estado del servicio** - Verificación básica de disponibilidad del CRM
- **URL de Dynamics 365** - Muestra la instancia configurada
- **Versión de API** - Indica la versión de la API Web de D365 en uso
- **Indicador visual** - Badge con color según estado (ok=verde, error=rojo)

### 🔑 **Información del Token**
- **Vista previa del token** - Muestra parcialmente el token de autenticación (por seguridad)
- **Fecha de expiración** - Timestamp legible de cuando expira el token
- **Botón de limpieza** - Permite limpiar el caché del token manualmente
- **Validez** - Indica si el token actual es válido

### 🔧 **Diagnóstico Completo**
Ejecuta verificaciones exhaustivas del sistema:

#### Variables de Entorno
- `CRM_TENANT_ID` - ID del tenant de Azure AD
- `CRM_CLIENT_ID` - ID de la aplicación registrada
- `CRM_CLIENT_SECRET` - Secreto de la aplicación
- `CRM_D365_BASE_URL` - URL base de Dynamics 365
- `CRM_API_VERSION` - Versión de la API

Cada variable muestra su estado: Configured ✅ / Missing ❌

#### Adquisición de Token
- Estado del proceso de obtención de token
- Mensaje descriptivo del resultado
- Detalles adicionales si hay errores

#### Conectividad D365
- Estado de conexión con Dynamics 365
- Resultado de llamada WhoAmI
- Información del usuario autenticado
- Organización y unidad de negocio

#### Recomendaciones
- Lista automática de problemas detectados
- Sugerencias de configuración
- Pasos de troubleshooting

### 🔄 **Actualización**
- **Pull-to-refresh** - Deslizar hacia abajo para recargar toda la información
- **Carga paralela** - Los tres endpoints se consultan simultáneamente
- **Estados independientes** - Cada sección puede tener éxito o fallar independientemente

## 📱 Componentes Utilizados

### Layout y Navegación
```typescript
app-header          // Header con título "Sistema CRM"
ion-content         // Container principal
ion-refresher       // Pull-to-refresh
ion-grid            // Grid responsive
```

### Visualización de Datos
```typescript
ion-card            // Tarjetas para cada sección (Health, Token, Diagnóstico)
ion-card-header     // Encabezado con ícono y título
ion-card-content    // Contenido de cada tarjeta
ion-item            // Items para mostrar datos clave-valor
ion-label           // Etiquetas y valores
ion-chip            // Badges de estado con colores
ion-skeleton-text   // Loading placeholders animados
```

### Acciones
```typescript
ion-button          // Botón para limpiar caché
ion-icon            // Íconos descriptivos
```

## 🎨 Estados de la Interfaz

### Loading State (Skeleton)
Mientras carga cada sección, muestra placeholders animados que mantienen el layout.

### Success State
Muestra la información completa con:
- Badges de estado coloreados
- Íconos descriptivos
- Formato legible de fechas
- Valores estructurados

### Error State
Cuando falla alguna consulta:
- Item con fondo rojo (color="danger")
- Ícono de error
- Mensaje descriptivo del problema

## 🔧 Configuración Técnica

### Endpoints Consumidos

**Health Check:**
```
GET /api/crm/system/health
```
Retorna:
```typescript
{
  status: 'ok' | 'error',
  d365: string,        // URL de D365
  api_version: string
}
```

**Token Info:**
```
GET /api/crm/system/token
```
Retorna:
```typescript
{
  token_preview: string,    // Vista parcial
  expires_at: number,       // Timestamp Unix
  is_valid: boolean,
  expires_in_seconds: number
}
```

**Diagnóstico:**
```
GET /api/crm/system/diagnose
```
Retorna:
```typescript
{
  environment_variables: { [key: string]: string },
  token_acquisition: { [key: string]: any },
  d365_connectivity: { [key: string]: any },
  recommendations: string[]
}
```

**Limpiar Caché:**
```
POST /api/crm/system/clear-cache
```
Retorna:
```typescript
{
  message: string
}
```

### Carga de Datos

```typescript
// Carga paralela de los 3 endpoints
await Promise.all([
  this.loadHealthCheck(),
  this.loadTokenInfo(),
  this.loadDiagnosis()
]);
```

Cada método maneja sus propios errores independientemente, permitiendo que una sección falle sin afectar a las demás.

### Formato de Datos

**Timestamp a Fecha Legible:**
```typescript
formatTimestamp(1728481234)
// → "9 oct 2024, 15:47"
```

**Color según Estado:**
```typescript
getStatusColor('ok')        // → 'success' (verde)
getStatusColor('error')     // → 'danger' (rojo)
getStatusColor('warning')   // → 'warning' (naranja)
```

**Ícono según Estado:**
```typescript
getStatusIcon('ok')        // → 'checkmarkCircle'
getStatusIcon('error')     // → 'closeCircle'
getStatusIcon('warning')   // → 'warningOutline'
```

## 🔐 Seguridad

### Token Preview
El token nunca se muestra completo. Solo se exponen:
- Primeros 12 caracteres
- Últimos 8 caracteres
- Formato: `eyJ0eXAiOiJ...Q4NDAx8A`

### Autenticación Requerida
Todos los endpoints requieren token JWT válido del usuario de ezekl-budget.

## 🎯 Casos de Uso

### 1. Verificación Rápida del Servicio
Abrir la página para ver si el CRM está funcionando correctamente mediante el Health Check.

### 2. Troubleshooting de Conectividad
Ejecutar diagnóstico completo cuando hay problemas de conexión con D365.

### 3. Renovación de Token
Si hay errores de autenticación, usar el botón "Limpiar Caché de Token" para forzar renovación.

### 4. Auditoría de Configuración
Revisar variables de entorno y estado de configuración en entornos nuevos o después de cambios.

## 📊 Flujo de Usuario

```
Usuario abre página
    ↓
Carga automática de:
  - Health Check
  - Token Info
  - Diagnóstico
    ↓
Visualización de datos
    ↓
¿Hay problemas?
  SÍ → Revisar recomendaciones
       → Limpiar caché si es token
       → Pull-to-refresh después de corregir
  NO  → Servicio operando correctamente
```

## 🧪 Testing

La página incluye suite completa de pruebas:
- Creación del componente
- Carga de datos
- Manejo de errores
- Formato de datos
- Interacciones de usuario
- Verificación de estructura Ionic

Ejecutar tests:
```bash
npm test -- --include='**/system.page.spec.ts'
```

## 🚀 Mejoras Futuras

- [ ] **Auto-refresh** - Actualización automática cada X minutos
- [ ] **Historial** - Registro de estados anteriores del servicio
- [ ] **Notificaciones** - Alertas cuando el servicio está caído
- [ ] **Métricas** - Gráficos de uptime y performance
- [ ] **Export** - Exportar diagnóstico a JSON/PDF
- [ ] **Comparación** - Comparar diagnósticos entre ambientes

## 📚 Referencias

- **Backend API**: `app/api/crm/system.py`
- **Servicio CRM**: `app/services/crm_service.py`
- **Autenticación**: `app/services/crm_auth.py`
- **Modelos**: `app/models/crm.py`
- **Frontend Service**: `src/app/services/crm.service.ts`
- **Modelos Frontend**: `src/app/models/crm.models.ts`
