# Página de Cuentas - CRM

Documentación de la página de **Cuentas (Accounts)** del módulo CRM de ezekl-budget.

## 🌟 Resumen

Esta página permite la gestión completa de cuentas empresariales de Dynamics 365 CRM con funcionalidad CRUD, búsqueda avanzada, filtros y paginación inteligente.

## ✅ Funcionalidades Implementadas

### 📋 **Gestión CRUD Completa**
- **Listar cuentas** - Lista paginada con infinite scroll automático
- **Crear cuentas** - Formulario reactivo con validaciones
- **Ver detalles** - Modal de solo lectura con información completa
- **Editar cuentas** - Actualización parcial de campos
- **Eliminar cuentas** - Confirmación antes de eliminar

### 🔍 **Búsqueda y Filtros**
- **Búsqueda por nombre** - Integrada en el header con filtro en tiempo real
- **Limpiar filtros** - Botón para resetear todos los filtros

### 🎨 **Interfaz y UX**
- **Pull-to-refresh** - Deslizar hacia abajo para recargar
- **Infinite scroll** - Carga automática de más cuentas al hacer scroll
- **Skeleton screens** - Loading elegante con placeholders animados
- **Estados visuales** - Loading, empty state, error state
- **Formato de fechas** - Legible en español (ej: "9 oct 2025, 10:30")
- **FAB** - Floating Action Button para crear cuentas rápidamente

### ✏️ **Formularios**
- **Validación en tiempo real** - Feedback inmediato en campos
- **Campos requeridos** - Nombre (1-160 caracteres)
- **Campos opcionales** - Número de cuenta, teléfono, email, sitio web, dirección completa
- **Validación de email** - Formato válido requerido
- **Valores por defecto** - Campos vacíos para libertad de entrada

### 🔗 **Integración con CRM**
- **Sincronización D365** - Todos los cambios se reflejan en Dynamics 365
- **Datos de contacto** - Teléfono, email, sitio web
- **Dirección completa** - Calle, ciudad, código postal, país

## 📱 Componentes Utilizados

### Layout y Navegación
```typescript
app-header          // Header con búsqueda integrada
ion-content         // Container principal
ion-refresher       // Pull-to-refresh
ion-infinite-scroll // Paginación automática
ion-fab             // Botón flotante de crear
```

### Visualización de Datos
```typescript
ion-card            // Tarjetas para cada cuenta
ion-list            // Lista de cuentas
ion-skeleton-text   // Loading placeholders
ion-note            // Número de cuenta
ion-icon            // Iconos (call, mail, globe, location)
```

### Modales
```typescript
ion-modal           // Crear, editar, ver detalles
ion-alert           // Confirmación de eliminación
ion-toast           // Notificaciones de éxito/error
```

### Formularios
```typescript
ion-input           // Campos de texto
ion-select          // Selectores (no usados actualmente)
FormGroup           // Formularios reactivos de Angular
Validators          // Validaciones (required, email, minLength, maxLength)
```

## 🔧 Configuración Técnica

### Formularios Reactivos

**Formulario de Creación:**
```typescript
createForm = {
  name: string (requerido, 1-160 chars)
  accountnumber: string (opcional)
  telephone1: string (opcional)
  emailaddress1: string (opcional, formato email)
  websiteurl: string (opcional)
  address1_line1: string (opcional)
  address1_city: string (opcional)
  address1_postalcode: string (opcional)
  address1_country: string (opcional)
}
```

**Formulario de Edición:**
```typescript
editForm = {
  name: string (requerido, 1-160 chars)
  telephone1: string (opcional)
  emailaddress1: string (opcional, formato email)
  websiteurl: string (opcional)
  address1_line1: string (opcional)
  address1_city: string (opcional)
  address1_postalcode: string (opcional)
  address1_country: string (opcional)
}
```

### Paginación
- **Método**: Server-driven paging con `@odata.nextLink` (Dynamics 365)
- **Página inicial**: 25 cuentas
- **Tamaño de página**: 25 cuentas por carga
- **Scroll automático**: Infinite scroll cuando se acerca al final
- **Indicador visual**: "Cargando más cuentas..." mientras carga
- **Ordenamiento**: Por `accountid` (primary key) para resultados determinísticos
- **⚠️ Importante**: D365 NO soporta `$skip`, usa `$skiptoken` en el nextLink

### Búsqueda y Filtros
```typescript
// Búsqueda por nombre (OData contains)
filter_query = "contains(name,'texto búsqueda')"

// Parámetros de consulta inicial
params = {
  top: 25,              // Número de resultados por página
  skip: 0,              // No usado (D365 no soporta $skip)
  filter_query: string, // Filtro OData opcional
  order_by: 'accountid' // Ordenamiento determinístico
}

// Paginación subsecuente usa nextLink completo
// nextLink contiene $skiptoken interno de D365
```

## 📊 Flujo de Operaciones

### Crear Cuenta
```
1. Usuario click en FAB (+)
   ↓
2. Se abre modal con formulario
   ↓
3. Usuario completa campos requeridos (nombre mínimo)
   ↓
4. Click en "Crear Cuenta"
   ↓
5. Validación de formulario
   ↓
6. POST al backend → Dynamics 365
   ↓
7. Toast de éxito + recarga lista
   ↓
8. Modal se cierra automáticamente
```

### Ver Detalles
```
1. Usuario click en botón "Ver" (ojo)
   ↓
2. Se abre modal de solo lectura
   ↓
3. Muestra información de contacto completa
   ↓
4. Muestra dirección completa
   ↓
5. Muestra fechas del sistema (creación/modificación)
   ↓
6. Usuario revisa información
   ↓
7. Click en X o fuera del modal para cerrar
```

### Editar Cuenta
```
1. Usuario click en botón "Editar" (lápiz)
   ↓
2. Modal se abre con formulario pre-rellenado
   ↓
3. Usuario modifica campos deseados
   ↓
4. Click en "Actualizar Cuenta"
   ↓
5. PATCH al backend → Dynamics 365 (solo campos modificados)
   ↓
6. Toast de éxito + actualiza lista
   ↓
7. Modal se cierra
```

### Eliminar Cuenta
```
1. Usuario click en botón "Eliminar" (basura)
   ↓
2. Alert de confirmación aparece
   ↓
3. Usuario confirma eliminación
   ↓
4. DELETE al backend → Dynamics 365
   ↓
5. Toast de éxito + recarga lista
```

### Búsqueda
```
1. Usuario click en icono de búsqueda (header)
   ↓
2. Aparece barra de búsqueda
   ↓
3. Usuario escribe texto
   ↓
4. Búsqueda automática por nombre (debounce aplicado)
   ↓
5. Lista se actualiza con resultados filtrados
   ↓
6. Usuario puede cerrar búsqueda (X) para ver todas las cuentas
```

## 🗂️ Estructura de Archivos

```
accounts/
├── accounts.page.html         # Template HTML con modales
├── accounts.page.ts           # Lógica del componente
├── accounts.page.scss         # Estilos mínimos
├── accounts.page.spec.ts      # Tests unitarios
└── README.md                  # Esta documentación
```

## 🔌 Servicios Utilizados

### CrmService
```typescript
// Listar cuentas con parámetros opcionales (primera página)
getAccounts(params?: CRMListParams): Observable<AccountsListResponse>

// Obtener siguiente página usando nextLink de D365
getAccountsByNextLink(nextLink: string): Observable<AccountsListResponse>

// Obtener cuenta específica por ID
getAccount(accountId: string): Observable<AccountResponse>

// Crear nueva cuenta
createAccount(accountData: AccountCreateRequest): Observable<CRMOperationResponse>

// Actualizar cuenta existente (PATCH - campos modificados)
updateAccount(accountId: string, accountData: AccountUpdateRequest): Observable<CRMOperationResponse>

// Eliminar cuenta
deleteAccount(accountId: string): Observable<CRMOperationResponse>
```

## 📝 Modelos de Datos

### AccountsListResponse
```typescript
interface AccountsListResponse {
  count: number;                  // Total de cuentas disponibles
  accounts: AccountResponse[];    // Array de cuentas en esta página
  next_link?: string;             // URL completa para siguiente página (D365 nextLink)
}
```

### AccountResponse
```typescript
interface AccountResponse {
  accountid: string;              // GUID único
  name: string;                   // Nombre de la cuenta
  accountnumber?: string;         // Número de cuenta
  telephone1?: string;            // Teléfono principal
  emailaddress1?: string;         // Email principal
  websiteurl?: string;            // Sitio web
  address1_line1?: string;        // Dirección línea 1
  address1_city?: string;         // Ciudad
  address1_postalcode?: string;   // Código postal
  address1_country?: string;      // País
  createdon?: string;             // Fecha de creación (ISO 8601)
  modifiedon?: string;            // Fecha de modificación (ISO 8601)
}
```

### AccountCreateRequest
```typescript
interface AccountCreateRequest {
  name: string;                   // Requerido
  accountnumber?: string;
  telephone1?: string;
  emailaddress1?: string;
  websiteurl?: string;
  address1_line1?: string;
  address1_city?: string;
  address1_postalcode?: string;
  address1_country?: string;
}
```

### AccountUpdateRequest
```typescript
interface AccountUpdateRequest {
  name?: string;
  telephone1?: string;
  emailaddress1?: string;
  websiteurl?: string;
  address1_line1?: string;
  address1_city?: string;
  address1_postalcode?: string;
  address1_country?: string;
}
```

## 🧪 Testing

### Tests Implementados
- ✅ Creación del componente
- ✅ Carga inicial de cuentas
- ✅ Visualización de datos en template
- ✅ Estados de loading y vacío
- ✅ Inicialización de formularios
- ✅ Validaciones de campos
- ✅ Apertura/cierre de modales
- ✅ Búsqueda por texto
- ✅ Formateo de fechas
- ✅ Refresh y carga infinita
- ✅ Manejo de errores

### Ejecutar Tests
```bash
npm test -- --include='**/accounts.page.spec.ts'
```

## 🎯 Mejoras Futuras

### Funcionalidades Adicionales
- [ ] Filtro por ciudad
- [ ] Filtro por país
- [ ] Ordenamiento personalizado (nombre, fecha, etc.)
- [ ] Exportar lista a CSV/Excel
- [ ] Importación masiva de cuentas
- [ ] Vista de tarjetas vs lista
- [ ] Búsqueda avanzada con múltiples criterios

### Optimizaciones
- [x] Server-driven paging con nextLink (D365)
- [x] Ordenamiento determinístico por primary key
- [ ] Caché de cuentas recientemente vistas
- [ ] Virtual scroll para listas muy grandes
- [ ] Búsqueda con debounce configurable
- [ ] Paginación configurable por usuario

### UX
- [ ] Filtros guardados/favoritos
- [ ] Acciones rápidas (llamar, email)
- [ ] Historial de cambios
- [ ] Notas y adjuntos

## 📚 Referencias

- [Documentación Ionic](https://ionicframework.com/docs)
- [Dynamics 365 Web API](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/)
- [OData Query Options](https://www.odata.org/getting-started/basic-tutorial/#queryData)
- [Angular Reactive Forms](https://angular.io/guide/reactive-forms)

## 🔗 Páginas Relacionadas

- [Casos](../cases/README.md) - Gestión de casos de soporte
- [Contactos](../contacts/README.md) - Gestión de contactos (próximamente)
- [CRM Dashboard](../README.md) - Documentación general del módulo CRM

---

**Última actualización**: 10 de octubre de 2025  
**Versión**: 1.0.0  
**Autor**: Equipo ezekl-budget
