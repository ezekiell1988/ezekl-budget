# Ezekl Budget - Aplicación Híbrida FastAPI + Ionic Angular

Este es un proyecto híbrido que combina **FastAPI** (backend) con **Ionic Angular 8**(frontend) para gestión de presupuesto con autenticación Microsoft, integración de Azure OpenAI, y deployment automático.

## 🚀 Características

### Frontend (Ionic Angular 8)
- **Ionic 8** con Angular 20 y Standalone Components (sin app.module.ts)
- **Autenticación Microsoft** con Azure AD
- **UI moderna** y responsive
- **PWA** capabilities con Capacitor

### Backend (FastAPI)
- **FastAPI** con documentación automática
- **Servidor híbrido** que sirve tanto API como frontend
- **WebSocket en tiempo real** con ping-pong y reconexión automática
- **Cliente HTTP asíncrono** con `aiohttp` y soporte completo para todos los verbos HTTP
- **Procesamiento de emails** via Azure Event Grid con descarga asíncrona de contenido MIME
- **Sistema de autenticación dual** - Login manual (2FA) + Microsoft OAuth2 SSO
- **Microsoft OAuth2** - Azure AD con asociación de cuentas automática
- **Cola de emails en background** - Envío asíncrono sin bloquear API
- **Azure OpenAI** integration
- **Dynamics 365 CRM** - Integración empresarial completa: casos de soporte, cuentas corporativas, contactos, diagnósticos automáticos y filtros OData avanzados
- **SQL Server** con conexiones asíncronas y stored procedures
- **Detección de ambiente** con variable ENVIRONMENT (development/production)

### DevOps
- **Docker** multi-stage build optimizado
- **CI/CD automático** con GitHub Actions (compila Ionic + despliega FastAPI)
- **SSL/HTTPS** con certificados Let's Encrypt
- **Reverse proxy** con Nginx

## 🌐 URLs del Proyecto

- **Frontend (Ionic Angular)**: https://budget.ezekl.com
- **API**: https://budget.ezekl.com/api/*
- **API Docs**: https://budget.ezekl.com/docs
- **API Health**: https://budget.ezekl.com/api/health
- **Microsoft Auth**: https://budget.ezekl.com/api/auth/microsoft
- **CRM API**: https://budget.ezekl.com/api/crm/* (Dynamics 365: casos, cuentas, contactos)
- **CRM Health**: https://budget.ezekl.com/api/crm/system/health (diagnóstico CRM)
- **WebSocket**: wss://budget.ezekl.com/ws/ (tiempo real)

## � Inicio Rápido (Desarrollo Local)

```bash
# 1. Clonar proyecto
git clone https://github.com/ezekiell1988/ezekl-budget.git
cd ezekl-budget

# 2. Configurar Python
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# 3. Configurar frontend Ionic
cd ezekl-budget-ionic
npm install
ionic build --prod  # ← IMPORTANTE: Compilar antes de levantar FastAPI
cd ..

# 4. Crear archivo .env (copiar desde .env.example)
cp .env.example .env
# Editar .env con tus credenciales de Azure OpenAI y BD

# 5. Levantar servidor híbrido
.venv/bin/python -m app.main
# 🌐 Abre: http://localhost:8001 (frontend + API)
# 📚 Docs: http://localhost:8001/docs
```

## �📋 Requisitos

### Local (Desarrollo)
- **Python 3.13+** (para FastAPI backend)
- **Node.js 20+** (para Ionic frontend)
- **Ionic CLI** (`npm install -g @ionic/cli`)
- **Git**

### Servidor (Azure)
- Ubuntu 22.04+
- Docker y Docker Compose
- Node.js 20+ (para compilar Ionic en CI/CD)
- Nginx
- Certbot (Let's Encrypt)
- SQL Server 2022 Developer Edition
- Microsoft ODBC Driver 18 for SQL Server (instalado en contenedor Docker)
- Archivo .env configurado en producción

## 🛠️ Configuración Inicial

### 1. Clonar el Proyecto

```bash
git clone https://github.com/ezekiell1988/ezekl-budget.git
cd ezekl-budget
```

### 2. Configurar Entorno de Desarrollo

#### Backend (FastAPI)
```bash
# Crear entorno virtual para Python
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate  # Linux/macOS
# o
.venv\\Scripts\\activate     # Windows

# Instalar dependencias de Python
pip install -r requirements.txt
```

#### Frontend (Ionic Angular)
```bash
# Instalar Ionic CLI globalmente
npm install -g @ionic/cli

# Navegar al proyecto Ionic e instalar dependencias
cd ezekl-budget-ionic
npm install
```

### 3. Configurar Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```env
# Configuración del servidor híbrido
PORT=8001
ENVIRONMENT=development

# Azure OpenAI Configuration (requerido)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# Microsoft Azure AD (OAuth2 SSO)
AZURE_CLIENT_ID=your-client-id-from-azure-ad
AZURE_TENANT_ID=your-tenant-id-from-azure-ad
AZURE_CLIENT_SECRET=your-client-secret-from-azure-ad

# Deployment Configuration
DEPLOY_HOST=20.246.83.239
DEPLOY_USER=azureuser
DEPLOY_BASE_PATH=/home/azureuser/projects

# Configuración de Base de Datos SQL Server
# En desarrollo (local): usar IP del servidor Azure
# En producción: usar localhost o conexión local (detectado automáticamente)
DB_HOST=20.246.83.239
DB_PORT=1433
DB_NAME=budgetdb
DB_USER=budgetuser
DB_PASSWORD=your-database-password
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUST_CERT=yes
```

### 4. Configuración de Base de Datos

La aplicación utiliza **SQL Server 2022** con un patrón específico de stored procedures:

#### Arquitectura de Base de Datos
- **Usuario limitado**: `budgetuser` con permisos solo para ejecutar stored procedures
- **Patrón de comunicación**: Todos los endpoints se comunican con la BD mediante stored procedures
- **Formato JSON**: Cada SP recibe un JSON como parámetro único y responde un JSON en columna "json"
- **Conexiones asíncronas**: Utiliza `aioodbc` para mejor rendimiento

#### Detección de Ambiente con Variable ENVIRONMENT
```python
# En desarrollo: ENVIRONMENT=development (usa DB_HOST=20.246.83.239 - IP externa)
# En producción: ENVIRONMENT=production (usa localhost para mejor rendimiento)
```

La aplicación usa la variable `ENVIRONMENT` para determinar el comportamiento:
- **development**: Usa IP externa del servidor para base de datos
- **production**: Usa localhost para mejor rendimiento y URLs de producción

#### Base de Datos Configurada
- **Nombre**: `budgetdb`
- **Collation**: `SQL_Latin1_General_CP1_CI_AS` (soporte para español y emojis)
- **Usuario**: `budgetuser` (permisos limitados)
- **Puerto**: 1433 (estándar SQL Server)

#### Sistema de Autenticación Dual Implementado

La aplicación incluye **dos métodos de autenticación**:

##### 🔐 Autenticación Manual (2FA)
Sistema tradicional de dos factores con tokens por email:

**Flujo Manual:**
- **Paso 1**: Usuario ingresa `codeLogin`
- **Paso 2**: Sistema genera token de 5 dígitos y envía por email
- **Paso 3**: Usuario verifica token y recibe JWE para sesiones

##### 🏢 Microsoft OAuth2 SSO
Single Sign-On empresarial con Azure AD:

**Flujo Microsoft:**
- **Paso 1**: Usuario hace clic en "Login with Microsoft"
- **Paso 2**: Redirección a Azure AD para autenticación
- **Paso 3**: Sistema verifica si está asociado con cuenta local:
  - ✅ **Si asociado**: Login automático con JWE
  - 🔄 **No asociado**: Solicita asociación con `codeLogin` existente

**Características:**
- ✅ **Asociación automática** - Vincula cuentas Microsoft con usuarios locales
- ✅ **Datos completos** - Obtiene perfil, email, departamento de Microsoft Graph
- ✅ **Tokens seguros** - Almacena access/refresh tokens encriptados
- ✅ **Login unificado** - Mismo JWE para ambos métodos tras asociación

##### Stored Procedures de Autenticación
```sql
-- Autenticación manual (2FA)
EXEC spLoginTokenAdd @json = '{"codeLogin": "S"}'
EXEC spLoginAuth @json = '{"codeLogin": "S", "token": "123456"}'

-- Microsoft OAuth2 (nuevo)
EXEC spLoginMicrosoftAddOrEdit @json = '{"id": "microsoft_user_id", "mail": "user@company.com", ...}'
```

##### Características de Seguridad
- ✅ **Dual authentication** - Login manual 2FA + Microsoft SSO
- ✅ **Microsoft Azure AD** - OAuth2 con asociación automática de cuentas
- ✅ **Tokens temporales** - Expiración en 10 minutos (manual)
- ✅ **JWE encryption** - No solo firmado, sino encriptado
- ✅ **Email queue** - Envío asíncrono en background
- ✅ **Account linking** - Usuarios Microsoft se asocian con cuentas locales
- ✅ **Base de datos** - Validación mediante stored procedures

### 4.5. Cliente HTTP Asíncrono (HTTPClient)

La aplicación incluye un **cliente HTTP asíncrono** robusto basado en `aiohttp`:

#### Características del Cliente HTTP
- **Soporte completo**: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- **Configuración flexible**: URL base, timeouts, headers por defecto
- **Logging automático**: Peticiones y respuestas con detalles
- **Manejo de errores**: Captura y logging de excepciones HTTP
- **Métodos de conveniencia**: `get_json()`, `get_text()`, `get_bytes()`
- **Session management**: Automático con context managers

#### Uso del Cliente HTTP

```python
from app.core.http_request import HTTPClient, get_text, get_json

# Cliente con configuración específica
client = HTTPClient(
    base_url="https://api.ejemplo.com",
    timeout=30,
    default_headers={"Authorization": "Bearer token"}
)

# Realizar peticiones
response = await client.get("/endpoint")
data = await client.get_json("/api/data")

# Funciones de conveniencia (cliente global)
content = await get_text("https://ejemplo.com/mime-content")
api_data = await get_json("https://api.ejemplo.com/data")
```

#### Integración en el Proyecto

El cliente HTTP se utiliza en:
- **Procesamiento de emails**: Descarga asíncrona de contenido MIME
- **Integraciones futuras**: APIs externas, webhooks, servicios de terceros
- **Centralización**: Un punto único para todas las peticiones HTTP

### 4.6. Servicios de Negocio (Services)

La aplicación implementa una **arquitectura de servicios** para organizar la lógica de negocio:

#### Estructura de Services

```
app/services/
├── __init__.py           # Módulo de servicios
└── email_service.py      # Servicio centralizado para envío de emails
```

#### EmailService - Gestión Centralizada de Emails

El `EmailService` proporciona funcionalidad reutilizable para el envío de emails desde cualquier parte de la aplicación:

**Características principales:**
- ✅ **Cliente Azure lazy-loaded** - Inicialización bajo demanda
- ✅ **Múltiples métodos de envío** - Desde objetos Request o parámetros directos  
- ✅ **Soporte dual de contenido** - HTML y texto plano
- ✅ **Múltiples destinatarios** - Lista de emails en una sola operación
- ✅ **Configuración flexible** - Remitente personalizable
- ✅ **Manejo robusto de errores** - Sin excepciones, respuestas estructuradas
- ✅ **Logging detallado** - Para debugging y auditoria

**Uso del servicio:**

```python
from app.services.email_service import email_service, send_email

# Usando la instancia global del servicio
response = await email_service.send_email(
    to=["user@example.com"],
    subject="Notificación importante",
    html_content="<h1>Mensaje HTML</h1>",
    text_content="Mensaje en texto plano"
)

# Usando función de conveniencia
response = await send_email(
    to=["user@example.com"], 
    subject="Test",
    text_content="Mensaje simple"
)
```

#### Arquitectura de Separación de Responsabilidades

- **`core/`** → Infraestructura y configuración (config.py, http_request.py)
- **`services/`** → Lógica de negocio y servicios (email_service.py)
- **`api/routes/`** → Endpoints que usan los services
- **`models/`** → Modelos de datos y validación

Esta separación permite:
- ✅ **Reutilización** - Los servicios se pueden usar desde múltiples endpoints
- ✅ **Testabilidad** - Fácil testing unitario de lógica de negocio
- ✅ **Mantenibilidad** - Código organizado por responsabilidades
- ✅ **Escalabilidad** - Agregar nuevos servicios es directo

### 4.8. Integración con Dynamics 365 CRM 🏢

La aplicación incluye **integración empresarial completa con Microsoft Dynamics 365 CRM**, proporcionando gestión avanzada de relaciones con clientes, seguimiento de casos de soporte y administración de cuentas corporativas.

#### 🚀 Funcionalidades CRM Principales

**Gestión Empresarial Completa:**
- ✅ **Casos de Soporte (Incidents)** - Tickets, seguimiento, resolución y escalado
- ✅ **Cuentas Corporativas (Accounts)** - Empresas, organizaciones y clientes B2B
- ✅ **Contactos Empresariales (Contacts)** - Personas, responsables y usuarios finales
- ✅ **Diagnósticos Automáticos** - Health check y troubleshooting integrado
- ✅ **Búsquedas Avanzadas** - Filtros OData, paginación y ordenamiento

**Características Técnicas Avanzadas:**
- ✅ **Autenticación Azure AD** - Client credentials flow con renovación automática
- ✅ **Caché Inteligente de Tokens** - Renovación 30 segundos antes de expirar
- ✅ **Cliente HTTP Asíncrono** - Máximo rendimiento con aiohttp
- ✅ **Modelos Pydantic Completos** - Validación y documentación automática
- ✅ **Logging Empresarial** - Auditoría completa de operaciones CRM
- ✅ **Manejo Robusto de Errores** - Recuperación automática y reintentos

#### 📊 Casos de Uso Empresariales

**Flujo de Trabajo Integrado:**
```
Cliente → Presupuesto → Cuenta D365 → Caso Soporte → Resolución → Facturación
```

**Escenarios Reales:**
1. **Cliente nuevo** → Se crea automáticamente cuenta corporativa en D365
2. **Presupuesto aprobado** → Genera oportunidad de venta en CRM
3. **Incidencia técnica** → Crea caso con contexto completo del proyecto
4. **Seguimiento comercial** → Actualiza contactos y actividades empresariales

#### Endpoints CRM disponibles:

**Sistema y diagnóstico:**
- `GET /api/crm/system/health` - Health check del CRM
- `GET /api/crm/system/diagnose` - Diagnóstico completo de configuración
- `GET /api/crm/system/token` - Información del token (debugging)

**Casos (Incidents):**
- `GET /api/crm/cases` - Lista paginada con filtros OData
- `GET /api/crm/cases/{id}` - Caso específico por GUID
- `POST /api/crm/cases` - Crear nuevo caso
- `PATCH /api/crm/cases/{id}` - Actualizar caso existente
- `DELETE /api/crm/cases/{id}` - Eliminar caso

**Cuentas (Accounts):**
- `GET /api/crm/accounts` - Lista de empresas/organizaciones
- `GET /api/crm/accounts/{id}` - Cuenta específica
- `POST /api/crm/accounts` - Crear nueva cuenta
- `PATCH /api/crm/accounts/{id}` - Actualizar cuenta
- `DELETE /api/crm/accounts/{id}` - Eliminar cuenta

**Contactos (Contacts):**
- `GET /api/crm/contacts` - Lista de personas/contactos
- `GET /api/crm/contacts/{id}` - Contacto específico
- `POST /api/crm/contacts` - Crear nuevo contacto
- `PATCH /api/crm/contacts/{id}` - Actualizar contacto
- `DELETE /api/crm/contacts/{id}` - Eliminar contacto

#### Configuración CRM:

```env
# Variables de entorno requeridas para CRM
CRM_TENANT_ID=your-azure-tenant-id
CRM_CLIENT_ID=your-azure-app-client-id
CRM_CLIENT_SECRET=your-azure-app-secret
CRM_D365_BASE_URL=https://yourorg.crm.dynamics.com
CRM_API_VERSION=v9.0
```

#### 🔗 Documentación Completa CRM

Para información detallada sobre configuración, ejemplos de uso, filtros OData, troubleshooting y características avanzadas, consulta:

📖 **[Documentación CRM Completa](./app/api/crm/README.md)** - Guía técnica exhaustiva con ejemplos prácticos

#### 🏥 Diagnósticos Rápidos

```bash
# Health check básico del CRM
curl https://budget.ezekl.com/api/crm/system/health

# Diagnóstico completo de configuración
curl -H "Authorization: Bearer {token}" https://budget.ezekl.com/api/crm/system/diagnose

# Ejemplo: Crear nuevo caso
curl -X POST https://budget.ezekl.com/api/crm/cases \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Sistema facturación", "description": "Error en módulo..."}'
```

#### ⚙️ Arquitectura CRM

```
app/api/crm/
├── README.md              # 📖 Documentación completa
├── __init__.py           # 🔧 Exportaciones del módulo
├── cases.py              # 🎫 Endpoints de casos/tickets
├── accounts.py           # 🏢 Endpoints de cuentas corporativas
├── contacts.py           # 👤 Endpoints de contactos empresariales
└── system.py             # 🏥 Diagnósticos y health checks

app/services/
├── crm_auth.py          # 🔐 Autenticación Azure AD + caché
└── crm_service.py       # ⚙️ Lógica de negocio CRM

app/models/crm.py        # 📝 Modelos Pydantic para CRM
```

### 4.7. WebSocket en Tiempo Real

La aplicación incluye **WebSocket** para comunicación en tiempo real entre cliente y servidor:

#### Características del WebSocket
- **Endpoint**: `/ws/` (prefijo consistente con estructura API)
- **Protocolo**: WS en desarrollo local, WSS en producción con SSL
- **Ping-Pong automático**: Cada 30 segundos para mantener conexión activa
- **Reconexión automática**: Hasta 5 intentos con backoff exponencial
- **Mensajes JSON**: Comunicación estructurada con tipos específicos
- **Detección de SO del servidor**: Fix automático para Windows

#### 🪟 Compatibilidad con Windows

**Problema común**: En Windows, `localhost` puede resolver a IPv6 (`::1`) causando fallos en WebSockets.

**Solución inteligente implementada**:

1. **Backend** expone dos endpoints:
   - `/api/server-config` (público): Retorna sistema operativo del servidor
   - `/api/credentials` (privado 🔒): Requiere autenticación

2. **Frontend** consulta el SO del servidor antes de conectar

3. **Fix automático**: Si servidor es Windows, convierte `localhost` → `127.0.0.1`

**Resultado**: WebSocket funciona en Windows, Mac, Linux y producción sin cambios manuales.

**Configuración del servidor por plataforma**:
```python
# Windows
host = "127.0.0.1"  # Solo localhost
loop = "asyncio"
event_loop_policy = WindowsSelectorEventLoopPolicy()

# Linux/Mac
host = "0.0.0.0"    # Todas las interfaces
loop = "uvloop"     # Más rápido
```

#### Tipos de mensajes soportados:
```json
// Ping desde cliente
{
  "type": "ping",
  "timestamp": "2024-10-05T02:47:09.589Z",
  "message": "ping from client"
}

// Pong desde servidor
{
  "type": "pong",
  "timestamp": "2024-10-05T02:47:09.632Z",
  "client_timestamp": "2024-10-05T02:47:09.589Z",
  "message": "pong from server"
}

// Echo test
{
  "type": "echo",
  "message": "Test message",
  "timestamp": "2024-10-05T02:47:09.589Z"
}
```

#### URLs del WebSocket:
- **Desarrollo local (Windows)**: `ws://127.0.0.1:8001/ws/`
- **Desarrollo local (Mac/Linux)**: `ws://localhost:8001/ws/` o `ws://127.0.0.1:8001/ws/`
- **Producción**: `wss://budget.ezekl.com/ws/`

#### Implementación del Cliente:
El componente `DemoWebsocketPage` incluye un cliente WebSocket completo con:
- ✅ Detección automática de URL según SO del servidor
- ✅ Fix automático de `localhost` → `127.0.0.1` solo en Windows
- ✅ Reconexión automática con backoff exponencial
- ✅ Ping-pong automático cada 30 segundos
- ✅ UI en tiempo real con estado de conexión
- ✅ Log de mensajes con timestamps
- ✅ Controles manuales para testing

### 5. Configurar GitHub Secrets

En tu repositorio de GitHub, ve a **Settings → Secrets and variables → Actions** y agrega:

```
# Deployment SSH
SSH_PRIVATE_KEY=contenido_completo_de_tu_archivo_.pem
SSH_HOST=20.246.83.239
SSH_USER=azureuser

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=tu_endpoint_de_azure
AZURE_OPENAI_API_KEY=tu_api_key_de_azure
AZURE_OPENAI_DEPLOYMENT_NAME=tu_deployment_name

# Azure Communication Services
AZURE_COMMUNICATION_ENDPOINT=tu_endpoint_de_communication_services
AZURE_COMMUNICATION_KEY=tu_primary_key_de_communication_services
AZURE_COMMUNICATION_SENDER_ADDRESS=noreply@tudominio.com

# Azure AD (OAuth)
AZURE_CLIENT_ID=tu_client_id_de_azure_ad
AZURE_CLIENT_SECRET=tu_client_secret_de_azure_ad
AZURE_TENANT_ID=tu_tenant_id_de_azure_ad

# Dynamics 365 CRM (opcional)
CRM_TENANT_ID=tu_tenant_id_para_dynamics365
CRM_CLIENT_ID=tu_client_id_de_la_app_dynamics365
CRM_CLIENT_SECRET=tu_client_secret_de_la_app_dynamics365
CRM_D365_BASE_URL=https://tuorganizacion.crm.dynamics.com

# Base de Datos
DB_PASSWORD=tu_contraseña_de_base_de_datos
```

**Nota:** El workflow de GitHub Actions sincroniza automáticamente estos secretos al archivo `.env` del servidor en cada deployment.

## 🖥️ Desarrollo Local

### Opción 1: Desarrollo Completo (Frontend + Backend por separado)

```bash
# Terminal 1: Frontend Ionic (desarrollo con hot-reload)
cd ezekl-budget-ionic
ionic serve  # http://localhost:8100 ← Para desarrollo del frontend

# Terminal 2: Backend FastAPI
source .venv/bin/activate
.venv/bin/python -m app.main  # http://localhost:8001/api ← Solo API endpoints
```

### Opción 2: Servidor Híbrido (Producción Local)

```bash
# 1. Compilar frontend (OBLIGATORIO - el servidor sirve desde www/)
cd ezekl-budget-ionic
ionic build --prod
cd ..

# 2. Ejecutar servidor híbrido FastAPI
source .venv/bin/activate  # Activar entorno virtual
.venv/bin/python -m app.main  # Levantar servidor en puerto 8001

# ⚠️ IMPORTANTE: El frontend DEBE estar compilado en www/ 
# porque FastAPI sirve los archivos estáticos desde ezekl-budget-ionic/www/
```

### URLs de Desarrollo:
- **Frontend (dev)**: http://localhost:8100 ← Hot reload
- **Frontend (híbrido)**: http://localhost:8001/ ← Como producción
- **API**: http://localhost:8001/api/*
- **API Docs**: http://localhost:8001/docs
- **WebSocket**: ws://localhost:8001/ws/ ← Tiempo real

### 🪟 Desarrollo en Windows

**Configuración específica para Windows**:

```bash
# Activar entorno virtual (PowerShell)
.\.venv\Scripts\Activate.ps1

# O en Command Prompt
.venv\Scripts\activate.bat

# Instalar dependencias (uvloop se excluye automáticamente en Windows)
pip install -r requirements.txt

# Ejecutar servidor (asyncio se usa automáticamente en Windows)
python -m app.main
```

**Script automatizado para Windows**:

```powershell
# Usar el script de inicio optimizado para Windows
.\start-windows.ps1

# O para reconstruir frontend + reiniciar servidor
.\rebuild-and-restart.ps1
```

**Diferencias importantes**:
- ✅ **Event Loop**: Se usa `asyncio` con `WindowsSelectorEventLoopPolicy` (automático)
- ✅ **Host**: Servidor usa `127.0.0.1` en lugar de `0.0.0.0` para WebSockets
- ✅ **WebSockets**: Funcionan perfectamente con detección inteligente del SO
- ✅ **Performance**: Ligeramente menor que Linux/Mac pero completamente funcional
- ✅ **Desarrollo**: Sin diferencias en el código, detección automática del OS

#### 🔧 Solución de WebSocket en Windows

**Problema**: Windows resuelve `localhost` a IPv6 (`::1`), causando fallos en WebSockets.

**Solución Implementada**: Sistema inteligente de detección del SO del servidor.

**Arquitectura**:
```
Cliente → GET /api/server-config (público) → Recibe SO del servidor
       → Si Windows: convierte localhost a 127.0.0.1
       → Conecta WebSocket con configuración correcta
```

**Características**:
- 🎯 **Detección inteligente**: Cliente consulta SO del servidor
- 🔒 **Seguro**: `/api/server-config` público, `/api/credentials` privado
- 🌍 **Multiplataforma**: Fix aplicado solo en Windows
- ✅ **Transparente**: Funciona con `localhost` o `127.0.0.1`

#### 🌐 Configuración de IIS con Reverse Proxy (Windows Server)

Si deseas desplegar la aplicación en un servidor Windows con IIS, sigue estos pasos:

**Requisitos previos**:
- Windows Server 2019/2022 o Windows 10/11 Pro
- IIS instalado con Application Request Routing (ARR) y URL Rewrite
- Python 3.13+ instalado
- Aplicación configurada y corriendo en `http://127.0.0.1:8001`

**1. Instalar módulos necesarios en IIS**:

Descarga e instala los siguientes módulos desde la web de Microsoft:
- **Application Request Routing (ARR) 3.0**: Para habilitar reverse proxy
- **URL Rewrite 2.1**: Para reescritura de URLs y manejo de WebSocket

```powershell
# Verificar que los módulos están instalados
Get-WindowsFeature -Name Web-* | Where-Object {$_.InstallState -eq 'Installed'}
```

**2. Habilitar Proxy en ARR**:

1. Abre IIS Manager
2. Selecciona el servidor (nivel raíz)
3. Doble clic en "Application Request Routing Cache"
4. Clic en "Server Proxy Settings" (panel derecho)
5. Marca "Enable proxy"
6. Establece valores:
   - HTTP version: `Pass Through`
   - Response buffer threshold: `0`
   - Time-out (seconds): `300`
7. Clic en "Apply"

**3. Configurar sitio en IIS**:

```powershell
# Crear directorio para el sitio
New-Item -ItemType Directory -Path "C:\inetpub\wwwroot\budget.ezekl.com" -Force

# Crear sitio en IIS (PowerShell)
Import-Module WebAdministration
New-WebSite -Name "budget.ezekl.com" `
    -Port 80 `
    -HostHeader "budget.ezekl.com" `
    -PhysicalPath "C:\inetpub\wwwroot\budget.ezekl.com"
```

**4. Configurar URL Rewrite para Reverse Proxy**:

Crea o edita el archivo `web.config` en `C:\inetpub\wwwroot\budget.ezekl.com\web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <!-- WebSocket Rule - DEBE IR PRIMERO -->
                <rule name="WebSocket" stopProcessing="true">
                    <match url="^ws/(.*)$" />
                    <action type="Rewrite" url="ws://127.0.0.1:8001/ws/{R:1}" />
                    <conditions>
                        <add input="{HTTP:Connection}" pattern="Upgrade" />
                        <add input="{HTTP:Upgrade}" pattern="websocket" />
                    </conditions>
                </rule>
                
                <!-- API Routes -->
                <rule name="API" stopProcessing="true">
                    <match url="^api/(.*)$" />
                    <action type="Rewrite" url="http://127.0.0.1:8001/api/{R:1}" />
                </rule>
                
                <!-- Docs and Static -->
                <rule name="Docs" stopProcessing="true">
                    <match url="^(docs|redoc|openapi.json)(.*)$" />
                    <action type="Rewrite" url="http://127.0.0.1:8001/{R:1}{R:2}" />
                </rule>
                
                <!-- Frontend/SPA Routes -->
                <rule name="SPA" stopProcessing="true">
                    <match url=".*" />
                    <conditions logicalGrouping="MatchAll">
                        <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
                        <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
                    </conditions>
                    <action type="Rewrite" url="http://127.0.0.1:8001/{R:0}" />
                </rule>
            </rules>
        </rewrite>
        
        <!-- Configuración adicional para WebSockets -->
        <webSocket enabled="true" />
        
        <!-- Headers para CORS y seguridad -->
        <httpProtocol>
            <customHeaders>
                <add name="X-Frame-Options" value="SAMEORIGIN" />
                <add name="X-Content-Type-Options" value="nosniff" />
            </customHeaders>
        </httpProtocol>
        
        <!-- Aumentar límites para subida de archivos -->
        <security>
            <requestFiltering>
                <requestLimits maxAllowedContentLength="52428800" />
            </requestFiltering>
        </security>
    </system.webServer>
</configuration>
```

**5. Configurar servicio Python como tarea programada o servicio Windows**:

Opción A - **NSSM (Non-Sucking Service Manager)** (Recomendado):

```powershell
# Descargar NSSM desde https://nssm.cc/download
# Instalar el servicio
nssm install ezekl-budget "C:\Users\Administrator\.venv\Scripts\python.exe" "-m app.main"
nssm set ezekl-budget AppDirectory "C:\inetpub\wwwroot\budget.ezekl.com"
nssm set ezekl-budget DisplayName "Ezekl Budget FastAPI"
nssm set ezekl-budget Description "Servidor FastAPI para Ezekl Budget"
nssm set ezekl-budget Start SERVICE_AUTO_START

# Iniciar servicio
nssm start ezekl-budget

# Ver logs
nssm status ezekl-budget
```

Opción B - **Tarea programada**:

```powershell
# Crear script de inicio
$scriptPath = "C:\inetpub\wwwroot\budget.ezekl.com\start-service.ps1"
@"
Set-Location 'C:\path\to\ezekl-budget'
.\.venv\Scripts\Activate.ps1
python -m app.main
"@ | Out-File -FilePath $scriptPath -Encoding UTF8

# Crear tarea programada
$action = New-ScheduledTaskAction -Execute 'PowerShell.exe' -Argument "-File $scriptPath"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
Register-ScheduledTask -TaskName "EzeklBudget" -Action $action -Trigger $trigger -Principal $principal
```

**6. Configurar SSL con Certificado**:

```powershell
# Instalar certificado SSL (desde archivo .pfx)
$certPath = "C:\certs\budget.ezekl.com.pfx"
$certPassword = ConvertTo-SecureString -String "tu_password" -Force -AsPlainText
Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\LocalMachine\My -Password $certPassword

# Obtener thumbprint del certificado
$cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object {$_.Subject -like "*budget.ezekl.com*"}

# Agregar binding HTTPS al sitio
New-WebBinding -Name "budget.ezekl.com" -Protocol https -Port 443 -HostHeader "budget.ezekl.com" -SslFlags 1
$binding = Get-WebBinding -Name "budget.ezekl.com" -Protocol https
$binding.AddSslCertificate($cert.Thumbprint, "my")
```

**7. Verificar configuración**:

```powershell
# Verificar que Python está corriendo
Test-NetConnection -ComputerName 127.0.0.1 -Port 8001

# Verificar IIS
Get-Website | Where-Object {$_.Name -eq "budget.ezekl.com"}

# Probar endpoints
Invoke-WebRequest -Uri "http://localhost/api/health" -UseBasicParsing
Invoke-WebRequest -Uri "https://budget.ezekl.com/api/health" -UseBasicParsing
```

**8. Troubleshooting común**:

```powershell
# Ver logs de IIS
Get-Content "C:\inetpub\logs\LogFiles\W3SVC*\*.log" -Tail 50

# Verificar permisos
icacls "C:\inetpub\wwwroot\budget.ezekl.com"

# Reiniciar servicios
Restart-Service W3SVC
Restart-Service WAS

# Verificar firewall
New-NetFirewallRule -DisplayName "HTTP-In" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "HTTPS-In" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

**Ventajas de IIS con Reverse Proxy**:
- ✅ Integración nativa con Windows Server
- ✅ Gestión centralizada de certificados SSL
- ✅ Soporte completo para WebSockets
- ✅ Logs y monitoreo integrados
- ✅ Load balancing si se necesita escalabilidad
- ✅ Gestión de autenticación Windows (opcional)

### Ejecutar con Docker (Local)

```bash
# Construir imagen
docker build -t ezekl-budget .

# Ejecutar contenedor
docker run -d --name ezekl-budget -p 8001:8001 --env-file .env ezekl-budget

# O usar docker-compose
docker-compose up -d
```

## 🌐 Configuración de Host/Binding por Sistema Operativo

### ⚠️ **Diferencia Crítica: 0.0.0.0 vs 127.0.0.1**

La configuración del **host binding** es **diferente** según el sistema operativo y tiene implicaciones importantes para accesibilidad:

#### 🐧 **Linux y macOS (Recomendado: 0.0.0.0)**

```python
# En app/main.py (configuración actual)
uvicorn.run(app, host="0.0.0.0", port=settings.port)
```

**Ventajas de 0.0.0.0:**
- ✅ **Acceso externo** - Otros dispositivos pueden conectarse
- ✅ **Docker compatible** - Funciona dentro de contenedores
- ✅ **Redes locales** - Accesible desde otras máquinas en la red
- ✅ **Producción** - Configuración estándar para servidores
- ✅ **Desarrollo colaborativo** - Otros desarrolladores pueden acceder

**URLs accesibles:**
```bash
http://localhost:8001     # ✅ Acceso local
http://127.0.0.1:8001     # ✅ Acceso local  
http://192.168.1.100:8001 # ✅ Acceso desde red local
http://YOUR_IP:8001       # ✅ Acceso externo (si firewall permite)
```

#### 🪟 **Windows (Alternativa: 127.0.0.1)**

Si tienes problemas con `0.0.0.0` en Windows, puedes usar:

```python
# Alternativa solo para desarrollo Windows local
uvicorn.run(app, host="127.0.0.1", port=settings.port)
```

**Limitaciones de 127.0.0.1:**
- ❌ **Solo acceso local** - Otros dispositivos NO pueden conectarse
- ❌ **Docker limitado** - Problemas con port mapping
- ❌ **Sin acceso de red** - Solo localhost funciona
- ⚠️ **Desarrollo limitado** - Solo el desarrollador puede acceder

**URLs accesibles:**
```bash
http://localhost:8001     # ✅ Acceso local
http://127.0.0.1:8001     # ✅ Acceso local
http://192.168.1.100:8001 # ❌ NO funciona
```

#### 🔧 **Configuración Condicional por OS**

Para máxima compatibilidad, puedes usar:

```python
import platform

# Configuración automática por SO
if platform.system() == "Windows":
    host = "127.0.0.1"  # Solo si 0.0.0.0 causa problemas
else:
    host = "0.0.0.0"    # Linux/macOS (recomendado)

uvicorn.run(app, host=host, port=settings.port)
```

#### 🐳 **Docker y Contenedores**

**SIEMPRE usar 0.0.0.0 en Docker:**

```dockerfile
# En Dockerfile (configuración actual correcta)
EXPOSE 8001
CMD ["python", "-m", "app.main"]
```

```python
# El servidor DEBE usar 0.0.0.0 para Docker
uvicorn.run(app, host="0.0.0.0", port=settings.port)
```

**¿Por qué?** Docker mapea puertos desde el contenedor al host:
```bash
docker run -p 8001:8001 ezekl-budget  # Host:Contenedor
# 127.0.0.1 NO funcionaría aquí
```

#### 🔥 **Firewall y Seguridad**

**Para producción con 0.0.0.0:**
```bash
# Linux: Configurar firewall
sudo ufw allow 8001/tcp

# Windows: Configurar Windows Defender Firewall
# Permitir aplicación Python en puerto 8001

# macOS: Sistema automático, generalmente no requiere configuración
```

#### 📊 **Tabla de Compatibilidad**

| Sistema | Host Config | Acceso Local | Acceso Red | Docker | Producción |
|---------|-------------|--------------|------------|---------|------------|
| **Linux** | `0.0.0.0` | ✅ Perfecto | ✅ Perfecto | ✅ Perfecto | ✅ Recomendado |
| **macOS** | `0.0.0.0` | ✅ Perfecto | ✅ Perfecto | ✅ Perfecto | ✅ Recomendado |
| **Windows** | `0.0.0.0` | ✅ Funciona | ✅ Funciona | ✅ Funciona | ✅ Recomendado |
| **Windows** | `127.0.0.1` | ✅ Solo local | ❌ No funciona | ❌ Problemas | ❌ No recomendado |

#### 🎯 **Recomendación Final**

**Usar SIEMPRE `0.0.0.0`** excepto en casos muy específicos:

```python
# ✅ CONFIGURACIÓN RECOMENDADA (actual en el proyecto)
uvicorn.run(app, host="0.0.0.0", port=settings.port)
```

**Casos donde usar 127.0.0.1:**
- 🔒 **Máxima seguridad local** - Solo desarrollo personal
- 🚫 **Restricciones corporativas** - Políticas de red estrictas  
- 🐛 **Debugging específico** - Problemas únicos de Windows

**Esta configuración permite:**
- ✅ Desarrollo en cualquier OS
- ✅ Acceso desde dispositivos móviles en la red
- ✅ Compatibilidad con Docker
- ✅ Deploy directo a producción
- ✅ Testing colaborativo en equipo

## 🚀 Deployment en Producción

### ⚡ Deployment Automático (Recomendado)

**El deployment se ejecuta automáticamente cuando:**
- Haces `git push` a la rama `main`
- **⚠️ SOLO en la rama main** - otros branches no activan deployment

```bash
# Workflow normal de desarrollo
git add .
git commit -m "descripción de cambios"
git push origin main  # ← Esto activa el deployment automático
```

**El proceso automático híbrido:**
1. 🔄 GitHub Actions detecta push a `main`
2. 🚀 Se conecta al servidor via SSH
3. 📥 Clona/actualiza código en `/home/azureuser/projects/ezekl-budget`
4. 📦 Instala Node.js e Ionic CLI si es necesario
5. 🔨 Compila frontend Ionic (`ionic build --prod`)
6. 🐳 Construye imagen Docker con FastAPI + frontend compilado + Microsoft ODBC Driver 18
7. 🛑 Detiene contenedor anterior
8. ▶️ Ejecuta nuevo contenedor con `--network host` para acceso a base de datos
9. ✅ Verifica que esté funcionando con health check
10. 📋 Usa archivo .env configurado en el servidor para variables de producción

**Para deployment manual desde GitHub:**
- Ve a **Actions** → **Deploy to Azure Server** → **Run workflow**

### Configuración Inicial del Servidor (Solo una vez)

El servidor ya está configurado, pero para referencia futura o nuevos servidores:

```bash
# Conectar al servidor
ssh -i "path/to/your/key.pem" azureuser@20.246.83.239

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker (si no está instalado)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker azureuser

# Instalar Nginx y Certbot (si no están instalados)
sudo apt install -y nginx certbot python3-certbot-nginx

# Crear directorio de proyectos
mkdir -p /home/azureuser/projects
```

### Configuración de Dominio y SSL

#### 1. Configuración en Cloudflare

**Para este proyecto (budget.ezekl.com):**
- ✅ **Dominio ya configurado** en Cloudflare
- ✅ **DNS configurado** como "DNS Only" (nube gris)
- ✅ **A Record**: budget.ezekl.com → 20.246.83.239

**⚠️ IMPORTANTE**: El dominio debe estar en **"DNS Only"** (nube gris), NO en **"Proxied"** (nube naranja), para que Let's Encrypt pueda generar el certificado SSL correctamente.

#### 2. Configuración en el Servidor

```bash
# 1. Crear directorio para validación SSL
sudo mkdir -p /var/www/budget.ezekl.com
sudo chown -R www-data:www-data /var/www/budget.ezekl.com

# 2. Configurar sitio en Nginx
sudo nano /etc/nginx/sites-available/budget.ezekl.com

# 3. Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/budget.ezekl.com /etc/nginx/sites-enabled/

# 4. Verificar configuración y recargar
sudo nginx -t && sudo systemctl reload nginx

# 5. Generar certificado SSL con Let's Encrypt
sudo certbot certonly --webroot \
  -w /var/www/budget.ezekl.com \
  -d budget.ezekl.com \
  --email ezekiell1988@gmail.com \
  --agree-tos --non-interactive

# 6. Configurar Nginx con SSL y recargar
sudo nginx -t && sudo systemctl reload nginx
```

#### 3. Verificar Configuración

```bash
# Verificar DNS desde el servidor
nslookup budget.ezekl.com
# Debe devolver: 20.246.83.239

# Verificar certificado SSL
sudo certbot certificates
# Debe mostrar certificado válido para budget.ezekl.com

# Probar HTTPS
curl -I https://budget.ezekl.com
# Debe devolver 200 OK con headers SSL
```

### 🪟 Configuración de SSL GRATUITO en Windows Server + IIS

Si tienes Windows Server con IIS, también puedes obtener certificados SSL gratuitos usando **Certify The Web**:

#### 🎯 **Opción Recomendada: Certify The Web (Más Fácil)**

**Certify The Web** es la herramienta **MÁS FÁCIL** para Windows + IIS con interfaz gráfica intuitiva:

##### **1. Instalación (2 minutos)**

```powershell
# Opción A: Microsoft Store (MÁS FÁCIL)
# 1. Abrir Microsoft Store
# 2. Buscar "Certify The Web"
# 3. Click "Install"

# Opción B: Descarga Directa
# 1. Ir a https://certifytheweb.com/
# 2. Click "Download"
# 3. Ejecutar instalador como Administrador
```

##### **2. Configuración Visual (5 minutos)**

```
🖥️ Proceso completamente VISUAL:

1. 📂 Abrir "Certify The Web"
2. 🔍 La app detecta automáticamente todos los sitios IIS
3. ➕ Click "New Certificate"
4. 🎯 Seleccionar tu sitio web de la lista
5. 📝 Verificar dominio y configuración
6. 📧 Ingresar email para Let's Encrypt
7. ✅ Click "Request Certificate"
8. 🎉 ¡LISTO! Certificado creado y configurado automáticamente
```

##### **3. Configuración Automática Incluida**

- ✅ **Binding HTTPS** se crea automáticamente en IIS
- ✅ **Renovación automática** cada 60 días (Task Scheduler)
- ✅ **Monitoreo visual** del estado de certificados
- ✅ **Validación DNS** automática
- ✅ **Backup automático** de configuraciones

##### **4. Dashboard Visual**

```
┌─────────────────────────────────────────┐
│  Certify The Web - Dashboard            │
├─────────────────────────────────────────┤
│  🌐 Certificados Activos:               │
│  ✅ budget.midominio.com (válido 89d)   │
│  ✅ api.midominio.com (válido 85d)      │
│  ⚠️  www.ejemplo.com (expira en 5d)     │
│                                         │
│  📊 Estado: 3 activos, 0 errores        │
│                                         │
│  [➕ Nuevo Certificado]                 │
│  [🔄 Renovar Todos]                     │
│  [⚙️ Configuraciones]                   │
└─────────────────────────────────────────┘
```

#### ⚡ **Opción Avanzada: Win-ACME (Línea de Comandos)**

Para administradores que prefieren CLI:

##### **1. Instalación Win-ACME**

```powershell
# 1. Descargar desde https://www.win-acme.com/
# 2. Extraer en C:\win-acme\
# 3. Ejecutar PowerShell como Administrador
cd C:\win-acme
.\wacs.exe
```

##### **2. Configuración Interactiva**

```powershell
# Menu de Win-ACME:
# N: Create certificate (default settings)
# 2: IIS bindings  
# Seleccionar tu sitio web
# Confirmar dominio (ej: budget.midominio.com)
# Ingresar email para Let's Encrypt notifications
# Confirmar configuración
# ¡Listo! Certificado instalado automáticamente
```

##### **3. Verificación**

```powershell
# Verificar certificado instalado
Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object {$_.Subject -like "*tudominio.com*"}

# Verificar binding HTTPS en IIS
Import-Module WebAdministration
Get-WebBinding -Protocol https

# Verificar renovación automática
Get-ScheduledTask | Where-Object {$_.TaskName -like "*win-acme*"}
```

#### 🆚 **Comparación de Herramientas Windows**

| Característica | **Certify The Web** | Win-ACME | ACME-PS |
|----------------|-------------------|----------|---------|
| **Facilidad de uso** | ⭐⭐⭐⭐⭐ GUI Visual | ⭐⭐⭐ CLI Menu | ⭐⭐ PowerShell |
| **Auto-detección IIS** | ✅ Perfecta | ✅ Básica | ❌ Manual |
| **Monitoreo visual** | ✅ Dashboard | ❌ Solo logs | ❌ Manual |
| **Renovación automática** | ✅ Task Scheduler | ✅ Task Scheduler | 🔧 Script manual |
| **Soporte técnico** | ✅ Comercial + Comunidad | ✅ Comunidad | ✅ Comunidad |
| **Costo** | 🆓 Community (5 certs) | 🆓 Completamente | 🆓 Completamente |

#### 📋 **Requisitos para Windows**

##### **Sistema Operativo**
- ✅ **Windows Server 2016+** (recomendado 2019/2022)
- ✅ **Windows 10/11** (para testing local)
- ✅ **IIS 8.5+** instalado y configurado

##### **Red y Dominio**
- ✅ **Dominio público** apuntando al servidor
- ✅ **Puerto 80 abierto** (para validación Let's Encrypt)  
- ✅ **Puerto 443 abierto** (para HTTPS)
- ✅ **DNS configurado** correctamente

##### **Permisos**
- ✅ **Administrador local** en Windows Server
- ✅ **Permisos IIS** para modificar bindings
- ✅ **Firewall configurado** (puertos 80/443)

#### 🎯 **Recomendación Final**

**Para el 95% de casos, usar Certify The Web:**

✅ **Más fácil** - Interfaz visual intuitiva  
✅ **Más rápido** - Setup en 5 minutos  
✅ **Más confiable** - Menos errores humanos  
✅ **Mejor monitoreo** - Dashboard visual completo  
✅ **Completamente gratuito** - Version Community suficiente  

**Solo usar Win-ACME si:**
- Prefieres línea de comandos
- Necesitas automatización avanzada con scripts
- Quieres máximo control del proceso

#### 💰 **Costos Reales**

```
🆓 COMPLETAMENTE GRATIS:
├── Let's Encrypt: Certificados SSL gratuitos
├── Certify The Web Community: Hasta 5 certificados  
├── Win-ACME: Certificados ilimitados
├── IIS: Incluido en Windows Server
└── Renovación automática: Sin costo adicional

💰 Únicos gastos opcionales:
├── Windows Server: Licencia Microsoft
├── Dominio: Registrar/renovar dominio público
└── Certify The Web Pro: $49/año (certificados ilimitados)
```

### Deployment Automático

El deployment se ejecuta automáticamente cuando haces push a la rama `main`. El proceso:

1. **Push a main** → Activa GitHub Actions
2. **GitHub Actions** se conecta al servidor via SSH
3. **Clona/Actualiza** el código en `/home/azureuser/projects/ezekl-budget`
4. **Construye** la imagen Docker
5. **Detiene** el contenedor anterior (si existe)
6. **Ejecuta** el nuevo contenedor en puerto 8001
7. **Verifica** que esté funcionando correctamente

### Deployment Manual

Si necesitas hacer deployment manual:

```bash
# Conectar al servidor
ssh -i "path/to/your/key.pem" azureuser@20.246.83.239

# Ir al directorio del proyecto
cd /home/azureuser/projects/ezekl-budget

# Actualizar código
git pull origin main

# Reconstruir imagen Docker con Microsoft ODBC Driver 18
docker stop ezekl-budget || true
docker rm ezekl-budget || true
docker build -t ezekl-budget-image .

# Ejecutar con network host para acceso a base de datos localhost
docker run -d --name ezekl-budget --network host --env-file .env ezekl-budget-image

# Verificar que esté funcionando
docker ps | grep ezekl-budget
docker logs ezekl-budget --tail 20
curl -s http://localhost:8001/api/health
```

## 🔧 Configuración para Múltiples Proyectos

### Puertos Recomendados

Para evitar conflictos, usa esta convención de puertos:

```
8000-8099: APIs principales
8100-8199: Servicios de autenticación  
8200-8299: Dashboards y frontends
8300-8399: Microservicios
```

### Configurar Nuevo Proyecto

#### 1. **Preparación Local**
```bash
git clone https://github.com/ezekiell1988/ezekl-budget.git nuevo-proyecto
cd nuevo-proyecto
```

#### 2. **Configurar Puerto y Variables**
```bash
# Cambiar puerto en .env (ejemplo: 8002, 8003, etc.)
# Cambiar puerto en .github/workflows/deploy.yml
# Cambiar PROJECT_NAME en el workflow
```

#### 3. **Configuración en Cloudflare** 
**⚠️ CRÍTICO: Configurar ANTES de generar SSL**

1. **Agregar subdominio** en Cloudflare:
   - Tipo: `A`
   - Nombre: `nuevo-proyecto` (para nuevo-proyecto.ezekl.com)
   - Valor: `20.246.83.239`
   - **Proxy status**: 🟤 **DNS only** (nube GRIS) ← MUY IMPORTANTE

2. **NO usar Proxied** (nube naranja) porque:
   - Let's Encrypt no puede validar el dominio
   - El SSL de Cloudflare interfiere con el nuestro
   - Los WebSockets pueden tener problemas

#### 4. **Configurar GitHub Secrets** para el nuevo repositorio

#### 5. **Crear configuración Nginx**:

```bash
# Ejemplo para nuevo-proyecto.ezekl.com en puerto 8002
sudo tee /etc/nginx/sites-available/nuevo-proyecto.ezekl.com << 'EOF'
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name nuevo-proyecto.ezekl.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/nuevo-proyecto.ezekl.com;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name nuevo-proyecto.ezekl.com;
    
    ssl_certificate /etc/letsencrypt/live/nuevo-proyecto.ezekl.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nuevo-proyecto.ezekl.com/privkey.pem;
    
    # SSL y security headers (igual que budget.ezekl.com)
    
    location / {
        proxy_pass http://localhost:8002;  # ← Cambiar puerto aquí
        # ... resto de configuración igual
    }
}
EOF

# Generar SSL
sudo mkdir -p /var/www/nuevo-proyecto.ezekl.com
sudo certbot certonly --webroot -w /var/www/nuevo-proyecto.ezekl.com -d nuevo-proyecto.ezekl.com

# Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/nuevo-proyecto.ezekl.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

5. **Configurar GitHub Secrets** para el nuevo proyecto
6. **Hacer push** para activar deployment automático

## 📊 Monitoreo

### Verificar Estado de Contenedores

```bash
# Ver contenedores activos
docker ps

# Ver logs de un proyecto específico
docker logs ezekl-budget -f

# Verificar uso de recursos
docker stats
```

### Verificar SSL

```bash
# Verificar certificado
sudo certbot certificates

# Renovar certificados (automático via cron)
sudo certbot renew --dry-run
```

### Verificar Nginx

```bash
# Estado del servicio
sudo systemctl status nginx

# Verificar configuración
sudo nginx -t

# Ver logs de acceso y error
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🛠️ Comandos Útiles

### Gestión de Contenedores

```bash
# Ver todos los contenedores
docker ps -a

# Detener todos los contenedores
docker stop $(docker ps -q)

# Limpiar contenedores no utilizados
docker container prune

# Limpiar imágenes no utilizadas
docker image prune -a
```

### Gestión de Nginx

```bash
# Recargar configuración sin downtime
sudo systemctl reload nginx

# Reiniciar Nginx completamente
sudo systemctl restart nginx

# Verificar sitios habilitados
ls -la /etc/nginx/sites-enabled/
```

### Logs y Debug

```bash
# Logs de deployment desde GitHub Actions
# (Ver en GitHub → Actions → último workflow)

# Logs de aplicación
docker logs ezekl-budget --tail 100 -f

# Logs de sistema
sudo journalctl -u nginx -f
sudo journalctl -u docker -f
```

## 🔧 Cambios Recientes (Octubre 2025)

### 🪟 Compatibilidad con Windows - WebSockets y Event Loop (Octubre 2025)

**Problema identificado**: uvloop no es compatible con Windows, causando fallos en WebSockets y servidor uvicorn.

**Solución implementada**:

#### 1. **Detección automática de sistema operativo en main.py**
```python
# Configuración específica para WebSockets compatible con Windows
if platform.system() != "Windows":
    config_kwargs["loop"] = "uvloop"  # Usar uvloop (más rápido) en Mac/Linux
else:
    config_kwargs["loop"] = "asyncio"  # Usar asyncio (estándar) en Windows
```

#### 2. **Dependencies condicionales en requirements.txt**
```python
uvloop==0.21.0; sys_platform != "win32"  # Solo instalar uvloop en sistemas Unix/Linux
```

#### 3. **Configuración optimizada para WebSockets multiplataforma**
- ✅ **Windows**: asyncio event loop (nativo de Python)
- ✅ **Mac/Linux**: uvloop event loop (hasta 2-4x más rápido)
- ✅ **Parámetros WebSocket**: ws_ping_interval, ws_ping_timeout, ws_max_size configurados
- ✅ **Reload deshabilitado**: Evita problemas específicos de Windows

#### 4. **Beneficios obtenidos**
- 🪟 **Compatibilidad total con Windows** - WebSockets funcionan correctamente
- 🚀 **Rendimiento optimizado** - uvloop en Mac/Linux para máxima velocidad
- 🔄 **Código universal** - Una sola base de código para todos los sistemas
- 🛠️ **Desarrollo local** - Funciona igual en Windows, Mac y Linux

### � Mejora de Modelos Pydantic y Documentación Swagger (Octubre 2025)

**Refactorización de modelos implementada**:

#### 1. **Separación de Modelos Request/Response** (`app/models/`)
- ✅ **`requests.py`** - Modelos de entrada con validación completa
- ✅ **`responses.py`** - Modelos de salida con documentación detallada
- ✅ **Field descriptions** con ejemplos y validaciones específicas
- ✅ **Documentación Swagger mejorada** automáticamente generada

#### 2. **EmailSendRequest - Modelo de Entrada Optimizado**
```python
class EmailSendRequest(BaseModel):
    to: List[EmailStr] = Field(..., description="Lista de destinatarios", example=["user@example.com"])
    subject: str = Field(..., min_length=1, max_length=255, description="Asunto del email")
    html_content: Optional[str] = Field(None, description="Contenido HTML del email")
    text_content: Optional[str] = Field(None, description="Contenido en texto plano")
    cc: Optional[List[EmailStr]] = Field(None, description="Lista de destinatarios en copia")
    bcc: Optional[List[EmailStr]] = Field(None, description="Lista de destinatarios en copia oculta")
    reply_to: Optional[EmailStr] = Field(None, description="Dirección de respuesta")
    # from_address removido - siempre viene del .env por seguridad
```

#### 3. **WebhookEvent - Modelos para Azure Event Grid**
```python
class WebhookEventRequest(BaseModel):
    # Modelo flexible para recibir eventos de Azure Event Grid
    
class WebhookEventResponse(BaseModel):
    validationResponse: Optional[str] = Field(None, description="Código de validación para Azure Event Grid")
    ok: Optional[bool] = Field(None, description="Estado del procesamiento")
    message: Optional[str] = Field(None, description="Mensaje descriptivo del resultado")
    event_type: Optional[str] = Field(None, description="Tipo de evento procesado")
    processed_at: Optional[str] = Field(None, description="Timestamp del procesamiento")
```

#### 4. **Mejoras en Endpoints de Email**
- ✅ **POST /api/email/send** con validación Pydantic completa
- ✅ **POST /api/email/webhook** con modelos específicos (no más Request genérico)
- ✅ **Configuración from_address** desde .env (mayor seguridad)
- ✅ **Campos null removidos** de respuestas (message_id, recipients_count)
- ✅ **Documentación Swagger automática** con ejemplos y descripciones

#### 5. **Beneficios Obtenidos**
- 📚 **Swagger más informativo** - Documentación automática con Field descriptions
- 🔒 **Mayor seguridad** - from_address no expuesto en API, viene del .env
- 🧹 **Respuestas limpias** - Sin campos null innecesarios
- 🔧 **Mantenibilidad mejorada** - Separación clara entre entrada y salida
- ⚡ **Validación robusta** - Pydantic v2 con validaciones específicas por campo

### �🚀 Nueva Funcionalidad: Cliente HTTP Asíncrono, Procesamiento y Envío de Emails

**Características implementadas**:

- ✅ **Cliente HTTP asíncrono** - aiohttp para operaciones no bloqueantes
- ✅ **Procesamiento de emails** - Azure Event Grid webhooks y Communication Services
- ✅ **API endpoints** - /api/email/send y /api/email/webhook
- ✅ **Modelos Pydantic** - Validaciones y documentación Swagger









### ✅ Resolución de Error 502 - Missing ODBC Drivers

**Problema identificado**: El contenedor Docker no tenía los Microsoft ODBC Driver 18 instalados, causando:
```
ImportError: libodbc.so.2: cannot open shared object file: No such file or directory
```

**Solución implementada**:

#### 1. **Dockerfile actualizado** con drivers ODBC
```dockerfile
# Instalar dependencias del sistema y Microsoft ODBC Driver
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    gnupg2 \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.asc.gpg \
    && echo "deb [arch=amd64] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*
```

#### 2. **Configuración de red Docker**
- **Problema**: Contenedor no podía conectar a `localhost` del servidor
- **Solución**: Usar `--network host` para acceso directo a localhost
```bash
docker run -d --name ezekl-budget --network host --env-file .env ezekl-budget-image
```

#### 3. **Configuración .env en producción**
El archivo `.env` debe estar configurado en el servidor con variables de producción:
```bash
# En el servidor: /home/azureuser/projects/ezekl-budget/.env
DB_HOST=localhost          # En producción usar localhost
DB_PORT=1433
DB_NAME=budgetdb
DB_USER=budgetuser
DB_PASSWORD=Budget2024!
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUST_CERT=yes
```

#### 4. **Verificación del health check**
```bash
# Endpoint que verifica base de datos
curl https://budget.ezekl.com/api/health
```

**Estado actual**: ✅ **Completamente funcional** - API y base de datos operando correctamente

### 📚 Lecciones Aprendidas - Mejores Prácticas de Deployment

#### 🔄 **Problema: Git Sync Inconsistente**
- **Causa**: `git reset --hard` solo no garantiza sincronización completa de archivos
- **Solución**: Agregar `git clean -fd` para limpiar archivos no trackeados
- **Prevención**: Siempre usar secuencia completa: `fetch` → `reset --hard` → `clean -fd`

#### 🐳 **Problema: Docker Cache Corrupto**  
- **Causa**: Docker reutiliza layers cache incluso con archivos actualizados
- **Solución**: Usar `--no-cache` en builds críticos + limpieza previa de imágenes
- **Prevención**: Limpiar imágenes antiguas antes de rebuild: `docker rmi` + `docker image prune -af`

#### 🔍 **Problema: GitHub Action "Falso Positivo"**
- **Causa**: Workflow reporta éxito pero usa archivos desactualizados
- **Solución**: Verificación post-build de archivos críticos (Dockerfile, etc.)
- **Prevención**: Agregar verificaciones de integridad en el workflow

#### ⚡ **Checklist de Deployment Seguro**
```bash
# Antes de hacer push crítico:
1. Verificar cambios locales: git status && git diff
2. Confirmar Dockerfile actualizado: grep "ODBC Driver" Dockerfile  
3. Push y monitorear GitHub Actions
4. Verificar aplicación post-deployment: curl https://budget.ezekl.com/api/health
5. Si falla, revisar logs: docker logs ezekl-budget --tail 30
```

### 🔄 GitHub Action Actualizado

**Cambios en el workflow de deployment**:

1. **Variables de entorno completas**: El .env ahora incluye toda la configuración de base de datos
2. **Network host**: Contenedor ejecuta con `--network host` para acceso directo a localhost 
3. **Health check mejorado**: Verifica que tanto API como base de datos estén funcionando
4. **Nombre de imagen actualizado**: Usa `ezekl-budget-image` para mayor claridad
5. **Logs detallados**: Mejor troubleshooting en caso de errores
6. **Limpieza completa**: Fuerza rebuild completo de imágenes Docker con `--no-cache`
7. **Sincronización robusta**: Git reset forzado con limpieza para asegurar archivos actualizados

**Proceso completo del workflow mejorado**:
```yaml
# 1. Git reset --hard + clean -fd (forzar sincronización)
# 2. Crear .env con variables completas (incluye BD)
# 3. Limpieza completa de imágenes Docker existentes
# 4. Construir imagen Docker desde cero (--no-cache) con ODBC Driver 18
# 5. Verificar instalación de drivers ODBC en imagen  
# 6. Ejecutar contenedor con --network host
# 7. Health check con reintentos y timeout
# 8. Mostrar URLs de acceso público
```

### 📁 Refactorización de Estructura de Código (Octubre 2025)

**Mejora implementada**: Reorganización completa de la estructura del backend para mejor mantenimiento y escalabilidad.

#### **Antes (Estructura Plana)**
```
app/
├── main.py        # Todo en un solo archivo
├── settings.py    # Configuraciones mezcladas
└── database.py    # Base de datos y lógica
```

#### **Después (Estructura Organizada + API Modular)**
```
app/
├── __init__.py                 # Módulo principal
├── main.py                     # Solo servidor FastAPI + frontend
├── core/                       # 🔧 Configuración central
│   ├── __init__.py
│   └── config.py               # settings.py → config.py
├── database/                   # 💾 Acceso a datos
│   ├── __init__.py
│   └── connection.py           # database.py → connection.py
├── models/                     # 📝 Modelos Pydantic
│   ├── __init__.py
│   └── responses.py            # Extraído de main.py
└── api/                        # 🌐 API modular con routers estándar FastAPI
    ├── __init__.py             # Routers con prefijos: /api y /ws
    ├── routes/                 # 🛤️ REST API endpoints
    │   └── __init__.py         # Router base (sin prefijo)
    └── websockets/             # 📡 WebSockets en tiempo real
        └── __init__.py         # Router base (sin prefijo)
```





#### **Estructura de Escalabilidad Futura**
```
api/
├── __init__.py                 # Routers con prefijos centralizados
├── routes/                     # 🛤️ REST API endpoints (prefijo /api en padre)
│   ├── __init__.py             # Router base (sin prefijo)
│   ├── auth.py                 # Router para /auth/* → /api/auth/*
│   ├── budget.py               # Router para /budget/* → /api/budget/*
│   └── analytics.py            # Router para /analytics/* → /api/analytics/*
└── websockets/                 # 📡 WebSockets (prefijo /ws en padre)
    ├── __init__.py             # Router base (sin prefijo)
    ├── realtime.py             # Router para "/" → /ws/
    ├── chat.py                 # Router para "/chat" → /ws/chat
    └── notifications.py        # Router para "/notifications" → /ws/notifications

# En api/__init__.py:
# api_router = APIRouter(prefix="/api")
# websockets_router_with_prefix = APIRouter(prefix="/ws")
```

#### **Arquitectura de Routers Consistente (Noviembre 2025)**

**Principio aplicado**: Prefijos centralizados en el nivel padre para máxima consistencia y mantenibilidad.

```python
# ✅ Patrón consistente:
# 1. Routers hijos SIN prefijos (solo lógica)
# 2. Prefijos aplicados en el nivel padre
# 3. include_router() estándar en main.py

# api/routes/__init__.py
router = APIRouter()  # ← Sin prefijo
@router.get("/credentials")  # Endpoint base
@router.get("/health")

# api/websockets/__init__.py  
router = APIRouter()  # ← Sin prefijo
@router.websocket("/")  # WebSocket base

# api/__init__.py - PREFIJOS CENTRALIZADOS
api_router = APIRouter(prefix="/api")  # ← Prefijo aquí
api_router.include_router(routes_router)

websockets_router_with_prefix = APIRouter(prefix="/ws")  # ← Prefijo aquí  
websockets_router_with_prefix.include_router(websockets_router)

# main.py - 100% FastAPI estándar
app.include_router(api_router)                    # → /api/*
app.include_router(websockets_router_with_prefix) # → /ws/*
```

**Ventajas obtenidas**:
- ✅ **Patrón uniforme** - Todos los prefijos en el mismo nivel
- ✅ **Fácil refactoring** - Cambiar prefijos en un solo lugar
- ✅ **Escalabilidad clara** - Agregar sub-prefijos es trivial
- ✅ **100% FastAPI estándar** - Sin funciones custom

#### **Próximos Pasos Recomendados**
- 🔧 Crear `services/` para lógica de negocio compleja
- 🗂️ Organizar stored procedures en `database/procedures/`
- 🧪 Agregar `tests/` con estructura similar a `api/`
- 🔐 Implementar `api/routes/auth.py` para autenticación Microsoft
- 📊 Agregar `api/routes/budget.py` para gestión de presupuesto

### ⚠️ Problema Identificado: Sincronización de Archivos

**Issue crítico detectado**: Algunos deployments fallaban porque el `git reset --hard` no sincronizaba correctamente todos los archivos, especialmente el Dockerfile actualizado.

**Síntomas**:
- Contenedor se crashea con `ImportError: libodbc.so.2`
- Dockerfile en servidor no tiene drivers ODBC
- Imagen Docker usa versión anterior sin drivers

**Solución implementada**:
```bash
# GitHub Action mejorado con limpieza forzada
git fetch origin
git reset --hard origin/main
git clean -fd  # ← Limpia archivos no trackeados

# Docker rebuild forzado
docker rmi $PROJECT_NAME-image || true
docker build --no-cache -t $PROJECT_NAME-image .
```

---

## 🐛 Troubleshooting

### Problemas Comunes

#### El deployment falla en GitHub Actions
```bash
# 1. Verificar que los GitHub Secrets estén configurados
# 2. Revisar logs en GitHub Actions
# 3. Verificar conectividad SSH manual:
ssh -i "clave.pem" azureuser@20.246.83.239

# 4. Verificar espacio en disco del servidor
ssh -i "clave.pem" azureuser@20.246.83.239 "df -h"
```

#### La aplicación no responde
```bash
# 1. Verificar que el contenedor esté corriendo
ssh -i "clave.pem" azureuser@20.246.83.239 "docker ps | grep ezekl-budget"

# 2. Ver logs del contenedor
ssh -i "clave.pem" azureuser@20.246.83.239 "docker logs ezekl-budget --tail 50"

# 3. Verificar que Nginx esté funcionando
ssh -i "clave.pem" azureuser@20.246.83.239 "sudo systemctl status nginx"

# 4. Restart manual si es necesario
ssh -i "clave.pem" azureuser@20.246.83.239 "docker restart ezekl-budget"
```

#### SSL no funciona

**Problema común**: Dominio en Cloudflare configurado como "Proxied" 🟠

```bash
# 1. PRIMERO: Verificar configuración DNS en Cloudflare
# - Ir a Cloudflare Dashboard
# - Verificar que el A Record esté en "DNS only" (nube GRIS)
# - Si está en "Proxied" (nube NARANJA), cambiarlo a "DNS only"
# - Esperar 5 minutos para propagación DNS

# 2. Verificar DNS desde el servidor
ssh -i "clave.pem" azureuser@20.246.83.239 "nslookup budget.ezekl.com"
# Debe devolver la IP real del servidor: 20.246.83.239

# 3. Verificar certificado
ssh -i "clave.pem" azureuser@20.246.83.239 "sudo certbot certificates"

# 4. Si el certificado falló, regenerarlo
ssh -i "clave.pem" azureuser@20.246.83.239 "sudo certbot delete --cert-name budget.ezekl.com"
ssh -i "clave.pem" azureuser@20.246.83.239 "sudo certbot certonly --webroot -w /var/www/budget.ezekl.com -d budget.ezekl.com --email ezekiell1988@gmail.com"

# 5. Renovar certificado manualmente si existe
ssh -i "clave.pem" azureuser@20.246.83.239 "sudo certbot renew"
```

#### Error "No such authorization" en Certbot
```bash
# Esto suele pasar cuando Cloudflare está en modo "Proxied"
# 1. Cambiar a "DNS only" en Cloudflare
# 2. Esperar propagación DNS
# 3. Verificar que el dominio apunte directamente al servidor
# 4. Intentar generar certificado nuevamente
```

#### Puerto ocupado
```bash
# Ver qué está usando un puerto específico
ssh -i "clave.pem" azureuser@20.246.83.239 "sudo lsof -i :8001"

# Ver todos los puertos en uso
ssh -i "clave.pem" azureuser@20.246.83.239 "ss -tlnp | grep LISTEN"
```

#### Error de importación ODBC en Docker
```bash
# Si aparece: "ImportError: libodbc.so.2: cannot open shared object file"

# 1. Verificar que la imagen Docker tenga los drivers instalados
ssh -i "clave.pem" azureuser@20.246.83.239 "docker exec ezekl-budget odbcinst -q -d"
# Debe mostrar: [ODBC Driver 18 for SQL Server]

# 2. Si no están instalados, reconstruir la imagen
ssh -i "clave.pem" azureuser@20.246.83.239 "cd /home/azureuser/projects/ezekl-budget && docker build -t ezekl-budget-image ."

# 3. Verificar que el contenedor use --network host
ssh -i "clave.pem" azureuser@20.246.83.239 "docker inspect ezekl-budget | grep NetworkMode"
# Debe mostrar: "NetworkMode": "host"

# 4. Verificar logs del contenedor
ssh -i "clave.pem" azureuser@20.246.83.239 "docker logs ezekl-budget --tail 20"
```

#### Conexión a base de datos falla
```bash
# 1. Verificar que SQL Server esté ejecutándose
ssh -i "clave.pem" azureuser@20.246.83.239 "sudo systemctl status mssql-server"

# 2. Verificar conectividad desde el contenedor
ssh -i "clave.pem" azureuser@20.246.83.239 "docker exec ezekl-budget ping -c 2 localhost"

# 3. Verificar variables de entorno del contenedor
ssh -i "clave.pem" azureuser@20.246.83.239 "docker exec ezekl-budget env | grep DB_"

# 4. Probar conexión directa
ssh -i "clave.pem" azureuser@20.246.83.239 "curl -s http://localhost:8001/api/health"
```

#### Deployment falló pero GitHub Action mostró éxito
```bash
# Si GitHub Action dice "éxito" pero la app no funciona:

# 1. Verificar si los archivos se sincronizaron correctamente
ssh -i "clave.pem" azureuser@20.246.83.239 "cd /home/azureuser/projects/ezekl-budget && git log --oneline -3"

# 2. Verificar si el Dockerfile tiene los drivers ODBC
ssh -i "clave.pem" azureuser@20.246.83.239 "cd /home/azureuser/projects/ezekl-budget && grep -A 5 'Microsoft ODBC Driver' Dockerfile"

# 3. Forzar sincronización manual si es necesario
ssh -i "clave.pem" azureuser@20.246.83.239 "cd /home/azureuser/projects/ezekl-budget && git fetch origin && git reset --hard origin/main && git clean -fd"

# 4. Rebuild completo manual
ssh -i "clave.pem" azureuser@20.246.83.239 "cd /home/azureuser/projects/ezekl-budget && docker stop ezekl-budget && docker rm ezekl-budget && docker rmi ezekl-budget-image && docker build --no-cache -t ezekl-budget-image . && docker run -d --name ezekl-budget --network host --env-file .env ezekl-budget-image"
```

#### Contenedor en estado "Restarting" después del deployment
```bash
# Si el contenedor se reinicia continuamente:

# 1. Ver logs detallados del crash
ssh -i "clave.pem" azureuser@20.246.83.239 "docker logs ezekl-budget --tail 50"

# 2. Si aparece ImportError de libodbc.so.2:
#    → El Dockerfile no se actualizó correctamente
#    → Ejecutar rebuild manual (ver comando arriba)

# 3. Verificar que la imagen tenga los drivers instalados
ssh -i "clave.pem" azureuser@20.246.83.239 "docker run --rm ezekl-budget-image odbcinst -q -d"
#    Debe mostrar: [ODBC Driver 18 for SQL Server]

# 4. Si no aparecen los drivers, la imagen está corrupta
#    → Hacer limpieza completa y rebuild
ssh -i "clave.pem" azureuser@20.246.83.239 "docker system prune -af && cd /home/azureuser/projects/ezekl-budget && docker build --no-cache -t ezekl-budget-image ."
```

### Desarrollo en Ramas

**⚠️ Importante**: Solo la rama `main` activa deployment automático.

```bash
# Desarrollo en feature branch (NO se deploya)
git checkout -b feature/nueva-funcionalidad
git add .
git commit -m "nueva funcionalidad"
git push origin feature/nueva-funcionalidad  # ← NO activa deployment

# Cuando esté listo para producción
git checkout main
git merge feature/nueva-funcionalidad
git push origin main  # ← AQUÍ se activa el deployment automático
```

## �🔒 Seguridad

### Certificados SSL

- **Renovación automática** configurada via cron
- **Certificados válidos** por 90 días
- **Renovación** 30 días antes del vencimiento

### Headers de Seguridad

El Nginx está configurado con headers de seguridad:

- `Strict-Transport-Security`
- `X-Frame-Options`
- `X-Content-Type-Options`
- `X-XSS-Protection`
- `Referrer-Policy`

### Firewall y Acceso

- Puerto **22** (SSH): Restringido por clave privada
- Puerto **80** (HTTP): Redirige a HTTPS
- Puerto **443** (HTTPS): Acceso público via SSL
- Puertos **8000-8399**: Solo acceso interno (localhost)

## 📚 API Endpoints

### Principales

- `GET /` → Redirige a `/docs`
- `GET /docs` → Documentación interactiva Swagger
- `GET /redoc` → Documentación ReDoc
- `GET /api/health` → Health check del servicio y conexión a base de datos
- `WebSocket /ws/` → Conexión en tiempo real con ping-pong

### Específicos del Proyecto

- `GET /api/credentials` → Obtiene credenciales de Azure OpenAI (sin API key)
- `POST /api/email/webhook` → Webhook para recibir eventos de email desde Azure Event Grid
- `POST /api/email/send` → Endpoint para enviar emails usando Azure Communication Services

### Autenticación (Sistema de Login)

- `POST /api/auth/request-token` → Solicita token de autenticación por email (con modelos Pydantic)
- `POST /api/auth/login` → Completa autenticación con token y genera JWE de acceso
- `GET /api/auth/verify-token` → **[PRIVADO]** Obtiene datos del usuario autenticado 
- `POST /api/auth/refresh-token` → **[PRIVADO]** Extiende la expiración del token actual (+24h)
- `POST /api/auth/logout` → Cierra sesión (limpieza del lado cliente)

### Cuentas Contables (Catálogo)

- `GET /api/accounting-accounts` → **[PRIVADO]** Lista paginada de cuentas contables del catálogo
- `GET /api/accounting-accounts/{id}` → **[PRIVADO]** Obtiene una cuenta contable específica por ID

#### Funcionalidades de Cuentas Contables:

**Paginación y Búsqueda:**
- ✅ **Paginación configurable** - Parámetros `page` (1-∞) y `itemPerPage` (1-100)
- ✅ **Búsqueda por nombre** - Parámetro `search` para filtrar cuentas por nombre
- ✅ **Ordenamiento flexible** - Parámetro `sort` con múltiples opciones

**Parámetros de ordenamiento disponibles:**
- `idAccountingAccount_asc` → Por ID ascendente
- `codeAccountingAccount_asc` → Por código ascendente (por defecto)
- `codeAccountingAccount_desc` → Por código descendente
- `nameAccountingAccount_asc` → Por nombre ascendente
- `nameAccountingAccount_desc` → Por nombre descendente

**Ejemplos de uso:**
```bash
# Obtener primeras 10 cuentas (valores por defecto)
GET /api/accounting-accounts

# Buscar cuentas que contengan "activo" en el nombre
GET /api/accounting-accounts?search=activo

# Página 2 con 25 elementos por página
GET /api/accounting-accounts?page=2&itemPerPage=25

# Ordenar por nombre descendente
GET /api/accounting-accounts?sort=nameAccountingAccount_desc

# Combinación de parámetros
GET /api/accounting-accounts?search=caja&sort=codeAccountingAccount_asc&page=1&itemPerPage=5
```

**Estructura de respuesta:**
```json
{
  "total": 6,
  "data": [
    {
      "idAccountingAccount": 1,
      "codeAccountingAccount": "001",
      "nameAccountingAccount": "Activo"
    },
    {
      "idAccountingAccount": 2,
      "codeAccountingAccount": "002", 
      "nameAccountingAccount": "Pasivo"
    }
  ]
}
```

**Autenticación requerida:** Todos los endpoints requieren header `Authorization: Bearer {jwt_token}`

### Integración con Azure Event Grid (Emails)

El webhook `/api/email/webhook` maneja eventos de Azure Event Grid para procesamiento de emails:

#### Tipos de eventos soportados:

**1. Validación de suscripción**
```json
{
  "aeg-event-type": "SubscriptionValidation",
  "data": [
    {
      "validationCode": "12345678-abcd-1234-abcd-123456789012"
    }
  ]
}
```

**2. Emails entrantes**
```json
{
  "aeg-event-type": "Notification",
  "eventType": "Microsoft.Communication.InboundEmailReceived",
  "data": {
    "to": ["recipient@example.com"],
    "from": "sender@example.com",
    "subject": "Asunto del email",
    "emailContentUrl": "https://storage.azure.com/path/to/mime/content"
  }
}
```

#### Características del procesamiento:

- ✅ **Descarga asíncrona** de contenido MIME usando `aiohttp`
- ✅ **Parsing completo** de emails (texto plano, HTML, adjuntos)
- ✅ **Logging detallado** de todos los eventos
- ✅ **Manejo robusto de errores** sin afectar Azure Event Grid
- ✅ **Procesamiento de adjuntos** (preparado para implementación)
- ✅ **Reportes de entrega** y manejo de rebotes

### Envío de Emails (Azure Communication Services)

El endpoint `/api/email/send` permite enviar emails usando Azure Communication Services:

#### Request Body (EmailSendRequest):
```json
{
  "to": ["recipient1@example.com", "recipient2@example.com"],
  "subject": "Asunto del email",
  "html_content": "<h1>Contenido HTML</h1><p>Este es un email con formato.</p>",
  "text_content": "Contenido en texto plano como alternativa",
  "cc": ["cc@example.com"],
  "bcc": ["bcc@example.com"],
  "reply_to": "noreply@ezekl.com"
}
```
*Nota: `from_address` se configura automáticamente desde variables de entorno por seguridad*

#### Response (EmailSendResponse):
```json
{
  "success": true,
  "message": "Email enviado exitosamente",
  "operation_id": "operation-abcd-1234"
}
```
*Nota: Campos `message_id` y `recipients_count` removidos para limpiar respuesta*

#### Características del envío:

- ✅ **Validación automática** de direcciones de email usando Pydantic EmailStr
- ✅ **Soporte dual** para contenido HTML y texto plano
- ✅ **Múltiples destinatarios** - to, cc, bcc y reply_to
- ✅ **Configuración segura** - from_address desde .env (no expuesto en API)
- ✅ **Modelos Pydantic** - EmailSendRequest/EmailSendResponse con Field descriptions
- ✅ **Swagger mejorado** - Documentación automática con ejemplos y validaciones
- ✅ **Respuestas limpias** - Sin campos null innecesarios
- ✅ **Manejo robusto de errores** sin afectar la API

### Sistema de Autenticación (JWE con Email) - **ACTUALIZADO**

El sistema implementa autenticación de dos pasos con tokens enviados por email y **JWE (JSON Web Encryption)** para sesiones seguras. Todos los endpoints usan **modelos Pydantic** para validación automática y documentación completa.

#### Flujo de Autenticación

**1. Solicitar Token de Acceso**
```bash
curl -X POST https://budget.ezekl.com/api/auth/request-token \
  -H "Content-Type: application/json" \
  -d '{"codeLogin": "S"}'
```

Response:
```json
{
  "success": true,
  "message": "Token enviado por email exitosamente",
  "tokenGenerated": true
}
```

**2. Completar Login y Obtener JWE**
```bash
curl -X POST https://budget.ezekl.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "codeLogin": "S",
    "token": "12345"
  }'
```

Response (LoginResponse):
```json
{
  "success": true,
  "message": "Autenticación exitosa",
  "user": {
    "idLogin": 1,
    "codeLogin": "S",
    "nameLogin": "Ezequiel Baltodano Cubillo",
    "phoneLogin": "50683681485",
    "emailLogin": "ezekiell1988@hotmail.com"
  },
  "accessToken": "eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2R0NNIn0...",
  "expiresAt": "2025-10-06T19:10:00.646981+00:00"
}
```

**3. Verificar Sesión y Obtener Datos del Usuario (Endpoint Privado)**
```bash
curl -X GET https://budget.ezekl.com/api/auth/verify-token \
  -H "Authorization: Bearer eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2R0NNIn0..."
```

Response (VerifyTokenResponse):
```json
{
  "user": {
    "idLogin": 1,
    "codeLogin": "S", 
    "nameLogin": "Ezequiel Baltodano Cubillo",
    "phoneLogin": "50683681485",
    "emailLogin": "ezekiell1988@hotmail.com"
  },
  "expiresAt": "2025-10-06T19:10:00+00:00",
  "issuedAt": "2025-10-05T19:10:00+00:00"
}
```

**4. Renovar/Extender Token (Endpoint Privado)**
```bash
curl -X POST https://budget.ezekl.com/api/auth/refresh-token \
  -H "Authorization: Bearer eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2R0NNIn0..."
```

Response (LoginResponse):
```json
{
  "success": true,
  "message": "Token renovado exitosamente",
  "user": {
    "idLogin": 1,
    "codeLogin": "S",
    "nameLogin": "Ezequiel Baltodano Cubillo", 
    "phoneLogin": "50683681485",
    "emailLogin": "ezekiell1988@hotmail.com"
  },
  "accessToken": "eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2R0NNIn0...",
  "expiresAt": "2025-10-06T21:43:15+00:00"
}
```

**5. Cerrar Sesión**
```bash
curl -X POST https://budget.ezekl.com/api/auth/logout
```

Response (LogoutResponse):
```json
{
  "success": true,
  "message": "Sesión cerrada exitosamente"
}
```

#### Características del Sistema de Auth **[ACTUALIZADO 2025]**

- ✅ **Autenticación de 2 pasos** - Token por email + verificación
- ✅ **Tokens temporales** - Expiración configurable (30 minutos por defecto)  
- ✅ **JWE seguros** - Encriptación completa con algoritmo A256KW + A256GCM
- ✅ **Email en background** - Cola asíncrona sin bloquear API (1 segundo vs 5-10s antes)
- ✅ **Modelos Pydantic** - Validación automática y documentación completa
- ✅ **Renovación automática** - Sistema automático de extensión de sesión sin reautenticación
- ✅ **Renovación manual** - Botón para extender sesión cuando el usuario lo requiera
- ✅ **Detección inteligente** - Renueva automáticamente solo si el token expira pronto (<1 hora)
- ✅ **Base de datos integrada** - Stored procedures con SQL Server
- ✅ **Endpoint privado** - `GET /verify-token` con autenticación Bearer
- ✅ **Tokens de un solo uso** - Se eliminan automáticamente después del login
- ✅ **Clave de 256 bits** - Configuración segura para algoritmos JWE
- ✅ **Documentación automática** - Swagger/OpenAPI con todos los esquemas

#### Sistema de Renovación Automática de Tokens

El endpoint `POST /api/auth/refresh-token` permite extender la vida útil de tokens JWE sin reautenticación:

- **Funcionalidad**: Valida token actual y genera nuevo JWE con +24 horas de vida
- **Autenticación**: Requiere header `Authorization: Bearer {token_actual}`
- **Respuesta**: Mismo formato que login (LoginResponse) con nuevo token
- **Casos de uso**: Mantener sesiones activas, evitar relogin innecesario en aplicaciones SPA

#### Modelos Pydantic de Autenticación

El sistema usa modelos Pydantic profesionales ubicados en `/app/models/auth.py`:

- **`RequestTokenRequest`** - Solicitud de token temporal
- **`RequestTokenResponse`** - Respuesta de token generado  
- **`LoginRequest`** - Datos de login (codeLogin + token de 5 dígitos)
- **`LoginResponse`** - Respuesta completa con JWE y datos del usuario
- **`UserData`** - Información del usuario autenticado
- **`VerifyTokenResponse`** - Datos del usuario + fechas de token
- **`LogoutResponse`** - Confirmación de cierre de sesión
- **`AuthErrorResponse`** - Errores de autenticación (401, etc.)

**Beneficios:**
- 🔍 **Validación automática** - Error 422 para datos inválidos
- 📚 **Documentación completa** - Ejemplos en Swagger UI
- 🛡️ **Type Safety** - IntelliSense en desarrollo
- ⚡ **Rendimiento** - Validación rápida con Pydantic V2

### Testing de Endpoints

```bash
# Health check (incluye estado de base de datos y cola de emails)
curl https://budget.ezekl.com/api/health

# Credenciales (sin mostrar API key)
curl https://budget.ezekl.com/api/credentials

# Test completo de autenticación
# 1. Solicitar token
curl -X POST http://localhost:8001/api/auth/request-token \
  -H "Content-Type: application/json" \
  -d '{"codeLogin": "S"}'

# 2. Verificar en email y usar token recibido
curl -X POST http://localhost:8001/api/auth/verify-token \
  -H "Content-Type: application/json" \
  -d '{"codeLogin": "S", "token": "TOKEN_DEL_EMAIL"}'

# Documentación interactiva
open https://budget.ezekl.com/docs

# Testing local con detección de ambiente
curl http://localhost:8001/api/health

# WebSocket testing (requiere cliente WebSocket)
# Abre la aplicación en http://localhost:8001 para probar WebSocket interactivamente
# El componente HomePage incluye controles para:
# - Envío de pings manuales
# - Tests de echo
# - Monitoreo de estado de conexión en tiempo real
# - Reconexión automática
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📝 Notas Adicionales

### Estructura del Proyecto Híbrido

```
ezekl-budget/
├── .github/workflows/
│   └── deploy.yml                    # CI/CD híbrido (Ionic + FastAPI)
├── ezekl-budget-ionic/               # 📱 Frontend Ionic Angular 8
│   ├── src/
│   │   ├── app/                      # Componentes Angular (Standalone)
│   │   ├── assets/                   # Recursos estáticos
│   │   └── environments/             # Configuraciones por entorno
│   ├── www/                          # 🏗️ Build compilado (servido por FastAPI)
│   ├── package.json                  # Dependencias Node.js
│   ├── angular.json                  # Configuración Angular
│   ├── ionic.config.json             # Configuración Ionic
│   └── capacitor.config.ts           # Configuración Capacitor
├── app/                              # ⚡ Backend FastAPI (Estructura Refactorizada)
│   ├── __init__.py                   # Módulo principal de la aplicación
│   ├── main.py                       # Servidor híbrido (API + static files)
│   ├── api/                          # 🌐 API modular con routers estándar FastAPI
│   │   ├── __init__.py               # Routers con prefijos: /api y /ws
│   │   ├── routes/                   # �️ REST API endpoints
│   │   │   ├── __init__.py           # Router base (health, credentials)
│   │   │   └── email.py              # Endpoints de procesamiento de emails
│   │   └── websockets/               # 📡 WebSockets en tiempo real
│   │       └── __init__.py           # Router base (sin prefijo)
│   ├── core/                         # �🔧 Configuración central
│   │   ├── __init__.py               # Módulo core
│   │   ├── config.py                 # Configuración con pydantic-settings
│   │   └── http_request.py           # Cliente HTTP asíncrono con aiohttp
│   ├── database/                     # 💾 Capa de acceso a datos
│   │   ├── __init__.py               # Módulo database
│   │   └── connection.py             # Conexiones asíncronas a SQL Server
│   ├── models/                       # 📝 Modelos Pydantic
│   │   ├── __init__.py               # Módulo models
│   │   ├── requests.py               # Modelos de entrada con validación (NUEVO)
│   │   └── responses.py              # Modelos de respuesta de la API
│   └── services/                     # 🔧 Lógica de negocio (NUEVO)
│       ├── __init__.py               # Módulo services
│       └── email_service.py          # Servicio centralizado para emails
├── .env                              # Variables de entorno (no commitear)
├── .env.example                      # Template de variables de entorno
├── .dockerignore                     # Archivos excluidos del build Docker
├── docker-compose.yml                # Configuración Docker Compose
├── Dockerfile                        # Multi-stage build (Ionic + FastAPI)
├── README.md                         # Este archivo
└── requirements.txt                  # Dependencias Python
```

### Arquitectura de la Aplicación

```
┌─────────────────────────────────────────┐
│             Nginx (SSL)                 │
│         budget.ezekl.com                │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           FastAPI (Puerto 8001)         │
├─────────────────┬───────────────────────┤
│ GET /           │ Sirve Frontend Ionic  │
│ GET /api/*      │ Endpoints de la API   │
│ GET /docs       │ Documentación API     │
│ GET /static/*   │ Archivos estáticos    │
└─────────────────┼───────────────────────┘
                  │
        ┌─────────▼──────────┐
        │   Frontend Build   │
        │ (ezekl-budget-ionic│
        │      /www/)        │
        └────────────────────┘
```

### Contacto y Soporte

- **Desarrollador**: Ezequiel Baltodano
- **Email**: ezekiell1988@gmail.com
- **GitHub**: [@ezekiell1988](https://github.com/ezekiell1988)

## 📋 Estado Actual del Proyecto

### ✅ Configuración Completada

- **Frontend**: Ionic Angular 8 + Standalone Components ✅
- **Backend**: FastAPI con servidor híbrido y estructura refactorizada ✅
- **Base de Datos**: SQL Server 2022 con conexiones asíncronas ✅
- **Código**: Estructura organizada por módulos y responsabilidades ✅
- **Usuario BD**: `budgetuser` con permisos limitados ✅
- **Detección de Ambiente**: Automática (localhost/IP externa) ✅
- **Autenticación**: Microsoft Azure AD (en implementación) 🔄
- **Dominio**: budget.ezekl.com ✅
- **SSL**: Let's Encrypt válido hasta 2026-01-02 ✅
- **CI/CD**: GitHub Actions híbrido (Ionic + FastAPI) ✅
- **Docker**: Multi-stage build optimizado ✅
- **Servidor**: Azure Ubuntu 22.04 ✅

### 🚀 URLs Funcionales

- **Frontend (Ionic)**: https://budget.ezekl.com/
- **API**: https://budget.ezekl.com/api/*
- **API Docs**: https://budget.ezekl.com/docs
- **API Health**: https://budget.ezekl.com/api/health

### 🔄 Workflow de Desarrollo

```bash
# Desarrollo normal
git add .
git commit -m "descripción"
git push origin main  # ← Deployment automático

# Ver el deployment en GitHub Actions:
# https://github.com/ezekiell1988/ezekl-budget/actions
```

## 🧑‍💻 Scripts de Desarrollo

### Frontend (Ionic)
```bash
cd ezekl-budget-ionic

# Desarrollo con hot-reload
ionic serve

# Build para producción
ionic build --prod

# Ejecutar tests
npm test

# Linting
npm run lint
```

### Backend (FastAPI)
```bash
# Activar entorno virtual
source .venv/bin/activate

# Servidor de desarrollo
python -m app.main

# O con uvicorn y hot-reload
uvicorn app.main:app --reload --port 8001
```

### Docker
```bash
# Build y ejecutar localmente
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

---

⚡ **Proyecto híbrido configurado y listo para desarrollo y producción** ⚡

🔗 **Template perfecto para aplicaciones FastAPI + Ionic Angular con autenticación Microsoft** 🔗