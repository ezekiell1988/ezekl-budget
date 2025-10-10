# Página CRM - Interface de Usuario

Esta documentación describe la **página web CRM** de ezekl-budget, una interfaz moderna con tabs para gestionar Dynamics 365 CRM desde el frontend.

## 🌟 Resumen de la Página

La página CRM es una **Single Page Application (SPA)** construida con **Angular + Ionic** que proporciona una interfaz intuitiva y completa para gestionar:
- **Casos de soporte** (Incidents)
- **Cuentas corporativas** (Accounts) 
- **Contactos** (Contacts)
- **Diagnósticos del sistema** (System Health)

## 📱 Diseño y Arquitectura

### Estructura de Tabs
La página utiliza **`ion-tabs`** de Ionic para organizar las diferentes secciones:

```
┌─────────────────────────────────────┐
│  📋 Casos  │ 🏢 Cuentas │ 👤 Contactos │ 🔧 Sistema │
├─────────────────────────────────────┤
│                                     │
│        Contenido del Tab            │
│     (router-outlet dinámico)        │
│                                     │
└─────────────────────────────────────┘
```

### Rutas y Navegación
```typescript
/crm                    → Redirige a /crm/cases
/crm/cases              → Tab de Casos (CRUD completo)
/crm/accounts           → Tab de Cuentas (en desarrollo) 
/crm/contacts           → Tab de Contactos (en desarrollo)
/crm/system             → Tab de Sistema y Diagnósticos
```

### Cómo Acceder
- **Desde el menú lateral**: Busca el ícono `business-outline` con badge "NEW"
- **URL directa**: Navega a `/crm` desde el navegador
- **Programáticamente**: `this.router.navigate(['/crm/cases'])`

## 📋 Tab de Casos - Funcionalidades Implementadas

> 📖 **Documentación completa**: Ver [README de Casos](./cases/README.md) para detalles técnicos y de implementación.

## 🏢 Tab de Cuentas - Funcionalidades Implementadas

> 📖 **Documentación completa**: Ver [README de Cuentas](./accounts/README.md) para detalles técnicos y de implementación.

### ✅ **Gestión Completa CRUD**
- **📋 Lista paginada** con infinite scroll
- **➕ Crear casos** con formulario reactivo
- **👁️ Ver detalles** en modal de solo lectura  
- **✏️ Editar casos** con formulario pre-rellenado
- **🗑️ Eliminar casos** con confirmación

### ✅ **Búsqueda y Filtros Avanzados**
- **🔍 Búsqueda por título** con filtro en tiempo real
- **📊 Filtro por estado** (Activo, Resuelto, Cancelado)
- **🔄 Combinación de filtros** múltiples
- **🧹 Limpiar filtros** con un solo click

### ✅ **Interfaz de Usuario Optimizada**
- **📱 Responsive design** para móvil, tablet y desktop
- **♻️ Pull-to-refresh** para recargar la lista
- **📜 Infinite scroll** para paginación automática
- **🎨 Estados visuales** claros (loading, empty, error)
- **🏷️ Badges de estado** con códigos de color
- **📅 Formateo de fechas** legible

### ✅ **Validaciones y UX**
- **✔️ Validación de formularios** en tiempo real
- **🚨 Mensajes de error** descriptivos  
- **🎉 Toasts de éxito** para confirmaciones
- **⚡ Loading states** durante operaciones
- **🔒 Manejo de permisos** y autenticación
- **♿ Accesibilidad mejorada** con manejo de foco y aria-labels
- **🆕 Angular Control Flow** moderno con sintaxis @if/@for

### ✅ **Gestión Completa CRUD de Cuentas**
- **📋 Lista paginada** con infinite scroll automático
- **➕ Crear cuentas** con formulario reactivo y validaciones
- **👁️ Ver detalles** completos en modal de solo lectura  
- **✏️ Editar cuentas** con actualización parcial de campos
- **🗑️ Eliminar cuentas** con confirmación de seguridad

### ✅ **Búsqueda y Filtros de Cuentas**
- **🔍 Búsqueda por nombre** integrada en el header
- **🧹 Limpiar filtros** para ver todas las cuentas
- **📊 Paginación inteligente** de 25 resultados por página

### ✅ **Información de Cuentas**
- **📞 Datos de contacto** - Teléfono, email, sitio web
- **🏢 Información empresarial** - Nombre, número de cuenta
- **📍 Dirección completa** - Calle, ciudad, código postal, país
- **📅 Fechas del sistema** - Creación y última modificación
- **✨ Validación de email** en formularios

## 🎨 Componentes Ionic Utilizados

### Navegación y Layout
- `ion-tabs` - Navegación por pestañas
- `ion-tab-bar` - Barra inferior de tabs
- `ion-tab-button` - Botones de cada tab
- `ion-content` - Container principal con scroll
- `app-header` - Componente de cabecera reutilizable
- `ion-toolbar` - Barras de herramientas adicionales

### Listas y Tarjetas  
- `ion-list` - Listas de elementos
- `ion-card` - Tarjetas para casos individuales
- `ion-item` - Items de lista y formularios
- `ion-avatar` - Avatares e iconografía
- `ion-badge` - Badges de estado

### Formularios y Entradas
- `ion-input` - Campos de texto
- `ion-textarea` - Áreas de texto multilínea  
- `ion-select` - Selectores desplegables
- `ion-searchbar` - Barra de búsqueda
- `ion-checkbox` - Casillas de verificación

### Modales y Overlays
- `ion-modal` - Modales para crear/editar/ver
- `ion-alert` - Alertas de confirmación
- `ion-toast` - Mensajes de feedback
- `ion-loading` - Indicadores de carga

### Navegación y Acciones
- `ion-button` - Botones de acción
- `ion-fab` - Floating Action Button
- `ion-segment` - Segmented controls
- `ion-refresher` - Pull-to-refresh
- `ion-infinite-scroll` - Scroll infinito

## 🔧 Configuración Técnica

### Autenticación
```typescript
// Todos los endpoints requieren JWT token
Authorization: Bearer <token>

// Guard de protección en rutas
canActivate: [AuthGuard]
```

### Servicios Integrados
- **CrmService** - Comunicación con API backend
- **AuthService** - Gestión de autenticación
- **ToastController** - Mensajes de feedback
- **AlertController** - Confirmaciones
- **ModalController** - Gestión de modales

### Modelos TypeScript
```typescript
// Interfaces que coinciden con Pydantic backend
CaseResponse, CaseCreateRequest, CaseUpdateRequest
CasesListResponse, CRMOperationResponse
```

## 📊 Flujo de Datos

### Operaciones CRUD
```
1. Usuario interactúa con UI
   ↓
2. Componente valida entrada  
   ↓
3. CrmService llama al backend
   ↓  
4. Backend procesa con D365
   ↓
5. Respuesta actualiza la UI
   ↓
6. Toast confirma la operación
```

### Paginación Inteligente
```
1. Carga inicial: 25 casos
   ↓
2. Usuario hace scroll down
   ↓
3. Detecta proximidad al final
   ↓
4. Carga automática de más casos
   ↓
5. Agrega a la lista existente
```

## 🎯 Casos de Uso Empresariales

### 👩‍💼 **Agente de Soporte**
- Crear casos desde reportes de clientes
- Actualizar estado y prioridad  
- Buscar historial por cliente
- Resolver y cerrar casos

### 👨‍💻 **Administrador CRM**
- Monitorear casos abiertos
- Filtrar por estados críticos
- Revisar métricas de tiempo
- Gestionar asignaciones

### 📱 **Usuario Móvil**
- Acceso completo desde móvil
- Crear casos en campo
- Actualización offline (futuro)
- Push notifications (futuro)

## 🚀 Próximas Funcionalidades

### 🏢 **Tab de Cuentas** (Mejoras futuras)
- Filtros por industria y tamaño
- Filtros por ciudad y país
- Vinculación con casos
- Vista de relaciones con contactos
- Ordenamiento personalizado

### 👤 **Tab de Contactos** (En desarrollo)  
- CRUD completo para personas
- Búsqueda por nombre y email
- Vinculación con cuentas
- Historial de interacciones

### 🔧 **Tab de Sistema** (En desarrollo)
- Health check de conectividad
- Diagnóstico completo de configuración  
- Información de tokens y permisos
- Limpieza de caché
- Estadísticas de uso

### 🎨 **Mejoras de UX**
- Componentes reutilizables de filtros
- Paginación avanzada con saltos
- Exportación de datos
- Modo oscuro/claro  
- Configuración personalizable

### ⚡ **Optimizaciones Técnicas Implementadas**
- **CSS Budget optimizado** - Uso de componentes nativos de Ionic
- **Control Flow moderno** - Migración de *ngIf a @if para mejor rendimiento
- **Lifecycle hooks** - Manejo correcto de ionViewWillLeave para accesibilidad
- **Bundle size reducido** - Eliminación de CSS personalizado innecesario

## 📋 Estado de Implementación

| Funcionalidad | Estado | Progreso |
|--------------|--------|----------|
| **Tab de Casos** | ✅ Completo | 100% |
| **Tab de Cuentas** | ✅ Completo | 100% |  
| Tab de Contactos | 🟡 En desarrollo | 20% |
| Tab de Sistema | 🟡 En desarrollo | 30% |
| Componentes reutilizables | 🔴 Pendiente | 0% |
| Tests E2E | 🔴 Pendiente | 0% |

## 💡 Consejos de Uso

### **Para Desarrolladores**
- Todos los componentes son standalone
- Usar `CrmService` para operaciones API
- Seguir patrones de validación existentes  
- Mantener coherencia visual con Ionic

### **Para Usuarios Finales**
- **Pull hacia abajo** para recargar
- **Scroll hasta abajo** para más resultados
- **Tap prolongado** para opciones (futuro)
- **Buscar por fragmentos** de texto

## 🔗 Enlaces Relacionados

### Documentación por Página
- [📋 Casos (Cases)](./cases/README.md) - Documentación completa del tab de casos
- [🏢 Cuentas (Accounts)](./accounts/README.md) - Documentación completa del tab de cuentas
- 👤 Contactos (Contacts) - En desarrollo
- 🔧 Sistema (System) - En desarrollo

### Backend y Servicios
- [Documentación Backend CRM](../../../app/api/crm/README.md)
- [Modelos TypeScript](../shared/models/crm.models.ts)
- [Servicio CRM](../shared/services/crm.service.ts)
- [Documentación principal](../../../README.md)

---

📧 **Soporte**: Para dudas sobre la interfaz CRM, contacta al equipo de desarrollo.  
🔧 **Desarrollo**: Esta página está en activo desarrollo. Nuevas funcionalidades se añaden regularmente.
