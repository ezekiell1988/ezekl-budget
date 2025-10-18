# Script de Inicio del Proyecto

## 📝 Descripción

`start.py` es un script automatizado que prepara y ejecuta todo el stack del proyecto ezekl-budget.

## 🚀 Uso

### macOS/Linux:
```bash
python3 ./utils/start.py
```

### Windows:
```bash
python ./utils/start.py
```

### O directamente (si el archivo es ejecutable):
```bash
./utils/start.py
```

## ⚙️ Proceso Automático

El script ejecuta las siguientes tareas en orden:

1. **Activación del entorno virtual** 🔄
   - Detecta si el entorno virtual está activo
   - Si no lo está, reinicia el script usando el Python del `.venv`
   - Esto asegura que todas las dependencias estén disponibles

2. **Limpieza de logs** 🧹
   - Ejecuta `cleanup_logs.py` sobre el directorio `app/`
   - Elimina archivos de log antiguos o innecesarios

3. **Limpieza de imports** 📦
   - Ejecuta `cleanup_imports.py` sobre el directorio `app/`
   - Optimiza y organiza las importaciones de Python

4. **Construcción de Ionic** 🏗️
   - Ejecuta `npm run build` en el proyecto Ionic
   - Genera los archivos estáticos en `www/`

5. **Inicio del servidor FastAPI** 🌐
   - Inicia la aplicación principal con `python -m app.main`
   - El servidor queda corriendo hasta que presiones `Ctrl+C`

## ✅ Requisitos

- Entorno virtual creado en `.venv/`
- Node.js y npm instalados
- Todas las dependencias Python instaladas en el venv
- Estructura del proyecto intacta

## 🛑 Detener el Servidor

Presiona `Ctrl+C` en la terminal para detener el servidor FastAPI.

## 📊 Salidas

El script muestra:
- ✅ Confirmación de cada paso completado exitosamente
- ⚠️ Advertencias si falla la limpieza (pero continúa)
- ❌ Errores críticos si falla la construcción de Ionic o el inicio del servidor

## 🔧 Manejo de Errores

- **Limpieza de logs/imports falla**: El script continúa con una advertencia
- **Build de Ionic falla**: El script se detiene (error crítico)
- **Servidor falla**: El script se detiene y muestra el error

## 💡 Ventajas

- ✨ Ejecuta todo el proceso con un solo comando
- ✨ Activa automáticamente el entorno virtual
- ✨ Verifica pre-requisitos antes de comenzar
- ✨ Maneja errores de forma inteligente
- ✨ Muestra progreso visual con emojis y formato
