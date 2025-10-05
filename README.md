# Ezekl Budget - Aplicación Híbrida FastAPI + Ionic Angular

Este es un proyecto híbrido que combina **FastAPI** (backend) con **Ionic Angular 8** (frontend) para gestión de presupuesto con autenticación Microsoft, integración de Azure OpenAI, y deployment automático.

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
- **Autenticación JWT** integrada con Microsoft
- **Azure OpenAI** integration
- **SQL Server** con conexiones asíncronas y stored procedures
- **Detección automática** de ambiente (localhost en producción, IP externa en desarrollo)

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

# Azure OpenAI Configuration (requerido)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# Microsoft Azure AD (para autenticación)
AZURE_CLIENT_ID=your-client-id-from-azure-ad
AZURE_TENANT_ID=your-tenant-id-from-azure-ad

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

#### Detección Automática de Ambiente
```python
# En desarrollo (tu Mac): DB_HOST=20.246.83.239 (IP externa)
# En producción (servidor): DB_HOST=localhost (automático)
```

La aplicación detecta automáticamente si está en producción y usa `localhost` para mejor rendimiento.

#### Base de Datos Configurada
- **Nombre**: `budgetdb`
- **Collation**: `SQL_Latin1_General_CP1_CI_AS` (soporte para español y emojis)
- **Usuario**: `budgetuser` (permisos limitados)
- **Puerto**: 1433 (estándar SQL Server)

### 4.5. WebSocket en Tiempo Real

La aplicación incluye **WebSocket** para comunicación en tiempo real entre cliente y servidor:

#### Características del WebSocket
- **Endpoint**: `/ws/` (prefijo consistente con estructura API)
- **Protocolo**: WS en desarrollo local, WSS en producción con SSL
- **Ping-Pong automático**: Cada 30 segundos para mantener conexión activa
- **Reconexión automática**: Hasta 5 intentos con backoff exponencial
- **Mensajes JSON**: Comunicación estructurada con tipos específicos

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
- **Desarrollo local**: `ws://localhost:8001/ws/`
- **Producción**: `wss://budget.ezekl.com/ws/`

#### Implementación del Cliente:
El componente `HomePage` incluye un cliente WebSocket completo con:
- ✅ Detección automática de URL (desarrollo/producción)
- ✅ Reconexión automática con backoff exponencial
- ✅ Ping-pong automático cada 30 segundos
- ✅ UI en tiempo real con estado de conexión
- ✅ Log de mensajes con timestamps
- ✅ Controles manuales para testing

### 5. Configurar GitHub Secrets

En tu repositorio de GitHub, ve a **Settings → Secrets and variables → Actions** y agrega:

```
SSH_PRIVATE_KEY=contenido_completo_de_tu_archivo_.pem
SSH_HOST=20.246.83.239
SSH_USER=azureuser
AZURE_OPENAI_ENDPOINT=tu_endpoint_de_azure
AZURE_OPENAI_API_KEY=tu_api_key_de_azure
AZURE_OPENAI_DEPLOYMENT_NAME=tu_deployment_name
DB_PASSWORD=tu_contraseña_de_base_de_datos
```

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

### Ejecutar con Docker (Local)

```bash
# Construir imagen
docker build -t ezekl-budget .

# Ejecutar contenedor
docker run -d --name ezekl-budget -p 8001:8001 --env-file .env ezekl-budget

# O usar docker-compose
docker-compose up -d
```

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

#### **Beneficios Obtenidos**
- ✅ **Código más fácil de encontrar** y mantener
- ✅ **Separación lógica** por responsabilidades (core, database, models, api)
- ✅ **API modular** con endpoints y WebSockets separados
- ✅ **Imports más claros** y organizados
- ✅ **Preparado para escalar** agregando nuevas funcionalidades
- ✅ **Zero downtime** - Funcionalidad idéntica después de refactorización
- ✅ **main.py limpio** - Solo configuración de app y frontend

#### **Cambios en Imports (Evolución)**
```python
# Versión 1: Estructura plana
from app.settings import settings
from app.database import test_db_connection

# Versión 2: Estructura organizada  
from app.core.config import settings
from app.database.connection import test_db_connection
from app.models.responses import CredentialsResponse

# Versión 3: API modular con routers estándar FastAPI (actual)
from app.api import api_router, websockets_router_with_prefix
# api_router: endpoints HTTP con prefijo /api
# websockets_router_with_prefix: WebSockets con prefijo /ws

# main.py usa include_router() estándar:
app.include_router(api_router)                    # /api/*
app.include_router(websockets_router_with_prefix)  # /ws/*
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

### Testing de Endpoints

```bash
# Health check (incluye estado de base de datos)
curl https://budget.ezekl.com/api/health

# Credenciales (sin mostrar API key)
curl https://budget.ezekl.com/api/credentials

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
│   ├── core/                         # 🔧 Configuración central
│   │   ├── __init__.py               # Módulo core
│   │   └── config.py                 # Configuración con pydantic-settings
│   ├── database/                     # 💾 Capa de acceso a datos
│   │   ├── __init__.py               # Módulo database
│   │   └── connection.py             # Conexiones asíncronas a SQL Server
│   └── models/                       # 📝 Modelos Pydantic
│       ├── __init__.py               # Módulo models
│       └── responses.py              # Modelos de respuesta de la API
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