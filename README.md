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
- **Autenticación JWT** integrada con Microsoft
- **Azure OpenAI** integration

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

## 📋 Requisitos

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
```

### 4. Configurar GitHub Secrets

En tu repositorio de GitHub, ve a **Settings → Secrets and variables → Actions** y agrega:

```
SSH_PRIVATE_KEY=contenido_completo_de_tu_archivo_.pem
SSH_HOST=20.246.83.239
SSH_USER=azureuser
AZURE_OPENAI_ENDPOINT=tu_endpoint_de_azure
AZURE_OPENAI_API_KEY=tu_api_key_de_azure
AZURE_OPENAI_DEPLOYMENT_NAME=tu_deployment_name
```

## 🖥️ Desarrollo Local

### Opción 1: Desarrollo Completo (Frontend + Backend)

```bash
# Terminal 1: Frontend Ionic (desarrollo con hot-reload)
cd ezekl-budget-ionic
ionic serve  # http://localhost:8100

# Terminal 2: Backend FastAPI
source .venv/bin/activate
python -m app.main  # http://localhost:8001/api
```

### Opción 2: Servidor Híbrido (Producción Local)

```bash
# 1. Compilar frontend
cd ezekl-budget-ionic
ionic build --prod
cd ..

# 2. Ejecutar servidor híbrido
source .venv/bin/activate
python -m app.main
```

### URLs de Desarrollo:
- **Frontend (dev)**: http://localhost:8100 ← Hot reload
- **Frontend (híbrido)**: http://localhost:8001/ ← Como producción
- **API**: http://localhost:8001/api/*
- **API Docs**: http://localhost:8001/docs

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
6. 🐳 Construye imagen Docker con FastAPI + frontend compilado
7. 🛑 Detiene contenedor anterior
8. ▶️ Ejecuta nuevo contenedor en puerto 8001
9. ✅ Verifica que esté funcionando

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

# Reconstruir y ejecutar
docker stop ezekl-budget || true
docker rm ezekl-budget || true
docker build -t ezekl-budget .
docker run -d --name ezekl-budget --restart unless-stopped -p 8001:8001 --env-file .env ezekl-budget

# Verificar
docker ps | grep ezekl-budget
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

## � Troubleshooting

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
- `GET /health` → Health check del servicio

### Específicos del Proyecto

- `GET /credentials` → Obtiene credenciales de Azure OpenAI (sin API key)

### Testing de Endpoints

```bash
# Health check
curl https://budget.ezekl.com/health

# Credenciales (sin mostrar API key)
curl https://budget.ezekl.com/credentials

# Documentación interactiva
open https://budget.ezekl.com/docs
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
├── app/                              # ⚡ Backend FastAPI
│   ├── main.py                       # Servidor híbrido (API + static files)
│   └── settings.py                   # Configuración con pydantic-settings
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
- **Backend**: FastAPI con servidor híbrido ✅
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