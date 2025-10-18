# 🧹 cleanup_logs.py

Script para limpiar logs excesivos y prints en archivos Python.

## 🎯 Funcionalidad

- **Elimina** todos los `logger.info()`, `logger.debug()` y `print()`
- **Mantiene** `logger.warning()`, `logger.error()`, `logger.critical()`
- **Valida sintaxis** automáticamente y revierte cambios si hay errores
- **Preserva integridad** del código (agrega `pass` donde sea necesario)

## 📋 Ejemplo

**Antes:**
```python
if x_hub_signature_256:
    logger.info(f"🔐 Firma: {x_hub_signature_256}")
    print("Procesando firma...")
else:
    logger.warning("⚠️ Sin firma")
```

**Después:**
```python
if x_hub_signature_256:
    pass  # Logger/print eliminado
else:
    logger.warning("⚠️ Sin firma")
```

## 🚀 Uso

```bash
# Archivo individual
./.venv/bin/python utils/cleanup_logs.py <archivo.py> [--dry-run]

# Carpeta completa (recursivo por defecto)
./.venv/bin/python utils/cleanup_logs.py <carpeta> [--dry-run]

# Carpeta solo nivel actual (sin subcarpetas)
./.venv/bin/python utils/cleanup_logs.py <carpeta> --no-recursive [--dry-run]

# Todos los archivos en app/
./.venv/bin/python utils/cleanup_logs.py --all [--dry-run]
```

### Ejemplos

```bash
# Archivo individual
./.venv/bin/python utils/cleanup_logs.py app/api/routes/whatsapp.py --dry-run
./.venv/bin/python utils/cleanup_logs.py app/api/routes/whatsapp.py

# Carpeta completa (con subcarpetas)
./.venv/bin/python utils/cleanup_logs.py app/services/ --dry-run
./.venv/bin/python utils/cleanup_logs.py app/api/

# Carpeta sin subcarpetas
./.venv/bin/python utils/cleanup_logs.py app/api/routes/ --no-recursive

# Todos los archivos
./.venv/bin/python utils/cleanup_logs.py --all --dry-run
```

## 📝 Opciones

| Opción | Descripción |
|--------|-------------|
| `--dry-run` | Previsualiza cambios sin aplicarlos |
| `--all` | Procesa todos los archivos en `app/` recursivamente |
| `--recursive`, `-r` | Procesa subcarpetas recursivamente (default para carpetas) |
| `--no-recursive` | Solo procesa archivos en el nivel actual de la carpeta |
| `--stop-on-error` | Detiene todo el procesamiento al primer error de sintaxis |

## 📊 Salida Ejemplo

```
🧹 Procesando: app/api/routes/whatsapp.py
   Eliminando TODAS las líneas con logger.

📊 Resumen de cambios:
   Líneas originales: 903
   Líneas finales: 856
   Diferencia: -47 líneas

✨ Optimizaciones realizadas:
   • Eliminadas 64 líneas con logger/print
   • Agregados 17 'pass' para mantener integridad

✅ Archivo actualizado: app/api/routes/whatsapp.py
🔍 Validando sintaxis...
✅ Sintaxis válida

✅ Limpieza completada
```

## ⚠️ Importante

- **Valida automáticamente** la sintaxis después de limpiar cada archivo
- **Revierte cambios** automáticamente si detecta errores de sintaxis
- Por defecto **continúa** con otros archivos si encuentra un error
- Usa `--stop-on-error` para **detener todo** al primer error
- Siempre usa `--dry-run` primero para previsualizar
- Revisa cambios con `git diff` antes de commitear

## 🔄 Comportamiento ante errores

**Sin `--stop-on-error` (default):**
```bash
# Procesa todos los archivos, revierte solo los que fallan
./.venv/bin/python utils/cleanup_logs.py app/services/
# ✅ archivo1.py - OK
# ❌ archivo2.py - ERROR (revertido)
# ✅ archivo3.py - OK
# Resultado: 2 exitosos, 1 con error
```

**Con `--stop-on-error`:**
```bash
# Se detiene al primer error
./.venv/bin/python utils/cleanup_logs.py app/services/ --stop-on-error
# ✅ archivo1.py - OK
# ❌ archivo2.py - ERROR (revertido) → 🛑 DETIENE
# ⏸️  archivo3.py - No procesado
```
