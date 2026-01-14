#!/usr/bin/env python
"""
Script de inicio para el proyecto voice-bot.
Ejecuta el build del frontend y luego inicia el servidor backend.
"""
import subprocess
import sys
import os
import platform


def check_and_activate_venv():
    """Verifica si estamos en el entorno virtual y lo activa si es necesario."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(base_dir, ".venv")
    
    # Detectar sistema operativo
    is_windows = platform.system() == "Windows"
    venv_python = os.path.join(venv_dir, "Scripts" if is_windows else "bin", 
                                "python.exe" if is_windows else "python")
    
    # Verificar que existe el entorno virtual
    if not os.path.exists(venv_python):
        print("❌ Error: No se encontró el entorno virtual en .venv", file=sys.stderr)
        print(f"Por favor, crea el entorno virtual con: python -m venv .venv", file=sys.stderr)
        sys.exit(1)
    
    # Comparar rutas reales (funciona en Windows y Unix)
    current_python = os.path.realpath(sys.executable)
    venv_python_real = os.path.realpath(venv_python)
    
    if current_python != venv_python_real:
        print("🔄 Activando entorno virtual...")
        # Re-ejecutar este script usando el Python del entorno virtual
        result = subprocess.run([venv_python] + sys.argv, cwd=base_dir)
        sys.exit(result.returncode)
    
    # Si llegamos aquí, ya estamos en el venv
    print("✅ Entorno virtual activo")


def main():
    """Ejecuta el build del frontend y luego inicia el servidor backend."""
    
    # Importar dotenv aquí (ya dentro del venv)
    from dotenv import load_dotenv
    
    # Cargar variables de entorno desde .env
    load_dotenv()
    
    # Obtener el directorio base del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Obtener el directorio del frontend desde variables de entorno
    frontend_dir_name = os.getenv("FRONTEND_DIR", "ezekl-budget-ionic")
    
    # Rutas
    chat_bot_dir = os.path.join(base_dir, frontend_dir_name)
    venv_dir = os.path.join(base_dir, ".venv")
    
    # Detectar sistema operativo y usar la ruta correcta del ejecutable de Python
    is_windows = platform.system() == "Windows"
    if is_windows:
        python_executable = os.path.join(venv_dir, "Scripts", "python.exe")
        python_command = "python"  # En Windows se usa 'python'
    else:
        python_executable = os.path.join(venv_dir, "bin", "python")
        python_command = "python3"  # En Linux/Mac se usa 'python3'
    
    # Verificar que existe el entorno virtual
    if not os.path.exists(python_executable):
        print("❌ Error: No se encontró el entorno virtual en .venv", file=sys.stderr)
        print(f"Por favor, crea el entorno virtual con: {python_command} -m venv .venv", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 60)
    print("🚀 Iniciando Voice Bot")
    print("=" * 60)
    
    # Paso 1: Build del frontend
    print("\n📦 Construyendo el frontend (npm run build)...")
    print("-" * 60)
    
    try:
        # En Windows, necesitamos usar shell=True para encontrar npm
        if is_windows:
            result = subprocess.run(
                "npm run build",
                cwd=chat_bot_dir,
                shell=True,
                check=True
            )
        else:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=chat_bot_dir,
                check=True
            )
        print("✅ Build del frontend completado exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante el build del frontend: {e}", file=sys.stderr)
        print("⚠️  Continuando sin build del frontend...", file=sys.stderr)
    except FileNotFoundError:
        print("⚠️  npm no está instalado o no se encuentra en el PATH", file=sys.stderr)
        print("⚠️  Continuando sin build del frontend...", file=sys.stderr)
    
    # Paso 2: Iniciar el servidor backend
    print("\n🐍 Iniciando el servidor backend...")
    print("-" * 60)
    
    try:
        # Ejecutar el servidor Python
        subprocess.run(
            [python_executable, "-m", "app.main"],
            cwd=base_dir,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al iniciar el servidor backend: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Error: Python no se encuentra en {python_executable}", file=sys.stderr)
        print("Asegúrate de que el entorno virtual esté configurado correctamente.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Primero verificar y activar el entorno virtual
        check_and_activate_venv()
        # Luego ejecutar el main
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(0)
