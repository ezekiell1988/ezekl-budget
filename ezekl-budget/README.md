# 🗄️ SQL Execute Tool - Ejecutor de Stored Procedures

Herramienta avanzada para ejecutar archivos SQL con análisis de fases y medición de tiempos de rendimiento.

## 🚀 Uso Rápido

```bash
# Ejecutar el archivo spLoginTokenAdd.sql
.venv/bin/python -m ezekl-budget.sql_execute --file=spLoginTokenAdd --verbose
```

## 📋 Descripción

Este script permite ejecutar archivos SQL de forma estructurada, organizando automáticamente las declaraciones en **tres fases distintas** con medición precisa de tiempos:

1. **🗑️ FASE 1: Borrar SP existente** - Elimina stored procedures existentes
2. **🔨 FASE 2: Crear/Recrear SP** - Crea nuevos stored procedures  
3. **🚀 FASE 3: Ejecutar ejemplo** - Ejecuta ejemplos de uso (con o sin transacciones)

## 📦 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- Entorno virtual configurado (`.venv`)
- Archivo `.env.local` con credenciales de base de datos

### Configuración de Base de Datos (.env.local)
```env
DB_HOST=tu_servidor_db
DB_USER=tu_usuario_db
DB_PASSWORD=tu_password_seguro
DB_DATABASE=budgetdb
DB_PORT=1433
```

## 🛠️ Opciones de Uso

### Sintaxis Básica
```bash
.venv/bin/python ezekl-budget/sql_execute.py --file=<archivo> [opciones]
```

### Opciones Disponibles
- `--file=<nombre_archivo>` : Nombre del archivo SQL a ejecutar (sin extensión .sql)
- `--verbose` : Mostrar información detallada de cada declaración
- `--help` : Mostrar ayuda del comando

### Ejemplos de Uso

#### Ejecución Simple
```bash
# Ejecutar archivo spLoginTokenAdd.sql
.venv/bin/python ezekl-budget/sql_execute.py --file=spLoginTokenAdd
```

#### Ejecución con Detalles Verbosos
```bash
# Ejecutar archivo spLoginTokenAdd.sql con información detallada
.venv/bin/python ezekl-budget/sql_execute.py --file=spLoginTokenAdd --verbose
```

#### Ejecución como Módulo
```bash
# Ejecutar archivo spLoginAuth.sql como módulo
.venv/bin/python -m ezekl-budget.sql_execute --file=spLoginAuth --verbose
```

## 📊 Ejemplo de Salida

```
Encontradas 3 fases para ejecutar:
  1. 🗑️  FASE 1: Borrar SP existente (1 declaraciones)
  2. 🔨 FASE 2: Crear/Recrear SP (1 declaraciones)  
  3. 🚀 FASE 3: Ejecutar ejemplo (con transacción) (1 declaraciones)

🗑️  FASE 1: Borrar SP existente
===============================
  ✓ Declaración 1 ejecutada exitosamente (151.13ms)
✓ Fase completada exitosamente: 1/1 declaraciones (151.46ms)

🔨 FASE 2: Crear/Recrear SP
==========================
  ✓ Declaración 1 ejecutada exitosamente (177.50ms)
✓ Fase completada exitosamente: 1/1 declaraciones (177.77ms)

🚀 FASE 3: Ejecutar ejemplo (con transacción)
============================================
  ✓ Declaración 1 ejecutada exitosamente (83.40ms)
✓ Fase completada exitosamente: 1/1 declaraciones (83.99ms)

======================================================================
RESUMEN DETALLADO DE EJECUCIÓN
======================================================================
🗑️  FASE 1: Borrar SP existente | ✓ ÉXITO      |   151.46ms
🔨 FASE 2: Crear/Recrear SP     | ✓ ÉXITO      |   177.77ms
🚀 FASE 3: Ejecutar ejemplo     | ✓ ÉXITO      |    83.99ms
----------------------------------------------------------------------
TIEMPO TOTAL                    |              |   414.11ms
ESTADO GENERAL                  | ✓ ÉXITO COMPLETO
======================================================================
```

## 🎯 Características Principales

### ⏱️ Medición Precisa de Tiempos
- **Precisión**: Milisegundos con 2 decimales
- **Granularidad**: Por declaración y por fase
- **Tiempo total**: Medición completa del proceso

### 🔍 Análisis Automático de Fases
El script detecta automáticamente el tipo de declaraciones:
- `DROP PROCEDURE` → Fase 1 (Borrar SP)
- `CREATE PROCEDURE` → Fase 2 (Crear SP)
- `EXEC/EXECUTE/BEGIN TRAN` → Fase 3 (Ejecutar ejemplo)

### 🛡️ Manejo Inteligente de Errores
- **Errores esperados**: Ignora errores de DROP cuando el SP no existe
- **Errores críticos**: Detiene ejecución y reporta problemas
- **Transacciones**: Soporte completo para BEGIN TRAN/ROLLBACK

### 📁 Búsqueda Automática de Archivos
- Busca archivos con y sin extensión `.sql`
- Soporte para rutas relativas y absolutas
- Validación de existencia de archivos

## 🗂️ Estructura de Archivos SQL Soportada

### Archivo Ejemplo: `spLoginTokenAdd.sql`
```sql
-- FASE 1: Borrar SP existente
DROP PROCEDURE IF EXISTS spLoginTokenAdd
GO

-- FASE 2: Crear SP
CREATE PROCEDURE spLoginTokenAdd
  @json NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  -- Lógica del procedimiento aquí
END
GO

-- FASE 3: Ejecutar ejemplo
BEGIN TRAN
EXEC spLoginTokenAdd @json = N'{"codeLogin":"S"}';
ROLLBACK TRAN
GO
```

## 🔧 Configuración Avanzada

### Variables de Entorno
El script lee automáticamente la configuración de `.env.local`:
- `DB_HOST`: Servidor de base de datos
- `DB_USER`: Usuario de conexión
- `DB_PASSWORD`: Contraseña
- `DB_DATABASE`: Base de datos objetivo
- `DB_PORT`: Puerto de conexión (por defecto 1433)

### Logging
- **Nivel INFO**: Información general de ejecución
- **Nivel DEBUG**: Detalles de conexión a base de datos
- **Nivel ERROR**: Errores y fallos

## 🚨 Solución de Problemas

### Error: "command not found: python"
```bash
# Usar python3 explícitamente
.venv/bin/python3 ezekl-budget/sql_execute.py --file=spLoginTokenAdd
```

### Error: "No se pudo conectar a la base de datos"
1. Verificar `.env.local` existe y tiene las credenciales correctas
2. Confirmar que el servidor SQL está accesible
3. Validar permisos del usuario de base de datos

### Error: "Archivo no encontrado"
1. Verificar que el archivo `.sql` existe en el directorio `ezekl-budget/`
2. Usar nombre sin extensión (se agrega automáticamente)
3. Verificar permisos de lectura del archivo

## 📝 Notas Importantes

- **Conexiones**: Usa pooling de conexiones asíncronas para mejor rendimiento
- **Transacciones**: Soporta transacciones explícitas con BEGIN TRAN/ROLLBACK
- **Seguridad**: Usa parámetros seguros para evitar inyección SQL
- **Compatibilidad**: Diseñado para SQL Server 2019+

## 🔗 Archivos Relacionados

- `sql_execute.py`: Script principal
- `spLoginTokenAdd.sql`: Ejemplo de stored procedure
- `spLoginAuth.sql`: Otro ejemplo disponible
- `.env.local`: Configuración de base de datos

---

**Desarrollado para ezekl-budget** | **Versión 2.0 con análisis de fases**