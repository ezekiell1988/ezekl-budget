# Ezekl Budget - FastAPI Project

Este es un proyecto FastAPI para gestión de presupuesto con integración de Azure OpenAI, configurado con Docker, CI/CD automático y SSL.

## 🚀 Características

- **FastAPI** con documentación automática
- **Docker** y Docker Compose para deployment
- **CI/CD automático** con GitHub Actions
- **SSL/HTTPS** con certificados Let's Encrypt
- **Reverse proxy** con Nginx
- **WebSocket support** para aplicaciones en tiempo real
- **Configuración flexible** para múltiples proyectos

## 🌐 URLs del Proyecto

- **Producción**: https://budget.ezekl.com
- **API Docs**: https://budget.ezekl.com/docs
- **Health Check**: https://budget.ezekl.com/health

## 📋 Requisitos

### Local
- Python 3.13+
- Git
- Acceso a las claves SSH del servidor

### Servidor (Azure)
- Ubuntu 22.04+
- Docker y Docker Compose
- Nginx
- Certbot (Let's Encrypt)

## 🛠️ Configuración Inicial

### 1. Clonar el Proyecto

```bash
git clone https://github.com/ezekiell1988/ezekl-budget.git
cd ezekl-budget
```

### 2. Configurar Entorno Virtual Local

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate  # Linux/macOS
# o
.venv\\Scripts\\activate     # Windows

# Instalar dependencias
pip install fastapi "uvicorn[standard]" pydantic-settings python-dotenv

# Generar requirements.txt
pip freeze > requirements.txt
```

### 3. Configurar Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

# Server Configuration - ezekl-budget
PORT=8001

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

### Ejecutar la Aplicación

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar servidor de desarrollo
python -m app.main

# O usar uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

La aplicación estará disponible en:
- **API**: http://localhost:8001
- **Docs**: http://localhost:8001/docs
- **Health**: http://localhost:8001/health

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

```bash
# Configurar sitio en Nginx (ya configurado para budget.ezekl.com)
sudo nano /etc/nginx/sites-available/budget.ezekl.com

# Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/budget.ezekl.com /etc/nginx/sites-enabled/

# Generar certificado SSL
sudo certbot certonly --webroot -w /var/www/budget.ezekl.com -d budget.ezekl.com --email tu@email.com

# Recargar Nginx
sudo nginx -t && sudo systemctl reload nginx
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

1. **Clonar este template**
2. **Cambiar puerto** en `.env` y workflow
3. **Configurar dominio** en Cloudflare (DNS only)
4. **Crear configuración Nginx**:

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

## 🔒 Seguridad

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

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📝 Notas Adicionales

### Estructura del Proyecto

```
ezekl-budget/
├── .github/workflows/
│   └── deploy.yml              # CI/CD workflow
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app principal
│   └── settings.py             # Configuración con pydantic-settings
├── .env                        # Variables de entorno (no commitear)
├── .env.example                # Template de variables de entorno
├── .gitignore                  # Archivos ignorados por git
├── docker-compose.yml          # Configuración Docker Compose
├── Dockerfile                  # Imagen Docker
├── README.md                   # Este archivo
└── requirements.txt            # Dependencias Python
```

### Contacto y Soporte

- **Desarrollador**: Ezequiel Baltodano
- **Email**: ezekiell1988@gmail.com
- **GitHub**: [@ezekiell1988](https://github.com/ezekiell1988)

---

⚡ **Proyecto configurado y listo para desarrollo y producción** ⚡