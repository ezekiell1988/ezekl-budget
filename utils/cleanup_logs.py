#!/usr/bin/env python3
"""
Script para limpiar logs excesivos y cambiar niveles de logging en archivos Python.

Lógica de limpieza:
1. Identifica logs por nivel (INFO, DEBUG, WARNING, ERROR)
2. Elimina logs decorativos/verbosos configurables
3. Cambia niveles de logs técnicos (INFO → DEBUG)
4. Mantiene integridad del código (agrega 'pass' si es necesario)

Uso:
    # Archivo individual
    python cleanup_logs.py <archivo.py> [--dry-run]
    
    # Carpeta (recursivo por defecto)
    python cleanup_logs.py <carpeta> [--dry-run]
    
    # Carpeta solo nivel actual (sin subcarpetas)
    python cleanup_logs.py <carpeta> --no-recursive [--dry-run]
    
    # Todos los archivos en app/
    python cleanup_logs.py --all [--dry-run]

Ejemplos:
    python cleanup_logs.py app/api/routes/whatsapp.py --dry-run
    python cleanup_logs.py app/services/ --recursive
    python cleanup_logs.py app/api/ --no-recursive
    python cleanup_logs.py --all

Opciones:
    --dry-run: Muestra los cambios sin aplicarlos
    --all: Procesa todos los archivos Python en app/
    --recursive, -r: Procesa subcarpetas recursivamente (default para carpetas)
    --no-recursive: Solo procesa archivos en el nivel actual de la carpeta
    --stop-on-error: Detiene todo el procesamiento al primer error

Comportamiento ante errores:
    - Sin --stop-on-error (default): Continúa procesando, revierte solo archivos con error
    - Con --stop-on-error: Se detiene completamente al primer error de sintaxis
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Set


class LogCleaner:
    """Limpia logs excesivos y optimiza niveles de logging manteniendo la integridad del código."""
    
    def __init__(self, filepath: str, dry_run: bool = False, 
                 remove_levels: Set[str] = None, change_to_debug: bool = True):
        self.filepath = Path(filepath)
        self.dry_run = dry_run
        self.remove_levels = remove_levels or {'INFO'}  # Por defecto solo INFO decorativo
        self.change_to_debug = change_to_debug
        self.changes: List[Tuple[int, str, str]] = []
        
    def read_file(self) -> str:
        """Lee el contenido del archivo."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {self.filepath}")
        return self.filepath.read_text(encoding='utf-8')
    
    def _is_logger_line(self, line: str) -> tuple:
        """
        Determina si una línea contiene logger.info o logger.debug (a eliminar).
        Returns: (is_logger, level, content_after_logger)
        """
        stripped = line.strip()
        # Solo considerar logger.info y logger.debug
        if stripped.startswith('logger.info(') or stripped.startswith('logger.debug('):
            return (True, 'TO_REMOVE', stripped)
        
        return (False, None, None)
    
    def _count_logger_lines(self, lines: list, start_index: int) -> int:
        """
        Cuenta cuántas líneas ocupa un statement de logger (incluyendo multilínea).
        Cuenta paréntesis para determinar cuándo termina el statement.
        
        Returns:
            Número de líneas adicionales (0 si es single-line, N si es multilínea)
        """
        first_line = lines[start_index]
        
        # Contar paréntesis en la primera línea
        open_count = first_line.count('(')
        close_count = first_line.count(')')
        
        # Si está balanceado en la primera línea, no hay continuación
        if open_count == close_count:
            return 0
        
        # Buscar líneas siguientes hasta balancear paréntesis
        additional_lines = 0
        current_balance = open_count - close_count
        
        for i in range(start_index + 1, len(lines)):
            additional_lines += 1
            line = lines[i]
            open_count = line.count('(')
            close_count = line.count(')')
            current_balance += (open_count - close_count)
            
            # Cuando se balancea, terminó el statement
            if current_balance == 0:
                return additional_lines
            
            # Límite de seguridad (no más de 10 líneas de continuación)
            if additional_lines >= 10:
                return additional_lines
        
        return additional_lines
    
    def _should_remove_log(self, line, level) -> bool:
        """
        Elimina logger.info y logger.debug solamente.
        Mantiene logger.warning, logger.error, logger.critical
        """
        return level == 'TO_REMOVE'
    
    def _get_indentation(self, line: str) -> str:
        """Obtiene la indentación de una línea."""
        return line[:-len(line.lstrip())]
    
    def _is_control_structure(self, line: str) -> bool:
        """Verifica si una línea es una estructura de control (if, for, while, etc)."""
        stripped = line.strip()
        control_keywords = ['if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ']
        return any(stripped.startswith(kw) or (':' in stripped and stripped.split(':')[0].strip().startswith(kw.strip())) 
                   for kw in control_keywords)
    
    def _look_up(self, lines: list, current_index: int) -> str:
        """
        Mira hacia arriba saltando espacios y comentarios.
        Returns: 'logger' | 'control' | 'other'
        """
        for i in range(current_index - 1, -1, -1):
            line = lines[i].strip()
            
            # Saltar vacías y comentarios
            if not line or line.startswith('#'):
                continue
            
            # Es logger?
            if line.startswith('logger.'):
                return 'logger'
            
            # Es estructura de control?
            if self._is_control_structure(lines[i]):
                return 'control'
            
            # Es otra cosa (código normal)
            return 'other'
        
        return 'other'
    
    def _look_down(self, lines: list, current_index: int, current_indent: str) -> str:
        """
        Mira hacia abajo saltando espacios y comentarios.
        Returns: 'logger' | 'control' | 'other' | 'end' | 'else'
        """
        for i in range(current_index + 1, len(lines)):
            line = lines[i]
            
            # Saltar vacías y comentarios
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # Obtener indentación
            next_indent = self._get_indentation(line)
            
            # Si tiene menos indentación, terminó el bloque
            if len(next_indent) < len(current_indent):
                # Pero verificar si es un else/elif al mismo nivel del if original
                if len(next_indent) == len(current_indent) - 4:  # Un nivel menos
                    stripped = line.strip()
                    if stripped.startswith('else:') or stripped.startswith('elif '):
                        return 'else'
                return 'end'
            
            # Si tiene mayor indentación, continuamos buscando al mismo nivel
            # (esto puede ser código dentro de un bloque que viene después de loggers)
            if len(next_indent) > len(current_indent):
                continue
            
            # Ahora estamos al mismo nivel de indentación
            
            # Es logger?
            if line.strip().startswith('logger.'):
                return 'logger'
            
            # Es estructura de control?
            if self._is_control_structure(line):
                return 'control'
            
            # Es otra cosa (código normal)
            return 'other'
        
        return 'end'
    
    def process_lines(self, content: str) -> str:
        """
        Procesa líneas con logger. según la lógica:
        1. Buscar logger.
        2. Mirar ARRIBA (saltando espacios/comentarios):
           - Si hay logger → ELIMINAR
           - Si hay control (if/for/while) → Paso 3
        3. Mirar ABAJO (saltando espacios/comentarios):
           - Si hay logger → ELIMINAR
           - Si hay control → Paso 4
        4. Si ARRIBA=control Y ABAJO=control → PASS
        5. Caso contrario → ELIMINAR
        """
        lines = content.split('\n')
        result_lines = []
        removed_count = 0
        added_pass = 0
        
        i = 0
        while i < len(lines):
            line = lines[i]
            is_logger, _, _ = self._is_logger_line(line)
            
            if is_logger:
                indent = self._get_indentation(line)
                
                # Contar cuántas líneas ocupa este logger statement (multilínea)
                continuation_lines = self._count_logger_lines(lines, i)
                
                # 1. Mirar ARRIBA
                up = self._look_up(result_lines, len(result_lines))
                
                # 2. Mirar ABAJO (después de las líneas de continuación)
                down = self._look_down(lines, i + continuation_lines, indent)
                
                # Lógica de decisión:
                # - Si ARRIBA es logger → simplemente eliminar (hay más logs seguidos)
                # - Si ABAJO es logger → simplemente eliminar (hay más logs seguidos)
                # - Si ARRIBA es control Y (ABAJO es control O else O end) → agregar pass
                # - Caso contrario → eliminar
                
                if up == 'logger' or down == 'logger':
                    # Hay otros loggers cerca, solo eliminar (incluyendo líneas de continuación)
                    removed_count += 1
                    i += continuation_lines + 1
                    continue
                
                if up == 'control' and (down in ['control', 'else', 'end']):
                    # Estructura de control quedaría vacía, agregar pass
                    result_lines.append(f"{indent}pass  # Logger eliminado")
                    added_pass += 1
                    removed_count += 1
                    i += continuation_lines + 1
                    continue
                
                # Caso contrario, simplemente eliminar (incluyendo líneas de continuación)
                removed_count += 1
                i += continuation_lines + 1
                continue
            
            # Línea normal, mantenerla
            result_lines.append(line)
            i += 1
        
        # Registrar cambios
        if removed_count > 0:
            self.changes.append((0, f"Eliminadas {removed_count} líneas con logger.", ""))
        if added_pass > 0:
            self.changes.append((0, f"Agregados {added_pass} 'pass' para mantener integridad", ""))
        
        return '\n'.join(result_lines)
    
    def change_main_log_level(self, content: str) -> str:
        """Cambia el nivel de logging principal de DEBUG a INFO."""
        pattern = r'logging\.basicConfig\(\s*level=logging\.DEBUG,'
        replacement = 'logging.basicConfig(\n    level=logging.INFO,'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            self.changes.append((0, "Cambiado nivel principal: DEBUG -> INFO", ""))
        
        return content
    
    def clean(self) -> str:
        """Ejecuta el proceso de limpieza completo con validaciones."""
        print(f"\n🧹 Procesando: {self.filepath}")
        print(f"   Eliminando TODAS las líneas con logger.")
        
        content = self.read_file()
        original_lines = len(content.split('\n'))
        
        # Aplicar transformaciones
        content = self.process_lines(content)
        content = self.change_main_log_level(content)
        
        final_lines = len(content.split('\n'))
        lines_diff = original_lines - final_lines
        
        # Mostrar resumen
        print(f"\n📊 Resumen de cambios:")
        print(f"   Líneas originales: {original_lines}")
        print(f"   Líneas finales: {final_lines}")
        if lines_diff != 0:
            print(f"   Diferencia: {lines_diff:+d} líneas")
        
        if self.changes:
            print(f"\n✨ Optimizaciones realizadas:")
            for _, change, _ in self.changes:
                print(f"   • {change}")
        else:
            print(f"\n✅ No se encontraron logs para limpiar")
        
        return content
    
    def save(self, content: str):
        """Guarda el contenido procesado y valida sintaxis."""
        if self.dry_run:
            print(f"\n🔍 [DRY-RUN] No se guardaron cambios")
            print(f"\nPara aplicar los cambios, ejecuta sin --dry-run:")
            print(f"   python cleanup_logs.py {self.filepath}")
        else:
            # Guardar contenido original para poder revertir
            original_content = self.filepath.read_text(encoding='utf-8')
            
            # Escribir nuevo contenido
            self.filepath.write_text(content, encoding='utf-8')
            print(f"\n✅ Archivo actualizado: {self.filepath}")
            
            # Validar sintaxis de Python
            print(f"🔍 Validando sintaxis...")
            import py_compile
            import tempfile
            
            try:
                # Intentar compilar el archivo
                py_compile.compile(str(self.filepath), doraise=True)
                print(f"✅ Sintaxis válida")
            except py_compile.PyCompileError as e:
                # Error de sintaxis, revertir cambios
                print(f"\n❌ ERROR DE SINTAXIS DETECTADO:")
                print(f"   {e}")
                print(f"\n🔄 Revirtiendo cambios...")
                self.filepath.write_text(original_content, encoding='utf-8')
                print(f"✅ Archivo restaurado a su estado original")
                raise Exception("Sintaxis inválida después de limpieza - cambios revertidos")


def find_python_files(directory: Path, recursive: bool = True) -> List[Path]:
    """
    Encuentra todos los archivos Python en un directorio.
    
    Args:
        directory: Directorio a buscar
        recursive: Si True, busca en subdirectorios. Si False, solo en el nivel actual.
    
    Returns:
        Lista de archivos Python encontrados
    """
    if recursive:
        return list(directory.rglob("*.py"))
    else:
        return list(directory.glob("*.py"))


def main():
    parser = argparse.ArgumentParser(
        description="Limpia logs excesivos y optimiza niveles de logging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Archivo individual
  python cleanup_logs.py app/main.py
  python cleanup_logs.py app/api/routes/whatsapp.py --dry-run
  
  # Carpeta completa (recursivo por defecto)
  python cleanup_logs.py app/services/
  python cleanup_logs.py app/api/ --dry-run
  
  # Carpeta solo nivel actual (sin subcarpetas)
  python cleanup_logs.py app/api/routes/ --no-recursive
  
  # Todos los archivos en app/
  python cleanup_logs.py --all
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
    parser.add_argument(
        '--remove-levels',
        nargs='+',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=['INFO'],
        help='Niveles de log a eliminar si son decorativos (default: INFO)'
    )
    parser.add_argument(
        '--no-change-to-debug',
        action='store_true',
        help='NO cambiar logs técnicos de INFO a DEBUG'
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.filepath and not args.all:
        parser.error("Debes especificar un archivo/carpeta o usar --all")
    
    if args.all and args.filepath:
        parser.error("No puedes usar --all con un archivo/carpeta específico")
    
    if args.recursive and args.no_recursive:
        parser.error("No puedes usar --recursive y --no-recursive al mismo tiempo")
    
    # Configurar parámetros de limpieza
    remove_levels = set(args.remove_levels)
    change_to_debug = not args.no_change_to_debug
    
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
            cleaner = LogCleaner(str(filepath), args.dry_run, remove_levels, change_to_debug)
            content = cleaner.clean()
            cleaner.save(content)
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


if __name__ == "__main__":
    main()
