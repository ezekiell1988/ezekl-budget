#!/usr/bin/env python3
"""
Script de inicio que ejecuta limpieza y construcción del proyecto.

Este script realiza las siguientes tareas en orden:
1. Activa el entorno virtual (si es necesario)
2. Limpia logs usando cleanup_logs.py
3. Limpia imports usando cleanup_imports.py
4. Construye la aplicación Ionic
5. Inicia la aplicación FastAPI

Uso: python ./utils/start.py
"""

import subprocess
import sys
import os
from pathlib import Path


def is_venv_active() -> bool:
    """Verifica si el entorno virtual está activo."""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )


def activate_venv_and_restart(venv_python: Path, script_path: Path):
    """
    Reinicia el script usando el intérprete del entorno virtual.
    
    Args:
        venv_python: Ruta al intérprete Python del entorno virtual
        script_path: Ruta al script actual
    """
    print(f"\n{'='*60}")
    print(f"🔄 Activando entorno virtual...")
    print(f"{'='*60}")
    print(f"📍 Python del venv: {venv_python}")
    
    # Re-ejecutar el script con el Python del entorno virtual
    os.execv(str(venv_python), [str(venv_python), str(script_path)] + sys.argv[1:])


def run_command(command: list[str], description: str, cwd: str = None) -> bool:
    """
    Ejecuta un comando y maneja errores.
    
    Args:
        command: Lista con el comando y sus argumentos
        description: Descripción de la tarea
        cwd: Directorio de trabajo (opcional)
    
    Returns:
        True si el comando fue exitoso, False en caso contrario
    """
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=False
        )
        print(f"✅ {description} - Completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en: {description}")
        print(f"Código de salida: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado en: {description}")
        print(f"Error: {str(e)}")
        return False


def main():
    """Función principal que ejecuta todas las tareas."""
    # Obtener el directorio raíz del proyecto
    script_dir = Path(__file__).parent
    script_path = Path(__file__).resolve()
    project_root = script_dir.parent
    app_dir = project_root / "app"
    ionic_dir = project_root / "ezekl-budget-ionic"
    venv_python = project_root / ".venv" / "bin" / "python"
    
    # Verificar que exista el entorno virtual
    if not venv_python.exists():
        print(f"❌ Error: No se encontró el entorno virtual Python en {venv_python}")
        print(f"Por favor, crea el entorno virtual primero con: python -m venv .venv")
        sys.exit(1)
    
    # Si no estamos en el entorno virtual, reiniciar con el Python del venv
    if not is_venv_active():
        activate_venv_and_restart(venv_python, script_path)
        return  # Esta línea nunca se ejecutará debido a execv
    
    print(f"\n{'='*60}")
    print(f"🎯 INICIANDO PROCESO DE BUILD Y START")
    print(f"{'='*60}")
    print(f"📁 Directorio del proyecto: {project_root}")
    print(f"🐍 Python activo: {sys.executable}")
    print(f"✅ Entorno virtual: Activo")
    
    # Verificar que existan los directorios necesarios
    if not app_dir.exists():
        print(f"❌ Error: No se encontró el directorio app en {app_dir}")
        sys.exit(1)
    
    if not ionic_dir.exists():
        print(f"❌ Error: No se encontró el directorio ionic en {ionic_dir}")
        sys.exit(1)
    
    # 1. Ejecutar cleanup_logs.py
    cleanup_logs_cmd = [str(venv_python), "utils/cleanup_logs.py", "app/"]
    if not run_command(
        cleanup_logs_cmd,
        "Limpiando logs",
        cwd=str(project_root)
    ):
        print("\n⚠️  Advertencia: Falló la limpieza de logs, continuando...")
    
    # 2. Ejecutar cleanup_imports.py
    cleanup_imports_cmd = [str(venv_python), "utils/cleanup_imports.py", "app/"]
    if not run_command(
        cleanup_imports_cmd,
        "Limpiando imports",
        cwd=str(project_root)
    ):
        print("\n⚠️  Advertencia: Falló la limpieza de imports, continuando...")
    
    # 3. Construir aplicación Ionic
    npm_build_cmd = ["npm", "run", "build", "--prefix", "./ezekl-budget-ionic"]
    if not run_command(
        npm_build_cmd,
        "Construyendo aplicación Ionic",
        cwd=str(project_root)
    ):
        print("\n❌ Error crítico: Falló la construcción de Ionic")
        sys.exit(1)
    
    # 4. Iniciar aplicación FastAPI
    print(f"\n{'='*60}")
    print(f"🚀 Iniciando servidor FastAPI")
    print(f"{'='*60}")
    print("Presiona Ctrl+C para detener el servidor\n")
    
    fastapi_cmd = [str(venv_python), "-m", "app.main"]
    try:
        subprocess.run(
            fastapi_cmd,
            cwd=str(project_root),
            check=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al iniciar el servidor FastAPI")
        print(f"Código de salida: {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
