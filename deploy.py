#!/usr/bin/env python3
"""
Script de deployment automático a Azure Container Apps
Ejecuta: python deploy.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# ============================
# CONFIGURACIÓN
# ============================

# Azure Container Registry
ACR_NAME = "demoecommerce"
ACR_LOGIN_SERVER = "demoecommerce.azurecr.io"

# Azure Container Apps
RESOURCE_GROUP = "rg-ezequiel"
CONTAINER_APP_NAME = "ezekl-budget-app"
CONTAINER_APP_ENV = "ezekl-budget-env"
LOCATION = "eastus"

# Imagen Docker
IMAGE_NAME = "ezekl-budget-app"
IMAGE_TAG = datetime.now().strftime("%Y%m%d-%H%M%S")

# Configuración de la app
TARGET_PORT = 8001
MIN_REPLICAS = 1
MAX_REPLICAS = 3
CPU = "0.5"
MEMORY = "1.0Gi"


# ============================
# FUNCIONES AUXILIARES
# ============================

def print_step(message):
    """Imprime un mensaje de paso con formato"""
    print(f"\n{'='*60}")
    print(f"🚀 {message}")
    print(f"{'='*60}\n")


def run_command(command, shell=True, check=True, cwd=None):
    """Ejecuta un comando y retorna el resultado"""
    print(f"💻 Ejecutando: {command}\n")
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=cwd
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr and not check:
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando comando: {e}")
        print(f"Salida: {e.stdout}")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def check_prerequisites():
    """Verifica que estén instaladas las herramientas necesarias"""
    print_step("Verificando prerequisitos")
    
    # Verificar Azure CLI
    try:
        result = run_command("az --version", check=False)
        if result.returncode != 0:
            print("❌ Azure CLI no está instalado")
            print("Instalar desde: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
            sys.exit(1)
        print("✅ Azure CLI instalado")
    except:
        print("❌ Azure CLI no está instalado")
        sys.exit(1)
    
    # Verificar Docker
    try:
        result = run_command("docker --version", check=False)
        if result.returncode != 0:
            print("❌ Docker no está instalado")
            print("Instalar desde: https://www.docker.com/get-started")
            sys.exit(1)
        print("✅ Docker instalado")
    except:
        print("❌ Docker no está instalado")
        sys.exit(1)
    
    # Verificar Node.js
    try:
        result = run_command("node --version", check=False)
        if result.returncode != 0:
            print("❌ Node.js no está instalado")
            sys.exit(1)
        print("✅ Node.js instalado")
    except:
        print("❌ Node.js no está instalado")
        sys.exit(1)
    
    # Verificar Ionic CLI
    try:
        result = run_command("ionic --version", check=False)
        if result.returncode != 0:
            print("⚠️  Ionic CLI no está instalado. Instalando...")
            run_command("npm install -g @ionic/cli")
        print("✅ Ionic CLI instalado")
    except:
        print("⚠️  Ionic CLI no está instalado. Instalando...")
        run_command("npm install -g @ionic/cli")


def login_azure():
    """Login a Azure y verifica la sesión"""
    print_step("Verificando sesión de Azure")
    
    # Verificar si ya está logueado
    result = run_command("az account show", check=False)
    
    if result.returncode != 0:
        print("No hay sesión activa de Azure. Iniciando login...")
        run_command("az login")
    else:
        print("✅ Sesión de Azure activa")
        account_info = json.loads(result.stdout)
        print(f"Suscripción: {account_info['name']}")
        print(f"ID: {account_info['id']}")


def login_acr():
    """Login a Azure Container Registry"""
    print_step(f"Login a Azure Container Registry: {ACR_NAME}")
    run_command(f"az acr login --name {ACR_NAME}")
    print("✅ Login exitoso a ACR")


def build_frontend():
    """Construye el frontend de Ionic"""
    print_step("Construyendo frontend Ionic")
    
    frontend_path = Path("ezekl-budget-ionic")
    
    if not frontend_path.exists():
        print(f"❌ Directorio {frontend_path} no encontrado")
        sys.exit(1)
    
    # Limpiar build anterior
    www_path = frontend_path / "www"
    node_modules_path = frontend_path / "node_modules"
    
    if www_path.exists():
        print("🧹 Limpiando build anterior...")
        if os.name == 'nt':  # Windows
            run_command(f"rmdir /s /q {www_path}", check=False)
        else:  # Linux/Mac
            run_command(f"rm -rf {www_path}", check=False)
    
    # Limpiar node_modules si existe para evitar conflictos de bloqueo
    if node_modules_path.exists():
        print("🧹 Limpiando node_modules...")
        if os.name == 'nt':  # Windows
            run_command(f"rmdir /s /q {node_modules_path}", check=False)
        else:  # Linux/Mac
            run_command(f"rm -rf {node_modules_path}", check=False)
        
        # Esperar un momento para que el sistema libere los archivos
        import time
        time.sleep(2)
    
    # Instalar dependencias
    print("📦 Instalando dependencias de npm...")
    
    # Intentar primero con npm ci
    result = run_command("npm ci --loglevel error", cwd=str(frontend_path), check=False)
    
    if result.returncode != 0:
        print("⚠️  npm ci falló, intentando con npm install...")
        run_command("npm install --loglevel error", cwd=str(frontend_path))
    
    # Build de producción
    print("🏗️  Ejecutando build de producción...")
    run_command("ionic build --prod", cwd=str(frontend_path))
    
    # Verificar que el build fue exitoso
    if not (www_path / "index.html").exists():
        print("❌ Error: El build del frontend falló")
        sys.exit(1)
    
    print("✅ Frontend construido exitosamente")


def build_docker_image():
    """Construye la imagen Docker"""
    print_step("Construyendo imagen Docker")
    
    image_full_name = f"{ACR_LOGIN_SERVER}/{IMAGE_NAME}:{IMAGE_TAG}"
    image_latest = f"{ACR_LOGIN_SERVER}/{IMAGE_NAME}:latest"
    
    print(f"Imagen: {image_full_name}")
    print(f"Latest: {image_latest}")
    
    # Construir para la plataforma Linux AMD64 (necesaria para Azure Container Apps)
    run_command(
        f"docker buildx build --platform linux/amd64 "
        f"--load -t {image_full_name} -t {image_latest} ."
    )
    
    print("✅ Imagen Docker construida exitosamente")
    return image_full_name, image_latest


def push_docker_image(image_full_name, image_latest):
    """Sube la imagen a Azure Container Registry"""
    print_step("Subiendo imagen a Azure Container Registry")
    
    print(f"📤 Pushing {image_full_name}...")
    run_command(f"docker push {image_full_name}")
    
    print(f"📤 Pushing {image_latest}...")
    run_command(f"docker push {image_latest}")
    
    print("✅ Imágenes subidas exitosamente")


def ensure_container_app_env():
    """Verifica que exista el Container App Environment, si no lo crea"""
    print_step("Verificando Container App Environment")
    
    result = run_command(
        f"az containerapp env show --name {CONTAINER_APP_ENV} --resource-group {RESOURCE_GROUP}",
        check=False
    )
    
    if result.returncode != 0:
        print(f"📦 Creando Container App Environment: {CONTAINER_APP_ENV}...")
        run_command(
            f"az containerapp env create "
            f"--name {CONTAINER_APP_ENV} "
            f"--resource-group {RESOURCE_GROUP} "
            f"--location {LOCATION}"
        )
        print("✅ Environment creado")
    else:
        print("✅ Environment ya existe")


def load_env_file():
    """Carga las variables de entorno desde .env"""
    env_vars = {}
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  Archivo .env no encontrado. Usando valores por defecto.")
        return env_vars
    
    print("📝 Cargando variables de entorno desde .env...")
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Remover comillas si existen
                value = value.strip('"').strip("'")
                env_vars[key.strip()] = value
    
    print(f"✅ Cargadas {len(env_vars)} variables de entorno")
    return env_vars


def build_env_vars_string(env_vars):
    """Construye el string de variables de entorno para az containerapp"""
    # Variables de entorno básicas
    env_list = [
        f"PORT={TARGET_PORT}",
    ]
    
    # Variables sensibles que van como secretos
    secret_keys = [
        'AZURE_OPENAI_API_KEY',
        'SMTP_PASSWORD',
        'AZURE_CLIENT_SECRET',
        'DB_PASSWORD',
        'CRM_CLIENT_SECRET',
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_VERIFY_TOKEN',
        'COPILOT_CLIENT_SECRET'
    ]
    
    # Agregar variables del .env (excepto las sensibles)
    for key, value in env_vars.items():
        if key not in secret_keys and key not in ['PORT', 'ENVIRONMENT']:
            # Escapar comillas y espacios
            value_escaped = value.replace('"', '\\"')
            env_list.append(f"{key}={value_escaped}")
    
    # Agregar ENVIRONMENT al final para evitar duplicados
    env_list.append("ENVIRONMENT=production")
    
    # Agregar referencias a secretos
    for secret_key in secret_keys:
        if secret_key in env_vars:
            secret_name = secret_key.lower().replace('_', '-')
            env_list.append(f"{secret_key}=secretref:{secret_name}")
    
    return " ".join([f'"{var}"' for var in env_list])


def build_secrets_string(env_vars):
    """Construye el string de secretos para az containerapp"""
    secret_keys = [
        'AZURE_OPENAI_API_KEY',
        'SMTP_PASSWORD',
        'AZURE_CLIENT_SECRET',
        'DB_PASSWORD',
        'CRM_CLIENT_SECRET',
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_VERIFY_TOKEN',
        'COPILOT_CLIENT_SECRET'
    ]
    
    secrets = []
    for key in secret_keys:
        if key in env_vars:
            secret_name = key.lower().replace('_', '-')
            value_escaped = env_vars[key].replace('"', '\\"')
            secrets.append(f"{secret_name}={value_escaped}")
    
    return " ".join([f'"{secret}"' for secret in secrets])


def deploy_container_app(image_full_name):
    """Despliega o actualiza la Container App"""
    print_step("Desplegando a Azure Container Apps")
    
    # Verificar si la app ya existe
    result = run_command(
        f"az containerapp show --name {CONTAINER_APP_NAME} --resource-group {RESOURCE_GROUP}",
        check=False
    )
    
    # Cargar variables de entorno
    env_vars = load_env_file()
    
    if result.returncode == 0:
        # App existe, hacer update
        print(f"🔄 Actualizando Container App: {CONTAINER_APP_NAME}...")
        
        # Construir strings de variables y secretos
        env_vars_str = build_env_vars_string(env_vars)
        secrets_str = build_secrets_string(env_vars)
        
        # Primero actualizar los secretos si existen
        if secrets_str:
            print("🔐 Actualizando secretos...")
            run_command(
                f"az containerapp secret set "
                f"--name {CONTAINER_APP_NAME} "
                f"--resource-group {RESOURCE_GROUP} "
                f"--secrets {secrets_str}",
                check=False  # No fallar si algún secreto ya existe
            )
        
        # Luego actualizar la imagen y variables de entorno
        run_command(
            f"az containerapp update "
            f"--name {CONTAINER_APP_NAME} "
            f"--resource-group {RESOURCE_GROUP} "
            f"--image {image_full_name} "
            f"--set-env-vars {env_vars_str}"
        )
        
        print("✅ Container App actualizada")
    else:
        # App no existe, crearla
        print(f"🆕 Creando Container App: {CONTAINER_APP_NAME}...")
        
        # Construir strings de variables y secretos
        env_vars_str = build_env_vars_string(env_vars)
        secrets_str = build_secrets_string(env_vars)
        
        cmd = (
            f"az containerapp create "
            f"--name {CONTAINER_APP_NAME} "
            f"--resource-group {RESOURCE_GROUP} "
            f"--environment {CONTAINER_APP_ENV} "
            f"--image {image_full_name} "
            f"--target-port {TARGET_PORT} "
            f"--ingress external "
            f"--min-replicas {MIN_REPLICAS} "
            f"--max-replicas {MAX_REPLICAS} "
            f"--cpu {CPU} "
            f"--memory {MEMORY} "
            f"--registry-server {ACR_LOGIN_SERVER} "
        )
        
        if secrets_str:
            cmd += f"--secrets {secrets_str} "
        
        if env_vars_str:
            cmd += f"--env-vars {env_vars_str}"
        
        run_command(cmd)
        
        print("✅ Container App creada")


def get_app_url(image_full_name):
    """Obtiene la URL de la aplicación desplegada"""
    print_step("Obteniendo URL de la aplicación")
    
    result = run_command(
        f"az containerapp show "
        f"--name {CONTAINER_APP_NAME} "
        f"--resource-group {RESOURCE_GROUP} "
        f"--query properties.configuration.ingress.fqdn "
        f"--output tsv"
    )
    
    fqdn = result.stdout.strip()
    
    if fqdn:
        app_url = f"https://{fqdn}"
        health_url = f"{app_url}/api/health"
        
        print(f"\n{'='*60}")
        print("✅ DEPLOYMENT EXITOSO!")
        print(f"{'='*60}\n")
        print(f"🌐 URL de la aplicación: {app_url}")
        print(f"📊 Health check: {health_url}")
        print(f"📝 Imagen desplegada: {image_full_name}")
        print(f"🏷️  Tag: {IMAGE_TAG}")
        print(f"\n{'='*60}\n")
    else:
        print("⚠️  No se pudo obtener la URL de la aplicación")


# ============================
# FUNCIÓN PRINCIPAL
# ============================

def main():
    """Función principal del script de deployment"""
    print("\n" + "="*60)
    print("🚀 DEPLOY A AZURE CONTAINER APPS")
    print("="*60)
    
    try:
        # 1. Verificar prerequisitos
        check_prerequisites()
        
        # 2. Login a Azure
        login_azure()
        
        # 3. Login a ACR
        login_acr()
        
        # 4. Build del frontend
        build_frontend()
        
        # 5. Build de la imagen Docker
        image_full_name, image_latest = build_docker_image()
        
        # 6. Push a ACR
        push_docker_image(image_full_name, image_latest)
        
        # 7. Verificar/crear environment
        ensure_container_app_env()
        
        # 8. Deploy/update container app
        deploy_container_app(image_full_name)
        
        # 9. Obtener URL
        get_app_url(image_full_name)
        
        print("\n✅ Deployment completado exitosamente!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error durante el deployment: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
