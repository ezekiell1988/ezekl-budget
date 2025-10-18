# 🗄️ SQL Execute Tool - Ejecutor de Stored Procedures

Herramienta avanzada para ejecutar archivos SQL con análisis de fases y medición de tiempos de rendimiento.

## 📍 Ubicación

- **Script ejecutor**: `/utils/sql_execute.py` (junto con otros scripts utilitarios)
- **Archivos SQL**: `/ezekl-budget/*.sql` (stored procedures y scripts SQL)

### 📄 Archivos SQL Disponibles (en `/ezekl-budget/`)

| Archivo | Tamaño | Descripción |
|---------|--------|-------------|
| `data_table.sql` | 3.9K | Creación/actualización de tablas de datos |
| `spAccountingAccountGet.sql` | 1.8K | Obtener cuentas contables |
| `spAccountingAccountGetOne.sql` | 653B | Obtener una cuenta contable específica |
| `spLoginAuth.sql` | 1.2K | Autenticación de login |
| `spLoginLoginMicrosoftAssociate.sql` | 2.8K | Asociar login con cuenta Microsoft |
| `spLoginMicrosoftAddOrEdit.sql` | 8.8K | Agregar o editar login Microsoft |
| `spLoginTokenAdd.sql` | 1.3K | Agregar token de login |

## 🚀 Uso Rápido

```bash
# Ejecutar desde el directorio raíz del proyecto
# El script busca automáticamente los archivos .sql en /ezekl-budget/
.venv/bin/python -m utils.sql_execute --file=spLoginTokenAdd --verbose

# O directamente con la ruta completa
.venv/bin/python utils/sql_execute.py --file=spLoginTokenAdd --verbose

# Ejemplo: ejecutar data_table.sql que está en /ezekl-budget/
.venv/bin/python -m utils.sql_execute --file=data_table
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
- Archivo `.env` con todas las variables base
- Archivo `.env.local` opcional (para sobrescribir variables localmente)
- Archivos SQL ubicados en `/ezekl-budget/` (ej: `spLoginTokenAdd.sql`, `data_table.sql`, etc.)

### Configuración de Variables de Entorno

El script carga variables de entorno de forma jerárquica:

1. **`.env`** - Archivo base con todas las variables (Azure, BD, etc.)
2. **`.env.local`** - Sobrescribe solo variables específicas (opcional)

#### Archivo `.env.local` (para desarrollo local)
```env
# Solo las variables que necesitas sobrescribir
DB_HOST=20.246.83.239
DB_USER=sa
DB_PASSWORD=tu_password_local

# Las demás variables se cargan automáticamente desde .env
```

#### Archivo `.env` (base - requerido)
Debe contener todas las variables necesarias:
- Variables de Azure OpenAI
- Variables de Azure Communication Services
- Variables de Base de Datos (valores por defecto)
- Variables de deployment
- Etc.

## 🛠️ Opciones de Uso

### Sintaxis Básica
```bash
# Como módulo (recomendado)
.venv/bin/python -m utils.sql_execute --file=<archivo> [opciones]

# O directamente
.venv/bin/python utils/sql_execute.py --file=<archivo> [opciones]
```

### Opciones Disponibles
- `--file=<nombre_archivo>` o `-f <nombre_archivo>` : Nombre del archivo SQL a ejecutar (sin extensión .sql)
- `--verbose` o `-v` : Mostrar información detallada de cada declaración
- `--help` o `-h` : Mostrar ayuda del comando

### Ejemplos de Uso

#### Ejecución Simple
```bash
# Ejecutar archivo spLoginTokenAdd.sql ubicado en /ezekl-budget/
# (desde directorio raíz del proyecto)
.venv/bin/python -m utils.sql_execute --file=spLoginTokenAdd

# O con ruta directa
.venv/bin/python utils/sql_execute.py --file=spLoginTokenAdd

# Ejecutar data_table.sql
.venv/bin/python -m utils.sql_execute --file=data_table
```

#### Ejecución con Detalles Verbosos
```bash
# Ejecutar archivo spLoginTokenAdd.sql con información detallada
.venv/bin/python -m utils.sql_execute --file=spLoginTokenAdd --verbose

# Usando banderas cortas
.venv/bin/python -m utils.sql_execute -f spLoginTokenAdd -v
```

#### Ejecución de Otros Archivos SQL
```bash
# Todos los archivos SQL están en /ezekl-budget/

# Ejecutar archivo spLoginAuth.sql
.venv/bin/python -m utils.sql_execute --file=spLoginAuth --verbose

# Ejecutar archivo spAccountingAccountGet.sql
.venv/bin/python -m utils.sql_execute --file=spAccountingAccountGet --verbose

# Ejecutar archivo data_table.sql
.venv/bin/python -m utils.sql_execute --file=data_table

# Ejecutar archivo spLoginTokenAdd.sql
.venv/bin/python -m utils.sql_execute --file=spLoginTokenAdd -v
```

#### Mostrar Ayuda
```bash
# Ver todas las opciones disponibles
.venv/bin/python -m utils.sql_execute --help
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

### Sistema de Variables de Entorno (Jerárquico)

El script implementa un sistema de carga jerárquica de variables:

```
1. .env          → Carga todas las variables base
2. .env.local    → Sobrescribe solo variables específicas (override=True)
3. settings      → Usa las variables finales combinadas
```

#### Variables de Base de Datos utilizadas:
- `DB_HOST`: Servidor de base de datos
- `DB_USER`: Usuario de conexión
- `DB_PASSWORD`: Contraseña
- `DB_NAME`: Base de datos objetivo
- `DB_PORT`: Puerto de conexión (por defecto 1433)
- `DB_DRIVER`: Driver ODBC
- `DB_TRUST_CERT`: Confiar en certificado del servidor

### Logging
- **Nivel INFO**: Información general de ejecución
- **Nivel DEBUG**: Detalles de conexión a base de datos
- **Nivel ERROR**: Errores y fallos

## 🚨 Solución de Problemas

### Error: "command not found: python"
```bash
# Usar python3 explícitamente
.venv/bin/python3 utils/sql_execute.py --file=spLoginTokenAdd

# O activar el entorno virtual primero
source .venv/bin/activate
python -m utils.sql_execute --file=spLoginTokenAdd
```

### Error: "No module named 'utils'"
```bash
# Asegúrate de ejecutar el comando desde el directorio raíz del proyecto
cd /Users/ezequielbaltodanocubillo/Documents/ezekl/ezekl-budget

# Luego ejecuta el comando
.venv/bin/python -m utils.sql_execute --file=spLoginTokenAdd
```

### Error: "No se pudo conectar a la base de datos"
1. Verificar que `.env` existe en el directorio raíz con todas las variables base
2. Si usas configuración local diferente, crear `.env.local` con las variables a sobrescribir
3. Confirmar credenciales correctas (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT)
4. Confirmar que el servidor SQL está accesible desde tu máquina
5. Validar permisos del usuario de base de datos
6. Verificar que el driver ODBC está instalado: `odbcinst -j`

### Error: "Archivo no encontrado"
1. **Verificar ubicación**: Los archivos `.sql` deben estar en el directorio `/ezekl-budget/`
2. **Usar nombre sin extensión**: El script agrega automáticamente `.sql` (ej: `--file=data_table`)
3. **Listar archivos disponibles**:
   ```bash
   ls -la ezekl-budget/*.sql
   ```
4. **Verificar permisos**: El archivo debe tener permisos de lectura
5. **Nota importante**: Los archivos SQL están en `/ezekl-budget/` NO en `/utils/`

### Error: "ModuleNotFoundError"
```bash
# Verificar que el entorno virtual está activo y tiene las dependencias
.venv/bin/pip install -r requirements.txt

# Verificar la ruta de Python
which python
.venv/bin/python --version
```

## 📝 Notas Importantes

- **Ubicación del script**: `/utils/sql_execute.py` (herramienta utilitaria)
- **Ubicación de archivos SQL**: `/ezekl-budget/*.sql` (⚠️ IMPORTANTE: aquí se buscan los archivos)
- **Directorio de trabajo**: Debe ejecutarse desde el directorio raíz del proyecto
- **Búsqueda automática**: El script busca automáticamente en `/ezekl-budget/` los archivos SQL
- **Variables de entorno**: 
  - `.env` (requerido): Todas las variables base del proyecto
  - `.env.local` (opcional): Solo las variables a sobrescribir localmente
- **Conexiones**: Usa pooling de conexiones asíncronas para mejor rendimiento
- **Transacciones**: Soporta transacciones explícitas con BEGIN TRAN/ROLLBACK
- **Seguridad**: Usa parámetros seguros para evitar inyección SQL
- **Compatibilidad**: Diseñado para SQL Server 2019+

## � Estructura de Directorios

```
ezekl-budget/
├── .env                                # ✅ Variables base (requerido, en Git)
├── .env.local                          # ✅ Variables locales (opcional, NO en Git)
├── .venv/                              # Entorno virtual de Python
├── utils/
│   ├── sql_execute.py                  # ✅ Script ejecutor (NUEVA UBICACIÓN)
│   ├── sql_execute.md                  # ✅ Documentación (NUEVA UBICACIÓN)
│   └── cleanup_logs.py                 # Otro script utilitario
└── ezekl-budget/
    ├── spLoginTokenAdd.sql             # Archivos SQL a ejecutar
    ├── spLoginAuth.sql
    ├── spAccountingAccountGet.sql
    └── ... otros archivos .sql
```

## 🔗 Archivos Relacionados

- **Script principal**: `utils/sql_execute.py` (herramienta)
- **Documentación**: `utils/sql_execute.md` (este archivo)
- **Archivos SQL disponibles** (ubicados en `/ezekl-budget/`):
  - `spLoginTokenAdd.sql` - Agregar token de login
  - `spLoginAuth.sql` - Autenticación de login
  - `spAccountingAccountGet.sql` - Obtener cuentas contables
  - `spAccountingAccountGetOne.sql` - Obtener una cuenta contable
  - `data_table.sql` - Crear/actualizar tablas de datos
  - Otros archivos `.sql` en el directorio
- **Configuración**: 
  - `.env` - Variables base del proyecto (requerido)
  - `.env.local` - Sobrescribe variables locales (opcional)

### Listar Archivos SQL Disponibles
```bash
# Ver todos los archivos SQL disponibles para ejecutar
ls -la ezekl-budget/*.sql

# Ejemplo de salida:
# ezekl-budget/data_table.sql
# ezekl-budget/spAccountingAccountGet.sql
# ezekl-budget/spAccountingAccountGetOne.sql
# ezekl-budget/spLoginAuth.sql
# ezekl-budget/spLoginTokenAdd.sql
```

## 🎯 Flujo de Trabajo Típico

```bash
# 1. Activar entorno virtual (opcional)
source .venv/bin/activate

# 2. Navegar al directorio raíz del proyecto
cd /Users/ezequielbaltodanocubillo/Documents/ezekl/ezekl-budget

# 3. Ver archivos SQL disponibles en /ezekl-budget/
ls ezekl-budget/*.sql

# 4. Ejecutar el script SQL deseado (el script busca en /ezekl-budget/)
.venv/bin/python -m utils.sql_execute --file=spLoginTokenAdd --verbose

# Otro ejemplo: ejecutar data_table.sql
.venv/bin/python -m utils.sql_execute --file=data_table

# 5. Revisar los resultados en la terminal
```

### 📝 Notas sobre la Ubicación de Archivos

- 🔧 **Script ejecutor**: Se encuentra en `/utils/sql_execute.py`
- 📄 **Archivos SQL**: Deben estar en `/ezekl-budget/` (ej: `ezekl-budget/data_table.sql`)
- ⚙️ **Ejecución**: Siempre desde el directorio raíz del proyecto
- 🔍 **Búsqueda automática**: El script busca los archivos SQL en `/ezekl-budget/` automáticamente

---

**Desarrollado para ezekl-budget** | **Versión 2.0 con análisis de fases** | **Ubicado en `/utils/`**