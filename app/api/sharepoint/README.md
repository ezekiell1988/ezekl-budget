# Integración SharePoint Online - API ezekl-budget

Este documento describe la integración completa del sistema **ezekl-budget** con **Microsoft SharePoint Online** a través de **Microsoft Graph API**, proporcionando gestión de sitios, listas, bibliotecas de documentos y búsqueda de contenido.

## 🌟 Resumen Ejecutivo

La integración SharePoint permite al sistema ezekl-budget conectarse directamente con SharePoint Online para:
- **Gestionar sitios de SharePoint** con acceso a información y metadatos
- **Administrar listas de SharePoint** con operaciones CRUD completas
- **Gestionar bibliotecas de documentos** con subida, descarga y eliminación de archivos
- **Buscar contenido** en sitios, listas y documentos
- **Automatizar workflows** de gestión documental

## 📋 Funcionalidades Implementadas

### ✅ Entidades SharePoint Soportadas
- **Sitios (Sites)** - Gestión de sitios de SharePoint
- **Listas (Lists)** - Listas de SharePoint con elementos
- **Drives (Bibliotecas de documentos)** - Gestión de archivos y carpetas
- **Búsqueda** - Búsqueda de contenido global o por sitio

### ✅ Operaciones CRUD Completas
- **Create** - Crear nuevos elementos de lista y subir archivos
- **Read** - Consultas con filtros OData y paginación
- **Update** - Actualización parcial (PATCH) de elementos
- **Delete** - Eliminación de elementos y archivos

### ✅ Características Avanzadas
- **Autenticación Azure AD** con client credentials flow
- **Microsoft Graph API v1.0** para acceso a SharePoint
- **Caché inteligente de tokens** con renovación automática
- **Filtros OData** para búsquedas avanzadas
- **Paginación configurable** para listas grandes
- **Upload/Download de archivos** con soporte para grandes archivos
- **Logging detallado** para auditoría y debugging

## 🏗️ Arquitectura de la Integración

```
app/
├── models/
│   └── sharepoint.py              # Modelos Pydantic para SharePoint
├── services/
│   ├── sharepoint_auth.py         # Servicio de autenticación
│   └── sharepoint_service.py      # Servicio principal SharePoint
└── api/sharepoint/
    ├── __init__.py                # Exportaciones del módulo
    └── demo.py                    # Endpoints de SharePoint
```

## 🔧 Configuración

### Variables de Entorno Requeridas

```env
# Configuración de Azure AD (compartida con CRM)
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_CLIENT_ID=your-azure-app-client-id  
AZURE_CLIENT_SECRET=your-azure-app-secret

# Configuración opcional de SharePoint
SHAREPOINT_SITE_URL=https://yourorg.sharepoint.com/sites/your-site
SHAREPOINT_SITE_ID=site-guid-if-known
```

### Azure AD App Registration

Para configurar la autenticación, necesitas:

1. **Crear App Registration en Azure AD** (puede ser la misma que para CRM)
2. **Configurar permisos API para Microsoft Graph:**
   - `Sites.Read.All` - Leer sitios
   - `Sites.ReadWrite.All` - Leer y escribir sitios
   - `Files.Read.All` - Leer archivos
   - `Files.ReadWrite.All` - Leer y escribir archivos
3. **Otorgar consentimiento de administrador** para los permisos
4. **Generar client secret**
5. **Configurar las variables de entorno**

## 📝 Uso de los Endpoints

### Health Check

```bash
# Verificar estado del servicio
GET /api/sharepoint/health

# Respuesta:
{
  "status": "healthy",
  "auth_configured": true,
  "token_valid": true,
  "root_site_accessible": true,
  "root_site_name": "IT Quest Solutions"
}
```

### Sitios (Sites)

```bash
# Listar sitios accesibles
GET /api/sharepoint/sites

# Buscar sitios por término
GET /api/sharepoint/sites?search=team

# Obtener sitio raíz
GET /api/sharepoint/sites/root

# Obtener sitio por ID
GET /api/sharepoint/sites/{site_id}
```

### Listas (Lists)

```bash
# Listar todas las listas de un sitio
GET /api/sharepoint/sites/{site_id}/lists

# Obtener lista específica
GET /api/sharepoint/sites/{site_id}/lists/{list_id}

# Listar elementos de una lista con paginación
GET /api/sharepoint/sites/{site_id}/lists/{list_id}/items?top=100&skip=0

# Filtrar elementos de lista
GET /api/sharepoint/sites/{site_id}/lists/{list_id}/items?filter_query=fields/Status eq 'Active'

# Crear nuevo elemento de lista
POST /api/sharepoint/sites/{site_id}/lists/{list_id}/items
{
  "fields": {
    "Title": "Nuevo elemento",
    "Description": "Descripción del elemento",
    "Status": "Active"
  }
}

# Actualizar elemento de lista
PATCH /api/sharepoint/sites/{site_id}/lists/{list_id}/items/{item_id}
{
  "fields": {
    "Status": "Completed"
  }
}

# Eliminar elemento de lista
DELETE /api/sharepoint/sites/{site_id}/lists/{list_id}/items/{item_id}
```

### Bibliotecas de Documentos (Drives)

```bash
# Listar bibliotecas de documentos de un sitio
GET /api/sharepoint/sites/{site_id}/drives

# Listar elementos de la raíz de una biblioteca
GET /api/sharepoint/sites/{site_id}/drives/{drive_id}/items

# Listar elementos de una carpeta específica
GET /api/sharepoint/sites/{site_id}/drives/{drive_id}/items?folder_path=Documentos/2025

# Subir archivo a la raíz
POST /api/sharepoint/sites/{site_id}/drives/{drive_id}/upload
Content-Type: multipart/form-data
file: [archivo binario]

# Subir archivo a una carpeta
POST /api/sharepoint/sites/{site_id}/drives/{drive_id}/upload?folder_path=Documentos/2025
Content-Type: multipart/form-data
file: [archivo binario]

# Descargar archivo
GET /api/sharepoint/sites/{site_id}/drives/{drive_id}/items/{item_id}/download

# Eliminar archivo
DELETE /api/sharepoint/sites/{site_id}/drives/{drive_id}/items/{item_id}
```

### Búsqueda

```bash
# Buscar en todos los sitios
GET /api/sharepoint/search?query=presupuesto

# Buscar en un sitio específico
GET /api/sharepoint/search?query=factura&site_id={site_id}
```

## 🔍 Filtros OData Soportados

### Operadores Básicos para Listas
- `eq` - Igual que: `fields/Status eq 'Active'`
- `ne` - No igual: `fields/Priority ne 1`
- `gt` - Mayor que: `fields/Amount gt 1000`
- `lt` - Menor que: `fields/DueDate lt 2025-12-31`
- `and` - Y lógico: `fields/Status eq 'Active' and fields/Priority eq 1`
- `or` - O lógico: `fields/Type eq 'A' or fields/Type eq 'B'`

### Ejemplos de Filtros Comunes

```bash
# Elementos activos
?filter_query=fields/Status eq 'Active'

# Elementos con prioridad alta
?filter_query=fields/Priority eq 1

# Elementos creados después de fecha
?filter_query=fields/Created gt 2025-01-01T00:00:00Z

# Combinación de filtros
?filter_query=fields/Status eq 'Active' and fields/Priority ge 2
```

## 📄 Paginación

### Paginación Estándar
Microsoft Graph API soporta paginación estándar con `$top` y `$skip`:

```bash
# Primera página (25 elementos)
GET /api/sharepoint/sites/{site_id}/lists/{list_id}/items?top=25&skip=0

# Segunda página (25 elementos)
GET /api/sharepoint/sites/{site_id}/lists/{list_id}/items?top=25&skip=25

# Tercera página (25 elementos)
GET /api/sharepoint/sites/{site_id}/lists/{list_id}/items?top=25&skip=50
```

### Paginación con nextLink
Para listas muy grandes, Graph API retorna un `@odata.nextLink`:

```json
{
  "value": [...],
  "count": 25,
  "@odata.nextLink": "https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items?$skiptoken=..."
}
```

## 🏥 Diagnósticos y Health Check

### Health Check
```bash
GET /api/sharepoint/health
```

Verifica:
- ✅ Configuración de autenticación
- ✅ Validez del token de acceso
- ✅ Conectividad con SharePoint Online
- ✅ Acceso al sitio raíz

## 🔒 Seguridad

### Autenticación de Endpoints
Todos los endpoints SharePoint requieren autenticación:
```bash
Authorization: Bearer {jwt_token}
```

### Autenticación con SharePoint Online
El servicio usa **OAuth2 Client Credentials Flow**:

1. **Aplicación se autentica** con Azure AD usando client_id y client_secret
2. **Azure AD retorna access token** válido para Microsoft Graph API
3. **Token se usa** para llamadas a Graph API
4. **Token se cachea** en memoria hasta 5 minutos antes de expirar
5. **Token se renueva** automáticamente cuando expira

## 📚 Recursos Adicionales

### Microsoft Graph API
- [Microsoft Graph API Reference](https://learn.microsoft.com/en-us/graph/api/overview)
- [SharePoint Sites API](https://learn.microsoft.com/en-us/graph/api/resources/sharepoint)
- [Working with Lists](https://learn.microsoft.com/en-us/graph/api/resources/list)
- [Working with Files](https://learn.microsoft.com/en-us/graph/api/resources/driveitem)

### Permisos Requeridos
| Operación | Permiso Mínimo | Permiso Recomendado |
|-----------|----------------|---------------------|
| Leer sitios | Sites.Read.All | Sites.Read.All |
| Escribir sitios | Sites.ReadWrite.All | Sites.ReadWrite.All |
| Leer archivos | Files.Read.All | Files.Read.All |
| Escribir archivos | Files.ReadWrite.All | Files.ReadWrite.All |

## 🐛 Troubleshooting

### Error: "Insufficient privileges to complete the operation"
**Causa:** La aplicación no tiene los permisos necesarios configurados en Azure AD.

**Solución:**
1. Ir a Azure Portal → App Registrations
2. Seleccionar la aplicación
3. API permissions → Add permission → Microsoft Graph
4. Agregar permisos necesarios (Sites.ReadWrite.All, Files.ReadWrite.All)
5. Grant admin consent

### Error: "Resource not found"
**Causa:** El site_id o list_id no existe o no es accesible.

**Solución:**
1. Verificar el ID del sitio con `GET /api/sharepoint/sites`
2. Verificar el ID de la lista con `GET /api/sharepoint/sites/{site_id}/lists`
3. Asegurarse que la aplicación tiene permisos al sitio

### Error: "Invalid authentication token"
**Causa:** El token ha expirado o es inválido.

**Solución:**
El servicio maneja automáticamente la renovación de tokens. Si persiste:
1. Verificar que AZURE_CLIENT_ID, AZURE_CLIENT_SECRET y AZURE_TENANT_ID están correctos
2. Verificar conectividad con Azure AD
3. Limpiar caché de token (reiniciar servicio)

## 🎯 Ejemplos de Uso

### Ejemplo 1: Subir archivo a SharePoint
```python
import httpx

# 1. Obtener site_id
response = httpx.get("http://localhost:8001/api/sharepoint/sites/root", headers=headers)
site_id = response.json()["id"]

# 2. Obtener drive_id
response = httpx.get(f"http://localhost:8001/api/sharepoint/sites/{site_id}/drives", headers=headers)
drive_id = response.json()["value"][0]["id"]

# 3. Subir archivo
files = {"file": ("reporte.pdf", open("reporte.pdf", "rb"), "application/pdf")}
response = httpx.post(
    f"http://localhost:8001/api/sharepoint/sites/{site_id}/drives/{drive_id}/upload",
    headers=headers,
    files=files,
    params={"folder_path": "Reportes/2025"}
)
```

### Ejemplo 2: Buscar documentos
```python
# Buscar documentos con el término "presupuesto"
response = httpx.get(
    "http://localhost:8001/api/sharepoint/search",
    headers=headers,
    params={"query": "presupuesto"}
)

results = response.json()
print(f"Encontrados {results['total']} resultados")
```

### Ejemplo 3: Gestionar elementos de lista
```python
# Crear elemento
response = httpx.post(
    f"http://localhost:8001/api/sharepoint/sites/{site_id}/lists/{list_id}/items",
    headers=headers,
    json={
        "fields": {
            "Title": "Nueva tarea",
            "Status": "Pendiente",
            "Priority": 1
        }
    }
)

item_id = response.json()["data"]["id"]

# Actualizar elemento
response = httpx.patch(
    f"http://localhost:8001/api/sharepoint/sites/{site_id}/lists/{list_id}/items/{item_id}",
    headers=headers,
    json={
        "fields": {
            "Status": "Completado"
        }
    }
)
```

## 🚀 Próximos Pasos

1. Implementar frontend en Ionic para visualizar y gestionar SharePoint
2. Agregar soporte para permisos granulares por sitio/lista
3. Implementar webhooks para notificaciones de cambios
4. Agregar soporte para versiones de documentos
5. Implementar compartición de archivos y enlaces
6. Agregar soporte para metadatos personalizados
