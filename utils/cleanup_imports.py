#!/usr/bin/env python3
"""
Script para eliminar imports no utilizados de archivos Python.
Valida el archivo después de los cambios y revierte si hay errores.

Uso:
    # Archivo individual
    python cleanup_imports.py <archivo.py> [--dry-run]
    
    # Carpeta (recursivo por defecto)
    python cleanup_imports.py <carpeta> [--dry-run]
    
    # Carpeta solo nivel actual (sin subcarpetas)
    python cleanup_imports.py <carpeta> --no-recursive [--dry-run]
    
    # Todos los archivos en app/
    python cleanup_imports.py --all [--dry-run]

Ejemplos:
    python cleanup_imports.py app/core/config.py --dry-run
    python cleanup_imports.py app/services/ --recursive
    python cleanup_imports.py app/api/ --no-recursive
    python cleanup_imports.py --all

Opciones:
    --dry-run: Muestra los cambios sin aplicarlos
    --all: Procesa todos los archivos Python en app/
    --recursive, -r: Procesa subcarpetas recursivamente (default para carpetas)
    --no-recursive: Solo procesa archivos en el nivel actual de la carpeta
    --stop-on-error: Detiene todo el procesamiento al primer error
"""

import ast
import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import Set, List, Tuple, Optional


class ImportCleaner:
    """Limpia imports no utilizados de archivos Python."""
    
    def __init__(self, file_path: str, dry_run: bool = False):
        self.file_path = Path(file_path)
        self.backup_path = self.file_path.with_suffix('.py.backup')
        self.original_content = ""
        self.modified_content = ""
        self.dry_run = dry_run
        
    def read_file(self) -> str:
        """Lee el contenido del archivo."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def create_backup(self):
        """Crea una copia de respaldo del archivo."""
        self.original_content = self.read_file()
        shutil.copy2(self.file_path, self.backup_path)
        print(f"✓ Backup creado: {self.backup_path}")
    
    def restore_backup(self):
        """Restaura el archivo desde el backup."""
        if self.backup_path.exists():
            shutil.copy2(self.backup_path, self.file_path)
            print(f"✓ Archivo restaurado desde backup")
            return True
        return False
    
    def remove_backup(self):
        """Elimina el archivo de backup."""
        if self.backup_path.exists():
            self.backup_path.unlink()
            print(f"✓ Backup eliminado")
    
    def get_imported_names(self, content: str) -> Set[str]:
        """Extrae todos los nombres importados del archivo."""
        imported = set()
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name
                        imported.add(name)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name
                        imported.add(name)
        except SyntaxError as e:
            print(f"⚠ Error de sintaxis al parsear: {e}")
        return imported
    
    def get_used_names(self, content: str) -> Set[str]:
        """Extrae todos los nombres usados en el código (excluyendo imports)."""
        used = set()
        try:
            tree = ast.parse(content)
            
            # Primera pasada: recolectar imports para excluirlos
            import_nodes = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_nodes.add(id(node))
            
            # Segunda pasada: recolectar nombres usados
            for node in ast.walk(tree):
                # Saltar nodos de import
                if id(node) in import_nodes or any(
                    id(parent) in import_nodes 
                    for parent in ast.walk(node) 
                    if parent != node
                ):
                    continue
                
                if isinstance(node, ast.Name):
                    used.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # Para casos como 'module.function', capturar 'module'
                    if isinstance(node.value, ast.Name):
                        used.add(node.value.id)
        except SyntaxError as e:
            print(f"⚠ Error de sintaxis al analizar uso: {e}")
        return used
    
    def find_unused_imports(self, content: str) -> Set[str]:
        """Encuentra imports que no se utilizan en el código."""
        imported = self.get_imported_names(content)
        used = self.get_used_names(content)
        unused = imported - used
        return unused
    
    def remove_unused_imports(self, content: str, unused: Set[str]) -> str:
        """Elimina las líneas de imports no utilizados."""
        if not unused:
            return content
        
        lines = content.split('\n')
        new_lines = []
        skip_line = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Manejar imports multilínea con paréntesis
            if '(' in stripped and 'import' in stripped and not ')' in stripped:
                skip_line = True
                temp_import = stripped
                j = i + 1
                while j < len(lines) and ')' not in lines[j]:
                    temp_import += ' ' + lines[j].strip()
                    j += 1
                if j < len(lines):
                    temp_import += ' ' + lines[j].strip()
                
                # Verificar si algún import en el bloque está en unused
                should_skip = any(name in temp_import for name in unused)
                if not should_skip:
                    new_lines.append(line)
                continue
            
            if skip_line and ')' in stripped:
                skip_line = False
                continue
            
            if skip_line:
                continue
            
            # Verificar imports simples
            if stripped.startswith(('import ', 'from ')):
                should_remove = any(name in unused for name in unused if name in stripped)
                
                # Verificar específicamente si es un import no usado
                try:
                    tree = ast.parse(stripped)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                name = alias.asname if alias.asname else alias.name
                                if name in unused:
                                    should_remove = True
                                    break
                        elif isinstance(node, ast.ImportFrom):
                            for alias in node.names:
                                name = alias.asname if alias.asname else alias.name
                                if name in unused:
                                    should_remove = True
                                    break
                except:
                    pass
                
                if should_remove:
                    print(f"  Eliminando: {stripped}")
                    continue
            
            new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def validate_syntax(self, content: str) -> Tuple[bool, Optional[str]]:
        """Valida que el código tenga sintaxis correcta."""
        try:
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            return False, f"Error de sintaxis en línea {e.lineno}: {e.msg}"
    
    def run_basic_checks(self) -> Tuple[bool, Optional[str]]:
        """Ejecuta verificaciones básicas en el archivo modificado."""
        # Verificar sintaxis
        content = self.read_file()
        is_valid, error = self.validate_syntax(content)
        
        if not is_valid:
            return False, error
        
        # Intentar importar el módulo si es posible (opcional)
        # Esto puede ayudar a detectar errores de import
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(self.file_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return False, f"Error de compilación: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Timeout al compilar el archivo"
        except Exception as e:
            # No fallar si py_compile no está disponible
            print(f"⚠ No se pudo ejecutar py_compile: {e}")
        
        return True, None
    
    def clean(self) -> bool:
        """Proceso principal de limpieza."""
        print(f"\n{'='*60}")
        print(f"🧹 Procesando: {self.file_path}")
        print(f"{'='*60}")
        
        # Leer contenido original
        self.original_content = self.read_file()
        content = self.original_content
        
        # Validar sintaxis original
        is_valid, error = self.validate_syntax(content)
        if not is_valid:
            print(f"✗ El archivo original tiene errores de sintaxis: {error}")
            return False
        
        # Encontrar imports no utilizados
        print("\nAnalizando imports...")
        unused = self.find_unused_imports(content)
        
        if not unused:
            print("✓ No se encontraron imports sin usar")
            return True
        
        print(f"\n✓ Imports no utilizados encontrados: {len(unused)}")
        for name in sorted(unused):
            print(f"  - {name}")
        
        # Eliminar imports no utilizados
        print("\nEliminando imports no utilizados...")
        modified = self.remove_unused_imports(content, unused)
        
        # Mostrar diferencia de líneas
        original_lines = len(content.split('\n'))
        final_lines = len(modified.split('\n'))
        lines_diff = original_lines - final_lines
        
        print(f"\n📊 Resumen de cambios:")
        print(f"   Líneas originales: {original_lines}")
        print(f"   Líneas finales: {final_lines}")
        if lines_diff != 0:
            print(f"   Diferencia: {lines_diff:+d} líneas")
        
        # Si es dry-run, no guardar
        if self.dry_run:
            print(f"\n🔍 [DRY-RUN] No se guardaron cambios")
            print(f"\nPara aplicar los cambios, ejecuta sin --dry-run:")
            print(f"   ./.venv/bin/python utils/cleanup_imports.py {self.file_path}")
            return True
        
        # Crear backup antes de guardar
        self.create_backup()
        
        # Guardar cambios
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(modified)
        
        # Validar el archivo modificado
        print("\n🔍 Validando cambios...")
        is_valid, error = self.run_basic_checks()
        
        if is_valid:
            print("✅ Validación exitosa")
            self.remove_backup()
            print(f"✅ Archivo limpiado correctamente: {self.file_path}")
            return True
        else:
            print(f"\n❌ Validación falló: {error}")
            print("🔄 Revirtiendo cambios...")
            self.restore_backup()
            self.remove_backup()
            print(f"✅ Archivo restaurado a su estado original")
            raise Exception("Sintaxis inválida después de limpieza - cambios revertidos")


def find_python_files(directory: Path, recursive: bool = True) -> List[Path]:
    """
    Encuentra todos los archivos Python en un directorio.
    
    Args:
        directory: Directorio a buscar
        recursive: Si True, busca en subdirectorios. Si False, solo en el nivel actual.
    
    Returns:
        Lista de archivos Python encontrados (excluyendo __init__.py y __pycache__)
    """
    if recursive:
        py_files = list(directory.rglob("*.py"))
    else:
        py_files = list(directory.glob("*.py"))
    
    # Excluir archivos __init__.py y archivos en __pycache__
    py_files = [
        f for f in py_files 
        if f.name != '__init__.py' and '__pycache__' not in str(f)
    ]
    
    return py_files


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Elimina imports no utilizados de archivos Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Archivo individual
  ./.venv/bin/python cleanup_imports.py app/core/config.py
  ./.venv/bin/python cleanup_imports.py app/services/email_service.py --dry-run
  
  # Carpeta completa (recursivo por defecto)
  ./.venv/bin/python cleanup_imports.py app/services/
  ./.venv/bin/python cleanup_imports.py app/api/ --dry-run
  
  # Carpeta solo nivel actual (sin subcarpetas)
  ./.venv/bin/python cleanup_imports.py app/api/routes/ --no-recursive
  
  # Todos los archivos en app/
  ./.venv/bin/python cleanup_imports.py --all
        """
    )
    
    parser.add_argument(
        'filepath',
        nargs='?',
        help='Ruta del archivo o carpeta Python a procesar'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Muestra los cambios sin aplicarlos'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Procesa todos los archivos Python en app/'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Si se especifica una carpeta, procesa subcarpetas recursivamente'
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Si se especifica una carpeta, solo procesa archivos en ese nivel (no subcarpetas)'
    )
    parser.add_argument(
        '--stop-on-error',
        action='store_true',
        help='Detiene el procesamiento completo si encuentra un error de sintaxis en algún archivo'
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.filepath and not args.all:
        parser.error("Debes especificar un archivo/carpeta o usar --all")
    
    if args.all and args.filepath:
        parser.error("No puedes usar --all con un archivo/carpeta específico")
    
    if args.recursive and args.no_recursive:
        parser.error("No puedes usar --recursive y --no-recursive al mismo tiempo")
    
    # Determinar si es recursivo (por defecto True a menos que se especifique --no-recursive)
    recursive = not args.no_recursive
    
    # Procesar archivos
    files_to_process = []
    
    if args.all:
        # Procesar toda la carpeta app/
        app_dir = Path(__file__).parent.parent / 'app'
        if not app_dir.exists():
            print(f"❌ Error: No se encontró la carpeta app/ en {app_dir.parent}")
            sys.exit(1)
        files_to_process = find_python_files(app_dir, recursive=True)
        print(f"\n🔍 Encontrados {len(files_to_process)} archivos Python en app/")
    else:
        # Procesar archivo o carpeta específica
        target = Path(args.filepath)
        
        if not target.exists():
            print(f"❌ Error: No se encontró {target}")
            sys.exit(1)
        
        if target.is_file():
            # Es un archivo
            if target.suffix != '.py':
                print(f"❌ Error: {target} no es un archivo Python")
                sys.exit(1)
            files_to_process = [target]
        elif target.is_dir():
            # Es una carpeta
            files_to_process = find_python_files(target, recursive=recursive)
            mode = "recursivamente" if recursive else "en el nivel actual"
            print(f"\n🔍 Encontrados {len(files_to_process)} archivos Python en {target} ({mode})")
            
            if len(files_to_process) == 0:
                print(f"⚠️ No se encontraron archivos Python")
                sys.exit(0)
        else:
            print(f"❌ Error: {target} no es un archivo ni una carpeta válida")
            sys.exit(1)
    
    # Procesar todos los archivos encontrados
    success_count = 0
    error_count = 0
    
    for filepath in files_to_process:
        try:
            cleaner = ImportCleaner(str(filepath), args.dry_run)
            cleaner.clean()
            success_count += 1
            print()  # Línea en blanco entre archivos
        except Exception as e:
            print(f"❌ Error procesando {filepath}: {e}")
            error_count += 1
            print()
            
            # Si está habilitado --stop-on-error, detener el flujo completo
            if args.stop_on_error:
                print(f"\n🛑 Deteniendo procesamiento debido a error (--stop-on-error activado)")
                print(f"\n📊 Resumen hasta el error:")
                print(f"   Archivos procesados antes del error: {success_count}")
                print(f"   Archivos pendientes: {len(files_to_process) - success_count - error_count}")
                print(f"\n💡 El archivo con error fue revertido a su estado original")
                sys.exit(1)
    
    # Resumen final
    if len(files_to_process) > 1:
        print(f"\n{'='*60}")
        print(f"📊 Resumen final:")
        print(f"   Total de archivos: {len(files_to_process)}")
        print(f"   ✅ Exitosos: {success_count}")
        if error_count > 0:
            print(f"   ❌ Con errores: {error_count}")
            print(f"\n⚠️ Archivos con error fueron revertidos a su estado original")
            print(f"💡 Usa --stop-on-error para detener el flujo al primer error")
    
    print(f"\n{'🔍 Simulación completada' if args.dry_run else '✅ Limpieza completada'}\n")
    
    # Si hubo errores y no es dry-run, salir con código de error
    if error_count > 0 and not args.dry_run:
        sys.exit(1)


if __name__ == '__main__':
    main()
