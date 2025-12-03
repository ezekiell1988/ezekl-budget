#!/usr/bin/env python
"""
Script de inicio para el proyecto voice-bot.
Ejecuta el build del frontend y luego inicia el servidor backend.
"""
import subprocess
import sys
import os
import platform


def main():
    """Ejecuta el build del frontend y luego inicia el servidor backend."""
    
    # Obtener el directorio base del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Rutas
    chat_bot_dir = os.path.join(base_dir, "ezekl-budget-ionic")
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
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(0)
