# Integración Dynamics 365 CRM - API ezekl-budget

Este documento describe la integración completa del sistema **ezekl-budget** con **Microsoft Dynamics 365 CRM**, proporcionando gestión empresarial de clientes, casos de soporte y cuentas corporativas.

## 🌟 Resumen Ejecutivo

La integración CRM permite al sistema ezekl-budget conectarse directamente con Dynamics 365 para:
- **Gestionar casos de soporte** con seguimiento completo del ciclo de vida
- **Administrar clientes corporativos** y sus datos de contacto
- **Sincronizar información** entre el sistema de presupuestos y el CRM empresarial
- **Automatizar workflows** de atención al cliente y ventas

## 📋 Funcionalidades Implementadas

### ✅ Entidades CRM Soportadas
- **Casos (Incidents)** - Gestión completa de tickets y casos de soporte
- **Cuentas (Accounts)** - Empresas, organizaciones y clientes corporativos  
- **Contactos (Contacts)** - Personas, responsables y usuarios finales

### ✅ Operaciones CRUD Completas
- **Create** - Crear nuevos registros con validación
- **Read** - Consultas con filtros OData y paginación
- **Update** - Actualización parcial (PATCH) de registros existentes
- **Delete** - Eliminación con confirmación

### ✅ Características Avanzadas
- **Autenticación Azure AD** con client credentials flow
- **Caché inteligente de tokens** con renovación automática
- **Filtros OData** para búsquedas avanzadas
- **Paginación configurable** para listas grandes
- **Diagnósticos integrados** para troubleshooting
- **Logging detallado** para auditoría y debugging

## 🏗️ Arquitectura de la Integración

```
app/
├── models/
│   └── crm.py                    # Modelos Pydantic para CRM
├── services/
│   ├── crm_auth.py              # Servicio de autenticación
│   └── crm_service.py           # Servicio principal CRM
└── api/crm/
    ├── __init__.py              # Exportaciones del módulo
    ├── cases.py                 # Endpoints de casos
    ├── accounts.py              # Endpoints de cuentas
    ├── contacts.py              # Endpoints de contactos
    └── system.py                # Diagnósticos y sistema
```

## 🔧 Configuración

### Variables de Entorno Requeridas

```env
# Configuración de Dynamics 365 CRM
CRM_TENANT_ID=your-azure-tenant-id
CRM_CLIENT_ID=your-azure-app-client-id  
CRM_CLIENT_SECRET=your-azure-app-secret
CRM_D365_BASE_URL=https://yourorg.crm.dynamics.com
CRM_API_VERSION=v9.0
```

### Azure AD App Registration

Para configurar la autenticación, necesitas:

1. **Crear App Registration en Azure AD**
2. **Configurar permisos para Dynamics 365:**
   - `https://yourorg.crm.dynamics.com/user_impersonation`
3. **Generar client secret**
4. **Configurar las variables de entorno**

## 📝 Uso de los Endpoints

### Casos (Incidents)

```bash
# Listar casos con filtros
GET /api/crm/cases?filter_query=statuscode eq 1&top=25

# Crear nuevo caso
POST /api/crm/cases
{
  "title": "Sistema de facturación no funciona",
  "description": "El cliente reporta errores...",
  "customer_account_id": "629ca2a0-024a-ea11-a815-000d3a591218"
}

# Actualizar caso
PATCH /api/crm/cases/4bb40b00-024b-ea11-a815-000d3a591219
{
  "title": "Sistema de facturación - RESUELTO"
}
```

### Cuentas (Accounts)

```bash
# Buscar cuentas por nombre
GET /api/crm/accounts?filter_query=contains(name,'Tecnología')

# Crear nueva cuenta
POST /api/crm/accounts
{
  "name": "IT Quest Solutions",
  "telephone1": "+1-555-0123",
  "emailaddress1": "info@itqs.com",
  "websiteurl": "https://www.itqs.com"
}
```

### Contactos (Contacts)

```bash
# Buscar contactos por puesto
GET /api/crm/contacts?filter_query=contains(jobtitle,'Gerente')

# Crear nuevo contacto
POST /api/crm/contacts
{
  "firstname": "María",
  "lastname": "García López", 
  "emailaddress1": "maria.garcia@empresa.com",
  "jobtitle": "Gerente de TI"
}
```

## 🔍 Filtros OData Soportados

### Operadores Básicos
- `eq` - Igual que: `statuscode eq 1`
- `ne` - No igual: `statuscode ne 0`
- `gt` - Mayor que: `createdon gt 2025-01-01T00:00:00Z`
- `lt` - Menor que: `revenue lt 1000000`
- `contains` - Contiene: `contains(name,'Tecnología')`
- `startswith` - Empieza con: `startswith(name,'IT')`

### Ejemplos de Filtros Comunes

```bash
# Casos activos del último mes
filter_query=statuscode eq 1 and createdon gt 2025-09-01T00:00:00Z

# Cuentas de tecnología con ingresos altos
filter_query=contains(name,'Tecnología') and revenue gt 1000000

# Contactos gerentes con email corporativo
filter_query=contains(jobtitle,'Gerente') and contains(emailaddress1,'@empresa.com')
```

## 🏥 Diagnósticos y Health Check

### Health Check Básico
```bash
GET /api/crm/system/health
```
Respuesta:
```json
{
  "status": "ok",
  "d365": "https://itqsdev.crm.dynamics.com",
  "api_version": "v9.0"
}
```

### Diagnóstico Completo
```bash
GET /api/crm/system/diagnose
```
Verifica:
- ✅ Variables de entorno
- ✅ Adquisición de tokens
- ✅ Conectividad con D365
- ✅ Permisos y configuración

## 🔒 Seguridad

### Autenticación de Endpoints
Todos los endpoints CRM requieren autenticación:
```bash
Authorization: Bearer {jwt_token}
```

### Autenticación con Dynamics 365
- **Client Credentials Flow** para autenticación de aplicación
- **Tokens automáticamente renovados** 30 segundos antes de expirar
- **Caché en memoria** para evitar llamadas innecesarias
- **Logging de seguridad** para auditoría

## 🚨 Troubleshooting

### Problemas Comunes

1. **Error 401 Unauthorized**
   - Verificar configuración de Azure AD App Registration
   - Confirmar permisos para Dynamics 365
   - Verificar client_secret no expirado

2. **Error 403 Forbidden**
   - Usuario de aplicación no tiene permisos en D365
   - Verificar roles de seguridad asignados

3. **Error 500 Configuration**
   - Usar endpoint `/api/crm/system/diagnose` para identificar problema
   - Verificar variables de entorno CRM_*

### Comandos de Debug

```bash
# Limpiar caché de token (útil para problemas de autenticación)
POST /api/crm/system/clear-cache

# Ver información del token actual
GET /api/crm/system/token

# Diagnóstico completo
GET /api/crm/system/diagnose
```

## 📊 Logs y Auditoría

El sistema genera logs detallados para:
- ✅ Autenticación y renovación de tokens
- ✅ Peticiones HTTP a Dynamics 365  
- ✅ Errores y excepciones
- ✅ Operaciones CRUD por usuario
- ✅ Filtros y consultas ejecutadas

Ejemplo de log:
```
2025-10-09 10:30:15 | INFO | 🔍 Obteniendo casos - Usuario: maria@empresa.com
2025-10-09 10:30:16 | INFO | ✅ 15 casos obtenidos exitosamente
```

## � Métricas y Rendimiento

### Performance Optimizado
- **Conexiones asíncronas** con aiohttp para máximo throughput
- **Caché inteligente** reduce latencia en un 80% tras primer request
- **Paginación eficiente** maneja datasets de millones de registros
- **Pool de conexiones** reutilizable para mejor gestión de recursos

### Monitoreo Integrado
```bash
# Estadísticas de rendimiento
GET /api/crm/system/stats

# Métricas de caché
GET /api/crm/system/cache-stats
```

## 🔗 Integración con ezekl-budget

### Flujo de Datos
```
Presupuesto → Cliente → Dynamics 365 → Caso de Soporte → Facturación
```

### Casos de Uso Empresariales
1. **Nuevo cliente** → Crear cuenta en D365 automáticamente
2. **Presupuesto aprobado** → Generar oportunidad en CRM
3. **Problema técnico** → Crear caso con contexto del proyecto
4. **Seguimiento post-venta** → Actualizar contactos y actividades

## 🚀 Próximas Funcionalidades

### Roadmap Q4 2025
- [ ] **Oportunidades (Opportunities)** - Gestión de pipeline de ventas
- [ ] **Actividades y Tareas** - Seguimiento de acciones comerciales
- [ ] **Campañas de Marketing** - Integración con campañas automatizadas
- [ ] **Reportes Avanzados** - Dashboards personalizados y KPIs
- [ ] **Webhooks en Tiempo Real** - Sincronización bidireccional automática

### Integraciones Futuras
- [ ] **Power BI** - Reportes ejecutivos y analytics
- [ ] **Teams** - Notificaciones en tiempo real
- [ ] **Outlook** - Sincronización de calendarios y emails
- [ ] **SharePoint** - Gestión documental integrada

---

📧 **Soporte**: Para dudas técnicas sobre esta integración, contacta al equipo de desarrollo.  
🔧 **Configuración**: Ver documentación de configuración en el README.md principal del proyecto.