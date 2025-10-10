# Página de Contactos - CRM

Documentación de la página de **Contactos (Contacts)** del módulo CRM de ezekl-budget.

## 🌟 Resumen

Esta página permite la gestión completa de contactos empresariales de Dynamics 365 CRM con funcionalidad CRUD, búsqueda avanzada, filtros y paginación inteligente.

## ✅ Funcionalidades Implementadas

### 📋 **Gestión CRUD Completa**
- **Listar contactos** - Lista paginada con infinite scroll automático
- **Crear contactos** - Formulario reactivo con validaciones
- **Ver detalles** - Modal de solo lectura con información completa
- **Editar contactos** - Actualización parcial de campos
- **Eliminar contactos** - Confirmación antes de eliminar

### 🔍 **Búsqueda y Filtros**
- **Búsqueda por nombre** - Integrada en el header con filtro en tiempo real
- **Limpiar filtros** - Botón para resetear todos los filtros

### 🎨 **Interfaz y UX**
- **Pull-to-refresh** - Deslizar hacia abajo para recargar
- **Infinite scroll** - Carga automática de más contactos al hacer scroll
- **Skeleton screens** - Loading elegante con placeholders animados
- **Estados visuales** - Loading, empty state, error state
- **Formato de fechas** - Legible en español (ej: "9 oct 2025, 10:30")
- **FAB** - Floating Action Button para crear contactos rápidamente

### ✏️ **Formularios**
- **Validación en tiempo real** - Feedback inmediato en campos
- **Campos requeridos** - Nombre (1-50 caracteres), Apellido (1-50 caracteres)
- **Campos opcionales** - Puesto de trabajo, teléfono, móvil, email, dirección completa
- **Validación de email** - Formato válido requerido
- **Valores por defecto** - Campos vacíos para libertad de entrada

### 🔗 **Integración con CRM**
- **Sincronización D365** - Todos los cambios se reflejan en Dynamics 365
- **Datos de contacto** - Teléfono, móvil, email
- **Información profesional** - Puesto de trabajo
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
ion-card            // Tarjetas para cada contacto
ion-list            // Lista de contactos
ion-skeleton-text   // Loading placeholders
ion-note            // Puesto de trabajo
ion-icon            // Iconos (call, mail, phone-portrait, location)
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
FormGroup           // Formularios reactivos de Angular
Validators          // Validaciones (required, email, minLength, maxLength)
```

## 🔧 Configuración Técnica

### Formularios Reactivos

**Formulario de Creación:**
```typescript
createForm = {
  firstname: string (requerido, 1-50 chars)
  lastname: string (requerido, 1-50 chars)
  jobtitle: string (opcional)
  telephone1: string (opcional)
  mobilephone: string (opcional)
  emailaddress1: string (opcional, formato email)
  address1_line1: string (opcional)
  address1_city: string (opcional)
  address1_postalcode: string (opcional)
  address1_country: string (opcional)
}
```

**Formulario de Edición:**
```typescript
editForm = {
  firstname: string (requerido, 1-50 chars)
  lastname: string (requerido, 1-50 chars)
  jobtitle: string (opcional)
  telephone1: string (opcional)
  mobilephone: string (opcional)
  emailaddress1: string (opcional, formato email)
  address1_line1: string (opcional)
  address1_city: string (opcional)
  address1_postalcode: string (opcional)
  address1_country: string (opcional)
}
```

### Paginación
- **Método**: Server-driven paging con `@odata.nextLink` (Dynamics 365)
- **Página inicial**: 25 contactos
- **Tamaño de página**: 25 contactos por carga
- **Scroll automático**: Infinite scroll cuando se acerca al final
- **Indicador visual**: "Cargando más contactos..." mientras carga
- **Ordenamiento**: Por `contactid` (primary key) para resultados determinísticos
- **Manejo de nextLink**: Soporte automático para URLs absolutas y relativas

#### ⚠️ Importante: nextLink puede venir en dos formatos

**Formato 1 - URL Relativa:**
```
/api/data/v9.2/contacts?$select=contactid,fullname&$skiptoken=<cookie>
```

**Formato 2 - URL Absoluta:**
```
https://orgname.crm.dynamics.com/api/data/v9.2/contacts?$select=contactid,fullname&$skiptoken=<cookie>
```

El backend maneja **ambos formatos automáticamente**, parseando URLs absolutas y extrayendo solo el path y query necesarios.

### Búsqueda
- **Campo de búsqueda**: En el header de la página
- **Búsqueda en tiempo real**: Filtra mientras escribes
- **Campo de búsqueda**: `fullname` (nombre completo del contacto)
- **Operador**: `contains` - búsqueda parcial case-insensitive

## 🚀 Arquitectura

### Servicios
```typescript
CrmService
  ├─ getContacts(params)              // Lista paginada
  ├─ getContactsByNextLink(nextLink)  // Siguiente página
  ├─ getContact(id)                   // Un contacto
  ├─ createContact(data)              // Crear
  ├─ updateContact(id, data)          // Actualizar
  └─ deleteContact(id)                // Eliminar
```

### Modelos
```typescript
ContactResponse {
  contactid: string
  fullname: string
  firstname: string
  lastname: string
  jobtitle?: string
  telephone1?: string
  mobilephone?: string
  emailaddress1?: string
  address1_line1?: string
  address1_city?: string
  address1_postalcode?: string
  address1_country?: string
  createdon?: string
  modifiedon?: string
}

ContactsListResponse {
  count: number
  contacts: ContactResponse[]
  next_link?: string
}

ContactCreateRequest {
  firstname: string
  lastname: string
  jobtitle?: string
  telephone1?: string
  mobilephone?: string
  emailaddress1?: string
  address1_line1?: string
  address1_city?: string
  address1_postalcode?: string
  address1_country?: string
}

ContactUpdateRequest {
  firstname?: string
  lastname?: string
  jobtitle?: string
  telephone1?: string
  mobilephone?: string
  emailaddress1?: string
  address1_line1?: string
  address1_city?: string
  address1_postalcode?: string
  address1_country?: string
}
```

## 📊 Backend Endpoints

### GET `/api/crm/contacts`
Obtiene lista paginada de contactos.

**Query Parameters:**
- `top` (default: 25) - Cantidad de registros
- `filter_query` - Filtro OData
- `order_by` - Campo de ordenamiento
- `select_fields` - Campos a retornar

**Response:**
```json
{
  "count": 25,
  "contacts": [...],
  "next_link": "/api/data/v9.2/contacts?$skiptoken=..."
}
```

### GET `/api/crm/contacts/by-nextlink`
Obtiene siguiente página usando nextLink de D365.

**Query Parameters:**
- `next_link` (required) - URL del @odata.nextLink (puede ser absoluta o relativa)

**Ejemplo de Request:**
```bash
# nextLink relativo
GET /api/crm/contacts/by-nextlink?next_link=%2Fapi%2Fdata%2Fv9.2%2Fcontacts%3F%24skiptoken%3D...

# nextLink absoluto (también soportado)
GET /api/crm/contacts/by-nextlink?next_link=https%3A%2F%2Forg.crm.dynamics.com%2Fapi%2Fdata%2Fv9.2%2Fcontacts%3F%24skiptoken%3D...
```

**Response:**
```json
{
  "count": 25,
  "contacts": [...],
  "next_link": "/api/data/v9.2/contacts?$skiptoken=..."  // null si es última página
}
```

### GET `/api/crm/contacts/{contact_id}`
Obtiene un contacto específico.

### POST `/api/crm/contacts`
Crea un nuevo contacto.

### PATCH `/api/crm/contacts/{contact_id}`
Actualiza un contacto existente.

### DELETE `/api/crm/contacts/{contact_id}`
Elimina un contacto.

## 🎯 Flujo de Usuario

### Crear Contacto
1. Click en botón flotante (+)
2. Llenar formulario (nombre y apellido requeridos)
3. Guardar → Notificación de éxito → Lista actualizada

### Editar Contacto
1. Click en "Editar" en tarjeta de contacto
2. Modificar campos deseados
3. Guardar → Notificación de éxito → Lista actualizada

### Eliminar Contacto
1. Click en "Eliminar" en tarjeta de contacto
2. Confirmar eliminación en alert
3. Confirmar → Notificación de éxito → Lista actualizada

### Búsqueda
1. Click en ícono de búsqueda en header
2. Escribir nombre del contacto
3. Resultados filtrados en tiempo real

## 📝 Notas Técnicas

### Server-Driven Paging
Dynamics 365 NO soporta `$skip` estándar de OData. En su lugar:
- Usa `$skiptoken` con cookies de paginación
- El `@odata.nextLink` contiene el token correcto
- **NO modificar** el nextLink
- Usar exactamente como viene del servidor
- El backend automáticamente maneja URLs absolutas y relativas

#### Implementación Frontend
```typescript
// contacts.page.ts

// 1. Cargar primera página
async loadContacts() {
  this.contacts = [];
  this.nextLink = null;
  this.isLoading = true;

  try {
    const params = {
      top: 25,
      order_by: 'contactid',  // Ordenamiento determinístico
      filter_query: this.searchQuery 
        ? `contains(fullname,'${this.searchQuery}')` 
        : undefined
    };

    const response = await this.crmService.getContacts(params);
    this.contacts = response.contacts;
    this.nextLink = response.next_link;  // Puede ser absoluta o relativa
    
  } catch (error) {
    console.error('Error al cargar contactos:', error);
  } finally {
    this.isLoading = false;
  }
}

// 2. Cargar siguiente página (infinite scroll)
async onLoadMore(event: any) {
  if (!this.nextLink) {
    event.target.complete();
    event.target.disabled = true;
    return;
  }

  try {
    // Encodear nextLink completo (absoluto o relativo)
    const encodedNextLink = encodeURIComponent(this.nextLink);
    const response = await this.crmService.getContactsByNextLink(encodedNextLink);
    
    this.contacts.push(...response.contacts);
    this.nextLink = response.next_link;  // Actualizar para próxima iteración
    
    if (!this.nextLink) {
      event.target.disabled = true;  // Última página alcanzada
    }
  } catch (error) {
    console.error('Error al cargar más contactos:', error);
  } finally {
    event.target.complete();
  }
}
```

#### Implementación CrmService
```typescript
// crm.service.ts

getContactsByNextLink(nextLink: string): Promise<ContactsListResponse> {
  // Enviar nextLink encodificado al backend
  // El backend parseará URLs absolutas automáticamente
  return this.http.get<ContactsListResponse>(
    `${this.apiUrl}/contacts/by-nextlink?next_link=${nextLink}`
  ).toPromise();
}
```

#### ⚠️ Errores Comunes

**Error: "next_link": null en primera página**
- **Causa**: Usar `$skip` en lugar de `Prefer: odata.maxpagesize`
- **Solución**: Backend debe usar header `Prefer: odata.maxpagesize=25`

**Error: "Resource not found for the segment 'https:'"**
- **Causa**: Concatenar URL absoluta con base_url sin parsear
- **Solución**: Backend parsea URLs con `urllib.parse.urlparse()`

Ver: `D365_PAGINATION_GUIDE.md` para más detalles técnicos

### Ordenamiento Determinístico
Siempre ordenar por `contactid` para:
- Evitar duplicados entre páginas
- Resultados consistentes
- Mejor rendimiento en D365
- Paginación estable y predecible

### Validaciones de Formulario
- **Nombre**: Requerido, 1-50 caracteres
- **Apellido**: Requerido, 1-50 caracteres
- **Email**: Formato válido si se proporciona
- **Otros campos**: Opcionales, sin validación de formato

## 🔮 Mejoras Futuras

- [ ] Filtros avanzados por puesto de trabajo
- [ ] Búsqueda por email/teléfono
- [ ] Exportar lista a Excel
- [ ] Asociar contactos con cuentas
- [ ] Vista de tarjetas vs lista
- [ ] Campos personalizados de D365
- [ ] Ordenamiento por diferentes campos
- [ ] Filtro por fecha de creación

## 📚 Referencias

- [Dynamics 365 Web API Docs](https://docs.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview)
- [OData V4 Specification](https://www.odata.org/documentation/)
- [Ionic Angular Components](https://ionicframework.com/docs/components)
- [Angular Reactive Forms](https://angular.io/guide/reactive-forms)

---

**Última actualización**: 10 de octubre de 2025  
**Estado**: Completamente funcional ✅  
**Mantenedor**: Equipo de Desarrollo ezekl-budget
