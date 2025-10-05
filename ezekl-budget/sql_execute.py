#!/usr/bin/env python3
"""
Ejecutor de archivos SQL para ezekl-budget.
Permite ejecutar archivos .sql directamente en la base de datos desde la línea de comandos.

Uso:
    python -m sql_execute --file=spLoginTokenAdd
    python -m sql_execute --file=spLoginTokenAdd.sql
    python -m sql_execute --file=spLoginAuth --verbose
"""

import os
import sys
import argparse
import asyncio
import time
import logging
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Cargar variables de entorno desde .env.local
env_local_path = Path(__file__).parent.parent / '.env.local'
if env_local_path.exists():
    load_dotenv(env_local_path)
    print(f"Cargado archivo de configuración: {env_local_path}")
else:
    print(f"Archivo .env.local no encontrado en: {env_local_path}")

# Agregar el directorio padre al path para importar módulos de la app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.database.connection import async_db_manager

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Resultado de ejecución de una fase."""
    phase_name: str
    execution_time_ms: float
    success: bool
    result_data: any = None
    error_message: str = None


@dataclass
class PhaseInfo:
    """Información de una fase de ejecución."""
    name: str
    statements: List[str]
    use_transaction: bool = False


class SQLExecutor:
    """Ejecutor de archivos SQL en la base de datos."""
    
    def __init__(self):
        """Inicializa el ejecutor SQL."""
        self.current_dir = Path(__file__).parent
        logger.info(f"SQLExecutor inicializado en directorio: {self.current_dir}")
    
    def find_sql_file(self, filename: str) -> Optional[Path]:
        """
        Busca un archivo SQL en el directorio actual.
        
        Args:
            filename (str): Nombre del archivo (con o sin extensión .sql)
            
        Returns:
            Optional[Path]: Ruta del archivo encontrado o None si no existe
        """
        # Asegurar que tenga extensión .sql
        if not filename.endswith('.sql'):
            filename += '.sql'
        
        file_path = self.current_dir / filename
        
        if file_path.exists():
            logger.info(f"Archivo encontrado: {file_path}")
            return file_path
        
        logger.error(f"Archivo no encontrado: {file_path}")
        return None
    
    def read_sql_file(self, file_path: Path) -> str:
        """
        Lee el contenido de un archivo SQL.
        
        Args:
            file_path (Path): Ruta del archivo SQL
            
        Returns:
            str: Contenido del archivo
            
        Raises:
            Exception: Si hay error al leer el archivo
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Archivo leído exitosamente: {file_path.name} ({len(content)} caracteres)")
            return content
            
        except Exception as e:
            logger.error(f"Error al leer archivo {file_path}: {str(e)}")
            raise Exception(f"Error al leer archivo: {str(e)}")
    
    def split_sql_statements(self, sql_content: str) -> list[str]:
        """
        Divide el contenido SQL en declaraciones individuales usando GO como separador.
        
        Args:
            sql_content (str): Contenido SQL completo
            
        Returns:
            list[str]: Lista de declaraciones SQL individuales
        """
        # Dividir por GO (case insensitive) - GO debe estar en su propia línea
        statements = []
        lines = sql_content.split('\n')
        current_statement = []
        
        for line in lines:
            stripped_line = line.strip()
            
            # Si la línea es solo "GO" (case insensitive), terminar la declaración actual
            if stripped_line.upper() == 'GO':
                if current_statement:
                    statement = '\n'.join(current_statement).strip()
                    if statement:  # Solo agregar declaraciones no vacías
                        statements.append(statement)
                    current_statement = []
            else:
                # No incluir la línea GO en la declaración
                current_statement.append(line)
        
        # Agregar la última declaración si existe
        if current_statement:
            statement = '\n'.join(current_statement).strip()
            if statement:
                statements.append(statement)
        
        # Si no hay declaraciones GO, tratar todo el contenido como una sola declaración
        if not statements and sql_content.strip():
            # Remover todas las líneas GO del contenido
            cleaned_content = []
            for line in lines:
                if line.strip().upper() != 'GO':
                    cleaned_content.append(line)
            
            statement = '\n'.join(cleaned_content).strip()
            if statement:
                statements.append(statement)
        
        logger.info(f"SQL dividido en {len(statements)} declaraciones")
        return statements

    def parse_sql_phases(self, file_path: str) -> List[PhaseInfo]:
        """
        Analiza un archivo SQL y organiza las declaraciones en fases según el patrón estándar.
        
        Args:
            file_path (str): Ruta al archivo SQL
            
        Returns:
            List[PhaseInfo]: Lista de fases identificadas
        """
        # Leer y dividir las declaraciones del archivo
        try:
            sql_content = self.read_sql_file(file_path)
            statements = self.split_sql_statements(sql_content)
        except Exception as e:
            logger.error(f"No se pudo procesar el archivo {file_path}: {str(e)}")
            return []
        phases = []
        drop_statements = []
        create_statements = []
        example_statements = []
        
        for stmt in statements:
            stmt_upper = stmt.upper().strip()
            
            if stmt_upper.startswith('DROP '):
                drop_statements.append(stmt)
            elif stmt_upper.startswith('CREATE '):
                create_statements.append(stmt)
            elif (stmt_upper.startswith('EXEC ') or stmt_upper.startswith('EXECUTE ') or
                  stmt_upper.startswith('BEGIN TRAN') or stmt_upper.startswith('ROLLBACK')):
                example_statements.append(stmt)
            else:
                # Declaraciones que no encajan claramente, las agregamos a create por defecto
                create_statements.append(stmt)
        
        # Fase 1: Borrar SP si existe
        if drop_statements:
            phases.append(PhaseInfo(
                name="🗑️  FASE 1: Borrar SP existente",
                statements=drop_statements,
                use_transaction=False
            ))
        
        # Fase 2: Recrear SP
        if create_statements:
            phases.append(PhaseInfo(
                name="🔨 FASE 2: Crear/Recrear SP",
                statements=create_statements,
                use_transaction=False
            ))
        
        # Fase 3: Ejecutar ejemplo
        if example_statements:
            # Detectar si hay transacciones explícitas
            has_transaction = any('TRAN' in stmt.upper() for stmt in example_statements)
            
            phases.append(PhaseInfo(
                name=f"🚀 FASE 3: Ejecutar ejemplo {'(con transacción)' if has_transaction else '(sin transacción)'}",
                statements=example_statements,
                use_transaction=has_transaction
            ))
        
        return phases
    
    async def execute_phase(self, phase: PhaseInfo, verbose: bool = False) -> ExecutionResult:
        """
        Ejecuta una fase completa con medición de tiempo.
        
        Args:
            phase (PhaseInfo): Información de la fase a ejecutar
            verbose (bool): Si mostrar información detallada
            
        Returns:
            ExecutionResult: Resultado de la ejecución con tiempos
        """
        start_time = time.time()
        logger.info(f"\n{phase.name}")
        logger.info(f"{'=' * len(phase.name)}")
        
        success_count = 0
        total_statements = len(phase.statements)
        results = []
        
        try:
            for i, statement in enumerate(phase.statements, 1):
                stmt_start_time = time.time()
                
                if verbose:
                    logger.info(f"  Ejecutando declaración {i}/{total_statements}:")
                    logger.info(f"  SQL: {statement[:100]}..." if len(statement) > 100 else f"  SQL: {statement}")
                
                try:
                    result = await async_db_manager.execute_raw_query(statement)
                    stmt_time = (time.time() - stmt_start_time) * 1000
                    success_count += 1
                    
                    if verbose:
                        logger.info(f"  ✓ Declaración {i} ejecutada exitosamente ({stmt_time:.2f}ms)")
                        if result is not None and str(result) != "-1":
                            logger.info(f"    Resultado: {result}")
                    
                    results.append(result)
                
                except Exception as e:
                    stmt_time = (time.time() - stmt_start_time) * 1000
                    error_msg = str(e)
                    
                    # Ignorar errores específicos de DROP PROCEDURE cuando el procedimiento no existe
                    if ("Cannot drop the procedure" in error_msg and 
                        "because it does not exist" in error_msg and
                        "DROP PROCEDURE" in statement.upper()):
                        
                        logger.info(f"  ⚠ Declaración {i}: Procedimiento no existe - ignorando ({stmt_time:.2f}ms)")
                        if verbose:
                            logger.info(f"    SQL ignorado: {statement}")
                        success_count += 1
                        continue
                    
                    # Para otros errores, fallar
                    execution_time_ms = (time.time() - start_time) * 1000
                    logger.error(f"  ✗ Error en declaración {i}: {error_msg} ({stmt_time:.2f}ms)")
                    if verbose:
                        logger.error(f"    SQL fallido: {statement}")
                    
                    return ExecutionResult(
                        phase_name=phase.name,
                        execution_time_ms=execution_time_ms,
                        success=False,
                        error_message=error_msg
                    )
            
            execution_time_ms = (time.time() - start_time) * 1000
            logger.info(f"✓ Fase completada exitosamente: {success_count}/{total_statements} declaraciones ({execution_time_ms:.2f}ms)")
            
            return ExecutionResult(
                phase_name=phase.name,
                execution_time_ms=execution_time_ms,
                success=True,
                result_data=results
            )
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Error general ejecutando fase: {str(e)}")
            return ExecutionResult(
                phase_name=phase.name,
                execution_time_ms=execution_time_ms,
                success=False,
                error_message=str(e)
            )
    
    async def execute_file(self, filename: str, verbose: bool = False) -> bool:
        """
        Ejecuta un archivo SQL completo con análisis de fases y medición de tiempos.
        
        Args:
            filename (str): Nombre del archivo SQL a ejecutar
            verbose (bool): Si mostrar información detallada
            
        Returns:
            bool: True si el archivo se ejecutó exitosamente
        """
        logger.info(f"Iniciando ejecución de archivo SQL: {filename}")
        
        # Buscar el archivo
        file_path = self.find_sql_file(filename)
        if not file_path:
            return False
        
        # Probar conexión a la base de datos
        if not await async_db_manager.test_connection():
            logger.error("No se pudo conectar a la base de datos")
            return False
        
        total_start_time = time.time()
        
        try:
            # Parsear el archivo SQL en fases
            phases = self.parse_sql_phases(file_path)
            
            if not phases:
                logger.warning("No se encontraron fases SQL válidas en el archivo")
                return False
            
            logger.info(f"\nEncontradas {len(phases)} fases para ejecutar:")
            for i, phase in enumerate(phases, 1):
                logger.info(f"  {i}. {phase.name} ({len(phase.statements)} declaraciones)")
            
            # Ejecutar cada fase y recolectar resultados
            phase_results = []
            overall_success = True
            
            for phase in phases:
                result = await self.execute_phase(phase, verbose)
                phase_results.append(result)
                
                if not result.success:
                    overall_success = False
                    break
            
            total_execution_time_ms = (time.time() - total_start_time) * 1000
            
            # Mostrar resumen final detallado
            logger.info("\n" + "=" * 70)
            logger.info("RESUMEN DETALLADO DE EJECUCIÓN")
            logger.info("=" * 70)
            
            for result in phase_results:
                status = "✓ ÉXITO" if result.success else "✗ FALLÓ"
                logger.info(f"{result.phase_name:30} | {status:12} | {result.execution_time_ms:8.2f}ms")
                if not result.success and result.error_message:
                    logger.info(f"{'':30} | Error: {result.error_message}")
            
            logger.info("-" * 70)
            logger.info(f"{'TIEMPO TOTAL':30} | {'':12} | {total_execution_time_ms:8.2f}ms")
            logger.info(f"{'ESTADO GENERAL':30} | {'✓ ÉXITO COMPLETO' if overall_success else '✗ FALLÓ':12}")
            logger.info("=" * 70)
            
            if overall_success:
                logger.info(f"\n✓ Archivo {filename} ejecutado exitosamente")
            else:
                logger.error(f"\n✗ Error ejecutando archivo {filename}")
            
            return overall_success
            
        except Exception as e:
            total_execution_time_ms = (time.time() - total_start_time) * 1000
            logger.error(f"Error procesando archivo SQL: {str(e)}")
            logger.error(f"Tiempo hasta error: {total_execution_time_ms:.2f}ms")
            return False


async def main():
    """Función principal del programa."""
    parser = argparse.ArgumentParser(
        description='Ejecutor de archivos SQL para ezekl-budget',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos de uso:
  python -m sql_execute --file=spLoginTokenAdd
  python -m sql_execute --file=spLoginTokenAdd.sql
  python -m sql_execute --file=spLoginAuth --verbose
        '''
    )
    
    parser.add_argument(
        '--file', '-f',
        required=True,
        help='Nombre del archivo SQL a ejecutar (con o sin extensión .sql)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar información detallada durante la ejecución'
    )
    
    args = parser.parse_args()
    
    # Configurar nivel de logging si es verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Mostrar información de conexión
    logger.info(f"Conectando a base de datos: {settings.effective_db_host}:{settings.db_port}/{settings.db_name}")
    
    # Ejecutar el archivo SQL
    executor = SQLExecutor()
    success = await executor.execute_file(args.file, args.verbose)
    
    # Salir con código de error apropiado
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
