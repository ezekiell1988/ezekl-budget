# Cleanup Imports - Limpiador de Imports No Utilizados

Script para eliminar automáticamente los imports no utilizados de archivos Python, con validación y reversión automática en caso de errores.

## Características

- ✅ Detecta y elimina imports no utilizados
- ✅ Crea backup automático antes de modificar
- ✅ Valida sintaxis después de los cambios
- ✅ Revierte cambios automáticamente si hay errores
- ✅ Soporta archivos individuales o directorios completos
- ✅ Maneja imports multilínea
- ✅ Excluye automáticamente `__init__.py` y `__pycache__`

## Uso

**Nota:** Este script debe ejecutarse usando el Python del virtual environment del proyecto.

### Procesar un archivo individual

```bash
./.venv/bin/python utils/cleanup_imports.py app/services/email_service.py [--dry-run]
```

### Procesar carpeta completa (recursivo por defecto)

```bash
# Procesa la carpeta y todas sus subcarpetas
./.venv/bin/python utils/cleanup_imports.py app/services/ [--dry-run]
```

### Procesar solo nivel actual (sin subdirectorios)

```bash
# Usa --no-recursive para NO incluir subcarpetas
./.venv/bin/python utils/cleanup_imports.py app/api/routes/ --no-recursive [--dry-run]
```

### Procesar todos los archivos en app/

```bash
./.venv/bin/python utils/cleanup_imports.py --all [--dry-run]
```

## Ejemplos

### Ejemplo 1: Limpiar un archivo específico

```bash
./.venv/bin/python utils/cleanup_imports.py app/main.py
```

Salida:
```
============================================================
Procesando: app/main.py
============================================================
✓ Backup creado: app/main.py.backup

Analizando imports...

✓ Imports no utilizados encontrados: 3
  - datetime
  - json
  - os

Eliminando imports no utilizados...
  Eliminando: import os
  Eliminando: import json
  Eliminando: from datetime import datetime

Validando cambios...
✓ Validación exitosa
✓ Backup eliminado
✓ Archivo limpiado correctamente: app/main.py
```

### Ejemplo 2: Limpiar todos los servicios

```bash
./.venv/bin/python utils/cleanup_imports.py app/services/
```

### Ejemplo 3: Limpiar toda la aplicación

```bash
./.venv/bin/python utils/cleanup_imports.py --all
```

### Ejemplo 4: Previsualizar cambios (dry-run)

```bash
# Ver qué cambios se harían sin aplicarlos
./.venv/bin/python utils/cleanup_imports.py app/core/config.py --dry-run
./.venv/bin/python utils/cleanup_imports.py app/services/ --dry-run
```

## 📝 Opciones

| Opción | Descripción |
|--------|-------------|
| `--dry-run` | Previsualiza cambios sin aplicarlos |
| `--all` | Procesa todos los archivos en `app/` recursivamente |
| `--no-recursive` | Solo procesa archivos en el nivel actual de la carpeta (por defecto es recursivo) |
| `--stop-on-error` | Detiene todo el procesamiento al primer error de sintaxis |

**Nota:** Por defecto, cuando se procesa una carpeta, se hace **recursivamente** (incluye subcarpetas). Usa `--no-recursive` para procesar solo el nivel actual.

## Cómo funciona

1. **Backup**: Crea una copia `.backup` del archivo original
2. **Análisis**: 
   - Extrae todos los nombres importados
   - Analiza el código para detectar qué nombres se usan
   - Identifica imports no utilizados
3. **Limpieza**: Elimina las líneas de imports no utilizados
4. **Validación**:
   - Verifica la sintaxis con `ast.parse()`
   - Compila el archivo con `py_compile`
5. **Reversión**: Si la validación falla, restaura el archivo original
6. **Limpieza**: Si todo va bien, elimina el backup

## Limitaciones

- No detecta imports usados en strings (ej: `eval()`, `exec()`)
- No analiza imports dinámicos
- No procesa archivos `__init__.py` por defecto
- Los comentarios sobre la línea de import se mantienen

## Seguridad

El script es **seguro** de usar porque:
- Siempre crea un backup antes de modificar
- Valida los cambios antes de confirmarlos
- Revierte automáticamente si detecta problemas
- No modifica el archivo si hay errores de sintaxis originales

## Casos de uso comunes

### Limpiar después de refactorización

```bash
# Después de mover funciones entre archivos (recursivo por defecto)
./.venv/bin/python utils/cleanup_imports.py app/services/
```

### Antes de hacer commit

```bash
# Limpiar solo los archivos modificados
./.venv/bin/python utils/cleanup_imports.py app/api/routes/budget.py
```

### Auditoría completa del proyecto

```bash
# Revisar todo el proyecto (recursivo por defecto)
./.venv/bin/python utils/cleanup_imports.py app/
# O usar --all para toda la carpeta app/
./.venv/bin/python utils/cleanup_imports.py --all
```

## 🔄 Comportamiento ante errores

**Sin `--stop-on-error` (default):**
```bash
# Procesa todos los archivos, revierte solo los que fallan
./.venv/bin/python utils/cleanup_imports.py app/services/
# ✅ archivo1.py - OK
# ❌ archivo2.py - ERROR (revertido)
# ✅ archivo3.py - OK
# Resultado: 2 exitosos, 1 con error
```

**Con `--stop-on-error`:**
```bash
# Se detiene al primer error
./.venv/bin/python utils/cleanup_imports.py app/services/ --stop-on-error
# ✅ archivo1.py - OK
# ❌ archivo2.py - ERROR (revertido) → 🛑 DETIENE
# ⏸️  archivo3.py - No procesado
```

## Integración con Git

Puedes agregar este script como un pre-commit hook:

```bash
# .git/hooks/pre-commit
#!/bin/bash
./.venv/bin/python utils/cleanup_imports.py --all
```

## Notas adicionales

- Los archivos `.backup` se eliminan automáticamente después de una limpieza exitosa
- Si el script se interrumpe, puedes encontrar el backup con extensión `.py.backup`
- Para restaurar manualmente: `cp archivo.py.backup archivo.py`
- Usa `--dry-run` para previsualizar cambios sin aplicarlos
- Por defecto excluye archivos `__init__.py` y directorios `__pycache__`
