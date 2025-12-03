#!/usr/bin/env python
"""
Script de inicio para el proyecto voice-bot.
Ejecuta el build del frontend y luego inicia el servidor backend.
"""
import subprocess
import sys
import os


def main():
    """Ejecuta el build del frontend y luego inicia el servidor backend."""
    
    # Obtener el directorio base del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Rutas
    chat_bot_dir = os.path.join(base_dir, "ezekl-budget-ionic")
    venv_dir = os.path.join(base_dir, ".venv")
    python_executable = os.path.join(venv_dir, "bin", "python")
    
    # Verificar que existe el entorno virtual
    if not os.path.exists(python_executable):
        print("❌ Error: No se encontró el entorno virtual en .venv", file=sys.stderr)
        print("Por favor, crea el entorno virtual con: python3 -m venv .venv", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 60)
    print("🚀 Iniciando Voice Bot")
    print("=" * 60)
    
    # Paso 1: Build del frontend
    print("\n📦 Construyendo el frontend (npm run build)...")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            ["npm", "run", "build", "--prefix", "./ezekl-budget-ionic"],
            cwd=base_dir,
            check=True
        )
        print("✅ Build del frontend completado exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante el build del frontend: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: npm no está instalado o no se encuentra en el PATH", file=sys.stderr)
        sys.exit(1)
    
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
