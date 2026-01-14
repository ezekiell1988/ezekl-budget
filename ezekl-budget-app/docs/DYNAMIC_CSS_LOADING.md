# Carga Dinámica de CSS - Sistema Completo

## 🎯 Solución: CERO CSS hasta detectar plataforma

**Principio**: No se carga ningún CSS de framework hasta saber si es desktop o mobile.

## 📋 Arquitectura

```
Application Start
├── styles.css (SOLO FontAwesome + mínimos)
│
├── cleanAllStyles() ← Limpieza preventiva
│
├── Detect Platform
│   ├── Desktop (>768px)
│   │   ├── Add class: desktop-mode
│   │   └── Load: desktop.css
│   │
│   └── Mobile (≤768px)
│       ├── Add class: ionic-mode
│       └── Load: mobile.css (compilado de ionic.scss)
│
└── On Window Resize
    ├── cleanAllStyles() ← Limpieza TOTAL
    ├── Reset: stylesLoaded = false
    └── Load CSS for new mode
```

## 📦 CSS Files

### Desktop (1 archivo):
- **`desktop.css`** - Compilado de `src/scss/angular.scss`
  - Incluye Color-Admin + componentes Angular
  - Tamaño: ~2.5MB
  - Se carga vía `DESKTOP_CSS_FILES = ['desktop.css']`

### Mobile (1 archivo compilado):
- **`mobile.css`** - Compilado de `src/scss/ionic.scss`
  - Incluye todos los CSS core de Ionic Framework:
    - `core.css`, `structure.css`, `typography.css`, `display.css`
    - `padding.css`, `float-elements.css`, `text-alignment.css`
    - `text-transformation.css`, `flex-utils.css`
    - `palettes/dark.class.css` (dark mode)
  - Incluye estructura modular personalizada:
    - `_variables.scss` - Variables CSS y configuración
    - `_layout.scss` - Estructura de página
    - `_components.scss` - Componentes Ionic personalizados
    - `_pages.scss` - Estilos específicos de páginas
    - `_theme-panel.scss` - Panel de tema
    - `_dark-mode.scss` - Modo oscuro
  - Tamaño: ~1.8MB
  - Se carga vía `IONIC_CSS_FILES = ['mobile.css']`

## 🔧 Implementación

### 1. angular.json

```json
"styles": [
  {
    "input": "src/styles.css",
    "bundleName": "styles",
    "inject": true  // ← Solo estilos globales
  },
  {
    "input": "src/scss/angular.scss",
    "bundleName": "desktop",
    "inject": false  // ← Carga dinámica para desktop
  },
  {
    "input": "src/scss/ionic.scss",
    "bundleName": "mobile",
    "inject": false  // ← Carga dinámica para mobile
  }
]
```

### 2. styles.css

```css
/* FontAwesome Icons */
@import '~@fortawesome/fontawesome-free/css/all.css';

/* Variables de Ionic para overlays (modals, alerts, action-sheets)
   Necesarias porque se renderizan fuera del <body> */
:root {
  --ion-color-primary: #348fe2;
  --ion-color-primary-rgb: 52, 143, 226;
  --ion-color-primary-contrast: #ffffff;
  --ion-color-primary-contrast-rgb: 255, 255, 255;
  --ion-color-primary-shade: #2e7ec7;
  --ion-color-primary-tint: #489ae5;
}

/* Ocultar elementos de Color-Admin en modo móvil */
body.ionic-mode {
  #header.app-header,
  #sidebar.app-sidebar,
  /* ... otros elementos ... */ {
    display: none !important;
  }
}
```

### 3. platform-detector.service.ts

```typescript
constructor() {
  // 1. Limpieza preventiva
  this.cleanAllStyles();
  
  // 2. Detectar modo
  const mode = this.getInitialMode();
  this.updateBodyClasses(mode);
  
  // 3. Cargar CSS correspondiente
  if (mode === 'mobile') {
    this.loadIonicStyles();
  } else {
    this.loadDesktopStyles();
  }
}

// Al cambiar de tamaño
handleStylesChange(mode: PlatformMode) {
  this.cleanAllStyles();              // Limpiar TODO
  this.appSettings.stylesLoaded = false;
  
  if (mode === 'mobile') {
    this.loadIonicStyles();
  } else {
    this.loadDesktopStyles();
  }
}

// Limpieza total
cleanAllStyles() {
  this.unloadIonicStyles();
  this.unloadDesktopStyles();
  // Limpiar cualquier link de estilo dinámico que pueda quedar
  const dynamicLinks = document.querySelectorAll(
    'link[id^="ionic-dynamic-"], link[id^="desktop-dynamic-"]'
  );
  dynamicLinks.forEach(link => link.remove());
}
```

## 🧪 Verificaciones en DevTools

### Verificar Desktop (>768px):

```javascript
// DevTools → Console
document.querySelectorAll('link[id^="desktop-dynamic"]').length
// Debe retornar: 1 (desktop.css)

document.querySelectorAll('link[id^="ionic-dynamic"]').length
// Debe retornar: 0

document.body.classList.contains('desktop-mode')
// Debe retornar: true

document.body.classList.contains('ionic-mode')
// Debe retornar: false
```

### Verificar Mobile (≤768px):

```javascript
// DevTools → Console
document.querySelectorAll('link[id^="ionic-dynamic"]').length
// Debe retornar: 1 (mobile.css)

document.querySelectorAll('link[id^="desktop-dynamic"]').length
// Debe retornar: 0

document.body.classList.contains('ionic-mode')
// Debe retornar: true

document.body.classList.contains('desktop-mode')
// Debe retornar: false
```

### Verificar Mobile (≤768px):

```javascript
// DevTools → Console
document.querySelectorAll('link[id^="ionic-dynamic"]').length
// Debe retornar: 1 (mobile.css)

document.querySelectorAll('link[id^="desktop-dynamic"]').length
// Debe retornar: 0

document.body.classList.contains('ionic-mode')
// Debe retornar: true
```

### Verificar Limpieza al Cambiar:

1. Abrir Console
2. Redimensionar ventana cruzando 768px
3. Ver logs:
   ```
   "Platform mode changed to: mobile"
   "Cleaning all dynamic styles..."
   "Loading Ionic CSS files dynamically..."
   "Files to load: [\"mobile.css\"]"
   "Loaded 1/1: mobile.css"
   "All Ionic CSS files loaded successfully"
   ```

## ⚠️ Reglas Críticas

### ❌ NUNCA hacer:

1. Agregar `@import` de frameworks en `styles.css`
2. Cambiar `inject: false` a `true` en angular.json
3. Cargar CSS sin limpiar primero
4. Cargar manualmente archivos CSS individuales de Ionic (usar mobile.css compilado)

### ✅ SIEMPRE hacer:

1. Limpiar con `cleanAllStyles()` antes de cargar
2. Verificar que solo un set de CSS esté activo
3. Actualizar clases del body al cambiar modo
4. Esperar a `stylesLoaded = true` antes de renderizar

## 🔍 Troubleshooting

### Problema: CSS no se carga

```javascript
// Console
document.querySelectorAll('link[rel="stylesheet"]').forEach(l => 
  console.log(l.id, l.href, l.sheet ? 'loaded' : 'loading')
);
```

### Problema: Conflictos entre frameworks

```javascript
// Forzar limpieza total
document.querySelectorAll('link[id*="-dynamic-"]').forEach(l => l.remove());
// Recargar página
location.reload();
```

### Problema: Scroll no funciona (Desktop)

```javascript
// Verificar que NO hay Ionic cargado
document.querySelectorAll('link[id^="ionic-dynamic"]').length === 0
// Si retorna false, hay un problema de limpieza
```

## 📊 Estado de CSS en Runtime

```typescript
// Obtener estado actual
const cssState = {
  mode: document.body.className,
  width: window.innerWidth + 'px',
  ionicFiles: document.querySelectorAll('link[id^="ionic-dynamic"]').length,
  desktopFiles: document.querySelectorAll('link[id^="desktop-dynamic"]').length,
  darkMode: document.documentElement.getAttribute('data-bs-theme'),
  expected: window.innerWidth <= 768 ? '1 file (mobile.css)' : '1 file (desktop.css)'
};

console.table(cssState);
```

## 🌓 Dark Mode

### Implementación Unificada

El dark mode se controla mediante el atributo `data-bs-theme` en `document.documentElement` (`<html>`):

```typescript
// Activar dark mode
document.documentElement.setAttribute('data-bs-theme', 'dark');

// Desactivar dark mode
document.documentElement.removeAttribute('data-bs-theme');
// o
document.documentElement.setAttribute('data-bs-theme', 'light');
```

### Selectores CSS

**✅ Correcto** - Busca en `<html>`:
```scss
[data-bs-theme="dark"] {
  ion-toolbar {
    --background: var(--bs-dark, #1a1d20);
  }
}
```

**❌ Incorrecto** - Buscaría en `<body>`:
```scss
body[data-bs-theme="dark"] {
  ion-toolbar { ... }
}
```

### Sincronización Desktop ↔ Mobile

- ✅ Mismo atributo: `data-bs-theme` en `<html>`
- ✅ Mismo localStorage: `localStorage["appDarkMode"]`
- ✅ Mismo selector CSS: `[data-bs-theme="dark"]`
- ✅ Funcionan ambos frameworks (Bootstrap y Ionic)

## 🎬 Flujo Completo

```
1. App Init
   └── Load styles.css only

2. Platform Detector Init
   ├── cleanAllStyles()
   ├── getInitialMode()
   ├── updateBodyClasses()
   └── loadStyles()

3. Styles Load
   ├── Create <link> tags
   ├── Append to <head>
   ├── Wait for onload
   └── Set stylesLoaded = true

4. App Render
   └── Show content

5. Window Resize (cross 768px)
   ├── Detect new mode
   ├── cleanAllStyles()
   ├── Reset stylesLoaded
   ├── Load new styles
   └── Update UI
```
