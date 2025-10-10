# Página de Casos - CRM

Documentación de la página de **Casos (Incidents)** del módulo CRM de ezekl-budget.

## 🌟 Resumen

Esta página permite la gestión completa de casos de soporte de Dynamics 365 CRM con funcionalidad CRUD, búsqueda avanzada, filtros y paginación inteligente.

## ✅ Funcionalidades Implementadas

### 📋 **Gestión CRUD Completa**
- **Listar casos** - Lista paginada con infinite scroll automático
- **Crear casos** - Formulario reactivo con validaciones
- **Ver detalles** - Modal de solo lectura con información completa
- **Editar casos** - Actualización parcial de campos
- **Eliminar casos** - Confirmación antes de eliminar

### 🔍 **Búsqueda y Filtros**
- **Búsqueda por título** - Integrada en el header con filtro en tiempo real
- **Filtro por estado** - Todos, Activo, Resuelto, Cancelado
- **Combinación de filtros** - Búsqueda + estado simultáneamente
- **Limpiar filtros** - Botón para resetear todos los filtros

### 🎨 **Interfaz y UX**
- **Pull-to-refresh** - Deslizar hacia abajo para recargar
- **Infinite scroll** - Carga automática de más casos al hacer scroll
- **Skeleton screens** - Loading elegante con placeholders animados
- **Estados visuales** - Loading, empty state, error state
- **Badges de estado** - Colores distintivos (Activo=azul, Resuelto=verde, Cancelado=gris)
- **Badges de prioridad** - Alta=rojo, Normal=naranja, Baja=verde
- **Formato de fechas** - Legible en español (ej: "9 oct 2025, 10:30")
- **FAB** - Floating Action Button para crear casos rápidamente

### ✏️ **Formularios**
- **Validación en tiempo real** - Feedback inmediato en campos
- **Campos requeridos** - Título (5-160 caracteres)
- **Campos opcionales** - Descripción, tipo, prioridad, origen
- **Selección de cliente** - Buscar y asociar cuenta o contacto
- **Valores por defecto** - Prioridad Normal, Origen Web

### 🔗 **Integración con CRM**
- **Búsqueda de cuentas** - Modal para seleccionar empresa cliente
- **Búsqueda de contactos** - Modal para seleccionar persona cliente
- **Validación exclusiva** - Solo cuenta O contacto, no ambos
- **Sincronización D365** - Todos los cambios se reflejan en Dynamics 365

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
ion-card            // Tarjetas para cada caso
ion-list            // Lista de casos
ion-chip            // Badges de estado y prioridad
ion-skeleton-text   // Loading placeholders
```

### Modales
```typescript
ion-modal           // Crear, editar, ver detalles
app-crm-search      // Búsqueda de cuentas/contactos
ion-alert           // Confirmación de eliminación
```

### Formularios
```typescript
ion-input           // Campos de texto
ion-textarea        // Descripción multilínea
ion-select          // Selectores (estado, prioridad, tipo, origen)
```

## 🔧 Configuración Técnica

### Formularios Reactivos

**Formulario de Creación:**
```typescript
createForm = {
  title: string (requerido, 5-160 chars)
  description: string (opcional)
  casetypecode: number (opcional)
  customer_account_id: string (opcional, excluyente con contact)
  customer_contact_id: string (opcional, excluyente con account)
  prioritycode: number (default: Normal)
  caseorigincode: number (default: Web)
}
```

**Formulario de Edición:**
```typescript
editForm = {
  title: string (requerido, 5-160 chars)
  description: string (opcional)
  casetypecode: number (opcional)
  statuscode: number (opcional)
  prioritycode: number (opcional)
}
```

### Paginación
- **Página inicial**: 25 casos
- **Tamaño de página**: 25 casos por carga
- **Scroll automático**: Cuando se acerca al final de la lista
- **Indicador visual**: "Cargando más casos..." mientras carga

### Búsqueda y Filtros
```typescript
// Búsqueda por título (OData contains)
filter_query = "contains(title,'texto búsqueda')"

// Filtro por estado (OData eq)
filter_query = "statuscode eq 1"

// Combinación (OData and)
filter_query = "contains(title,'texto') and statuscode eq 1"
```

## 📊 Flujo de Operaciones

### Crear Caso
```
1. Usuario click en FAB (+)
   ↓
2. Se abre modal con formulario
   ↓
3. Usuario completa campos requeridos
   ↓
4. (Opcional) Busca y selecciona cuenta/contacto
   ↓
5. Click en "Crear Caso"
   ↓
6. Validación de formulario
   ↓
7. POST al backend → Dynamics 365
   ↓
8. Toast de éxito + recarga lista
   ↓
9. Modal se cierra automáticamente
```

### Ver Detalles
```
1. Usuario click en botón "Ver" (ojo)
   ↓
2. Se abre modal de solo lectura
   ↓
3. Muestra todos los campos del caso
   ↓
4. Usuario revisa información
   ↓
5. Click en X o fuera del modal para cerrar
```

### Editar Caso
```
1. Usuario click en botón "Editar" (lápiz)
   ↓
2. Modal se abre con formulario pre-rellenado
   ↓
3. Usuario modifica campos deseados
   ↓
4. Click en "Actualizar Caso"
   ↓
5. PATCH al backend → Dynamics 365
   ↓
6. Toast de éxito + actualiza lista
   ↓
7. Modal se cierra
```

### Eliminar Caso
```
1. Usuario click en botón "Eliminar" (basura)
   ↓
2. Alert de confirmación aparece
   ↓
3. Usuario confirma eliminación
   ↓
4. DELETE al backend → Dynamics 365
   ↓
5. Toast de éxito + remueve de lista
   ↓
6. Alert se cierra
```

## 🎨 Estados Visuales

### Loading Inicial
- **5 skeleton cards** animados con placeholders
- Se muestra mientras carga la primera página
- Desaparece cuando llegan los datos

### Empty State
- **Icono** de documento vacío
- **Mensaje**: "No hay casos"
- **Descripción**: Explica que no hay resultados con los filtros actuales
- **Acción**: Botón "Limpiar Filtros"

### Loading More
- **Spinner** al final de la lista
- **Texto**: "Cargando más casos..."
- Se activa automáticamente al hacer scroll

### Refresh
- **Indicador nativo** de pull-to-refresh
- **Texto**: "Desliza para actualizar" / "Actualizando casos..."
- Recarga toda la lista desde cero

## 🏷️ Badges y Colores

### Estados del Caso
| Estado | Color | statuscode |
|--------|-------|------------|
| Activo | `primary` (azul) | 1 |
| Resuelto | `success` (verde) | 5 |
| Cancelado | `medium` (gris) | 6 |

### Prioridades
| Prioridad | Color | prioritycode |
|-----------|-------|--------------|
| Alta | `danger` (rojo) | 1 |
| Normal | `warning` (naranja) | 2 |
| Baja | `success` (verde) | 3 |

## 🔒 Seguridad y Permisos

- **Autenticación requerida**: Todos los endpoints requieren JWT token
- **Guard en ruta**: `canActivate: [AuthGuard]`
- **Manejo de errores**: Toasts descriptivos para errores de API
- **Validación frontend**: Formularios reactivos con validadores
- **Validación backend**: API valida datos antes de enviar a D365

## ♿ Accesibilidad

- **Manejo de foco**: `ionViewWillLeave()` limpia focus al salir
- **Aria labels**: Elementos interactivos con etiquetas descriptivas
- **Keyboard navigation**: Modales y formularios navegables con teclado
- **Touch targets**: Botones con tamaño mínimo para touch
- **Contraste**: Colores cumplen WCAG AA

## 🧪 Testing

La página incluye **24 tests unitarios** que cubren:
- ✅ Creación del componente
- ✅ Carga inicial de casos
- ✅ Renderizado de datos en template
- ✅ Estados de loading y empty
- ✅ Validación de formularios
- ✅ Operaciones CRUD
- ✅ Filtros y búsqueda
- ✅ Manejo de errores
- ✅ Formateo de datos
- ✅ Paginación y refresh

**Ejecutar tests:**
```bash
npm test -- --include='**/cases.page.spec.ts'
```

## 📱 Responsive Design

### Desktop (> 768px)
- Campos de formulario en 2 columnas
- Cards más anchas con mejor espaciado
- Modal de tamaño mediano centrado

### Tablet (576px - 768px)
- Campos de formulario en 1-2 columnas mixtas
- Cards de ancho completo
- Modal ocupa 80% del ancho

### Mobile (< 576px)
- Todos los campos en 1 columna
- Cards de ancho completo con padding reducido
- Modal de ancho completo
- FAB optimizado para touch

## 🚀 Próximas Mejoras

### Funcionalidad
- [ ] Asignación de casos a usuarios
- [ ] Adjuntar archivos a casos
- [ ] Comentarios y notas en casos
- [ ] Historial de cambios
- [ ] Exportar casos a PDF/Excel

### UX
- [ ] Búsqueda avanzada con múltiples campos
- [ ] Filtros guardados/favoritos
- [ ] Vista de kanban por estado
- [ ] Notificaciones push para casos críticos
- [ ] Modo offline con sincronización

### Performance
- [ ] Virtual scrolling para listas muy grandes
- [ ] Cache de datos en IndexedDB
- [ ] Lazy loading de imágenes
- [ ] Prefetch de siguiente página

## 🔗 Enlaces Relacionados

- [README principal CRM](../README.md)
- [Servicio CRM](../../shared/services/crm.service.ts)
- [Modelos TypeScript](../../shared/models/crm.models.ts)
- [Backend API](../../../../app/api/crm/cases.py)

---

📧 **Soporte**: Para dudas sobre esta página, contacta al equipo de desarrollo.
