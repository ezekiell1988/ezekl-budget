# Guía Completa: Utilidades CSS de Ionic

> **Última actualización**: 15 de enero de 2026  
> **Versión de Ionic**: Framework 8.x  
> **Documentación oficial**: [CSS Utilities](https://ionicframework.com/docs/layout/css-utilities) | [Dark Mode](https://ionicframework.com/docs/theming/dark-mode)

## 📋 Tabla de Contenidos

- [Introducción](#introducción)
- [Modificación de Texto](#modificación-de-texto)
- [Posicionamiento de Elementos](#posicionamiento-de-elementos)
- [Visualización de Elementos](#visualización-de-elementos)
- [Espaciado de Contenido](#espaciado-de-contenido)
- [Propiedades de Contenedor Flex](#propiedades-de-contenedor-flex)
- [Propiedades de Elementos Flex](#propiedades-de-elementos-flex)
- [Bordes](#bordes)
- [Modo Oscuro (Dark Mode)](#modo-oscuro-dark-mode)
- [Breakpoints de Ionic](#breakpoints-de-ionic)
- [Mejores Prácticas](#mejores-prácticas)

---

## Introducción

Ionic Framework proporciona un conjunto completo de clases CSS utilitarias que pueden ser utilizadas en cualquier elemento para modificar el texto, posicionamiento de elementos, ajustar padding y margin, sin necesidad de escribir CSS personalizado.

### ⚠️ Importante

Si tu aplicación no fue iniciada usando un starter oficial de Ionic, necesitarás incluir las hojas de estilo listadas en la [sección opcional de hojas de estilo globales](https://ionicframework.com/docs/layout/global-stylesheets#optional) para que estos estilos funcionen.

**En tu archivo `src/global.scss` o `src/styles.css`:**

```css
/* Utilidades CSS opcionales que pueden ser comentadas */
@import '@ionic/angular/css/padding.css';
@import '@ionic/angular/css/float-elements.css';
@import '@ionic/angular/css/text-alignment.css';
@import '@ionic/angular/css/text-transformation.css';
@import '@ionic/angular/css/flex-utils.css';
@import '@ionic/angular/css/display.css';
```

---

## Modificación de Texto

### Alineación de Texto

Las clases de alineación de texto controlan cómo se posiciona el contenido inline dentro de las cajas de línea.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-text-left` | `text-align: left` | Alinea el contenido al borde izquierdo |
| `.ion-text-right` | `text-align: right` | Alinea el contenido al borde derecho |
| `.ion-text-start` | `text-align: start` | Igual que `left` si la dirección es LTR, `right` si es RTL |
| `.ion-text-end` | `text-align: end` | Igual que `right` si la dirección es LTR, `left` si es RTL |
| `.ion-text-center` | `text-align: center` | Centra el contenido inline |
| `.ion-text-justify` | `text-align: justify` | Justifica el texto (alinea bordes izquierdo y derecho) |
| `.ion-text-wrap` | `white-space: normal` | Permite que el texto se envuelva en múltiples líneas |
| `.ion-text-nowrap` | `white-space: nowrap` | Suprime los saltos de línea (el texto no se envuelve) |

**Ejemplo:**

```html
<ion-grid>
  <ion-row>
    <ion-col>
      <div class="ion-text-start">
        <h3>Alineado al inicio</h3>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
      </div>
    </ion-col>
    <ion-col>
      <div class="ion-text-end">
        <h3>Alineado al final</h3>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
      </div>
    </ion-col>
    <ion-col>
      <div class="ion-text-center">
        <h3>Centrado</h3>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
      </div>
    </ion-col>
  </ion-row>
</ion-grid>
```

### Transformación de Texto

Controla la capitalización del texto.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-text-uppercase` | `text-transform: uppercase` | Convierte todo el texto a MAYÚSCULAS |
| `.ion-text-lowercase` | `text-transform: lowercase` | Convierte todo el texto a minúsculas |
| `.ion-text-capitalize` | `text-transform: capitalize` | Convierte la primera letra de cada palabra a mayúscula |

**Ejemplo:**

```html
<ion-list>
  <ion-item>
    <ion-label class="ion-text-uppercase">Este texto está en mayúsculas</ion-label>
  </ion-item>
  <ion-item>
    <ion-label class="ion-text-lowercase">Este Texto Está en Minúsculas</ion-label>
  </ion-item>
  <ion-item>
    <ion-label class="ion-text-capitalize">este texto está capitalizado</ion-label>
  </ion-item>
</ion-list>
```

### Clases Responsivas de Texto

Todas las clases de texto tienen versiones responsivas. En lugar de `text-`, usa `text-{breakpoint}-{modificador}`:

| Clase | Aplicación |
|-------|-----------|
| `.ion-text-{modifier}` | Aplica el modificador en todos los tamaños de pantalla |
| `.ion-text-sm-{modifier}` | Aplica cuando `min-width: 576px` |
| `.ion-text-md-{modifier}` | Aplica cuando `min-width: 768px` |
| `.ion-text-lg-{modifier}` | Aplica cuando `min-width: 992px` |
| `.ion-text-xl-{modifier}` | Aplica cuando `min-width: 1200px` |

**Ejemplo:**

```html
<!-- Centro en móvil, alineado al inicio en tablets y superiores -->
<div class="ion-text-center ion-text-md-start">
  <h2>Título Responsivo</h2>
</div>
```

---

## Posicionamiento de Elementos

### Float

Las clases float permiten que un elemento se posicione a lo largo del lado izquierdo o derecho de su contenedor.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-float-left` | `float: left` | El elemento flota a la izquierda |
| `.ion-float-right` | `float: right` | El elemento flota a la derecha |
| `.ion-float-start` | `float: left / right` | Igual que `left` si es LTR, `right` si es RTL |
| `.ion-float-end` | `float: left / right` | Igual que `right` si es LTR, `left` si es RTL |

**Ejemplo:**

```html
<ion-grid>
  <ion-row>
    <ion-col>
      <h3>Float Left</h3>
      <img 
        src="https://ionicframework.com/docs/img/demos/avatar.svg"
        height="50px"
        class="ion-float-left"
      />
      <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ac vehicula lorem.</p>
    </ion-col>
  </ion-row>
</ion-grid>
```

### Clases Responsivas de Float

| Clase | Aplicación |
|-------|-----------|
| `.ion-float-{modifier}` | Aplica el modificador en todos los tamaños |
| `.ion-float-sm-{modifier}` | Aplica cuando `min-width: 576px` |
| `.ion-float-md-{modifier}` | Aplica cuando `min-width: 768px` |
| `.ion-float-lg-{modifier}` | Aplica cuando `min-width: 992px` |
| `.ion-float-xl-{modifier}` | Aplica cuando `min-width: 1200px` |

---

## Visualización de Elementos

### Display

Controla el tipo de caja de visualización de un elemento.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-display-none` | `display: none` | Oculta el elemento (no afecta el layout) |
| `.ion-display-inline` | `display: inline` | El elemento se comporta como inline |
| `.ion-display-inline-block` | `display: inline-block` | El elemento se comporta como bloque pero fluye inline |
| `.ion-display-block` | `display: block` | El elemento se comporta como bloque |
| `.ion-display-flex` | `display: flex` | Activa el modelo flexbox |
| `.ion-display-inline-flex` | `display: inline-flex` | Activa flexbox inline |
| `.ion-display-grid` | `display: grid` | Activa el modelo grid |
| `.ion-display-inline-grid` | `display: inline-grid` | Activa grid inline |
| `.ion-display-table` | `display: table` | Se comporta como elemento `<table>` |
| `.ion-display-table-cell` | `display: table-cell` | Se comporta como elemento `<td>` |
| `.ion-display-table-row` | `display: table-row` | Se comporta como elemento `<tr>` |

**Ejemplo:**

```html
<!-- Ocultar en móvil, mostrar en tablets -->
<div class="ion-display-none ion-display-md-block">
  <p>Este contenido solo es visible en tablets y superiores</p>
</div>

<!-- Mostrar en móvil, ocultar en desktop -->
<div class="ion-display-block ion-display-lg-none">
  <p>Este contenido solo es visible en móviles</p>
</div>
```

### Clases Responsivas de Display

| Clase | Aplicación |
|-------|-----------|
| `.ion-display-{modifier}` | Aplica en todos los tamaños |
| `.ion-display-sm-{modifier}` | Aplica cuando `min-width: 576px` |
| `.ion-display-md-{modifier}` | Aplica cuando `min-width: 768px` |
| `.ion-display-lg-{modifier}` | Aplica cuando `min-width: 992px` |
| `.ion-display-xl-{modifier}` | Aplica cuando `min-width: 1200px` |

### ⚠️ Clases Deprecadas

Estas clases están deprecadas y serán removidas en la próxima versión mayor:

| Clase Deprecada | Reemplazo |
|----------------|-----------|
| `.ion-hide` | `.ion-display-none` |
| `.ion-hide-sm-{dir}` | `.ion-display-sm-{modifier}` |
| `.ion-hide-md-{dir}` | `.ion-display-md-{modifier}` |
| `.ion-hide-lg-{dir}` | `.ion-display-lg-{modifier}` |
| `.ion-hide-xl-{dir}` | `.ion-display-xl-{modifier}` |

---

## Espaciado de Contenido

### Padding

El padding es el espacio entre el contenido del elemento y su borde. El valor por defecto es `16px` (configurado por la variable `--ion-padding`).

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-padding` | `padding: 16px` | Aplica padding a todos los lados |
| `.ion-padding-top` | `padding-top: 16px` | Aplica padding arriba |
| `.ion-padding-start` | `padding-start: 16px` | Aplica padding al inicio |
| `.ion-padding-end` | `padding-end: 16px` | Aplica padding al final |
| `.ion-padding-bottom` | `padding-bottom: 16px` | Aplica padding abajo |
| `.ion-padding-vertical` | `padding: 16px 0` | Aplica padding arriba y abajo |
| `.ion-padding-horizontal` | `padding: 0 16px` | Aplica padding a izquierda y derecha |
| `.ion-no-padding` | `padding: 0` | Elimina todo el padding |

**Ejemplo:**

```html
<ion-grid>
  <ion-row>
    <ion-col class="ion-padding">
      <div>Con padding en todos los lados</div>
    </ion-col>
    <ion-col class="ion-padding-top">
      <div>Solo padding arriba</div>
    </ion-col>
    <ion-col class="ion-padding-vertical">
      <div>Padding vertical (arriba y abajo)</div>
    </ion-col>
  </ion-row>
</ion-grid>
```

### Margin

El margin extiende el área del borde con un área vacía usada para separar el elemento de sus vecinos. El valor por defecto es `16px` (configurado por la variable `--ion-margin`).

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-margin` | `margin: 16px` | Aplica margin a todos los lados |
| `.ion-margin-top` | `margin-top: 16px` | Aplica margin arriba |
| `.ion-margin-start` | `margin-start: 16px` | Aplica margin al inicio |
| `.ion-margin-end` | `margin-end: 16px` | Aplica margin al final |
| `.ion-margin-bottom` | `margin-bottom: 16px` | Aplica margin abajo |
| `.ion-margin-vertical` | `margin: 16px 0` | Aplica margin arriba y abajo |
| `.ion-margin-horizontal` | `margin: 0 16px` | Aplica margin a izquierda y derecha |
| `.ion-no-margin` | `margin: 0` | Elimina todo el margin |

**Ejemplo:**

```html
<ion-content>
  <ion-card class="ion-margin">
    <ion-card-content>Card con margin en todos los lados</ion-card-content>
  </ion-card>
  
  <ion-button class="ion-margin-top">
    Botón con margin arriba
  </ion-button>
</ion-content>
```

---

## Propiedades de Contenedor Flex

Las propiedades flexbox se dividen en dos categorías: propiedades de contenedor (controlan el layout de todos los elementos flex) y propiedades de elementos (controlan elementos flex individuales).

### Align Items

Controla la alineación de elementos en el eje transversal (cross axis).

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-align-items-start` | `align-items: flex-start` | Elementos empaquetados al inicio del eje transversal |
| `.ion-align-items-end` | `align-items: flex-end` | Elementos empaquetados al final del eje transversal |
| `.ion-align-items-center` | `align-items: center` | Elementos centrados en el eje transversal |
| `.ion-align-items-baseline` | `align-items: baseline` | Elementos alineados por sus líneas base |
| `.ion-align-items-stretch` | `align-items: stretch` | Elementos estirados para llenar el contenedor |

**Ejemplo:**

```html
<div class="ion-display-flex ion-align-items-center" style="height: 200px;">
  <ion-button>Botón 1</ion-button>
  <ion-button>Botón 2</ion-button>
  <ion-button>Botón 3</ion-button>
</div>
```

### Align Content

Controla la distribución de espacio entre y alrededor de las líneas de contenido en el eje transversal.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-align-content-start` | `align-content: flex-start` | Líneas empaquetadas al inicio |
| `.ion-align-content-end` | `align-content: flex-end` | Líneas empaquetadas al final |
| `.ion-align-content-center` | `align-content: center` | Líneas centradas |
| `.ion-align-content-stretch` | `align-content: stretch` | Líneas estiradas para llenar el contenedor |
| `.ion-align-content-between` | `align-content: space-between` | Líneas distribuidas uniformemente |
| `.ion-align-content-around` | `align-content: space-around` | Líneas distribuidas con espacio igual alrededor |

### Justify Content

Define cómo el navegador distribuye el espacio entre y alrededor del contenido a lo largo del eje principal.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-justify-content-start` | `justify-content: flex-start` | Elementos empaquetados al inicio |
| `.ion-justify-content-end` | `justify-content: flex-end` | Elementos empaquetados al final |
| `.ion-justify-content-center` | `justify-content: center` | Elementos centrados |
| `.ion-justify-content-around` | `justify-content: space-around` | Elementos con espacio igual alrededor |
| `.ion-justify-content-between` | `justify-content: space-between` | Elementos distribuidos uniformemente |
| `.ion-justify-content-evenly` | `justify-content: space-evenly` | Espaciado igual entre cualquier par de elementos |

**Ejemplo:**

```html
<div class="ion-display-flex ion-justify-content-between">
  <ion-button>Inicio</ion-button>
  <ion-button>Centro</ion-button>
  <ion-button>Final</ion-button>
</div>
```

### Flex Direction

Establece cómo se colocan los elementos flex en el contenedor flex.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-flex-row` | `flex-direction: row` | Elementos en la misma dirección que el texto |
| `.ion-flex-row-reverse` | `flex-direction: row-reverse` | Elementos en dirección opuesta al texto |
| `.ion-flex-column` | `flex-direction: column` | Elementos colocados verticalmente |
| `.ion-flex-column-reverse` | `flex-direction: column-reverse` | Elementos verticalmente en orden inverso |

**Ejemplo:**

```html
<!-- Layout en columna en móvil, fila en desktop -->
<div class="ion-display-flex ion-flex-column ion-flex-lg-row">
  <ion-card>Card 1</ion-card>
  <ion-card>Card 2</ion-card>
  <ion-card>Card 3</ion-card>
</div>
```

### Flex Wrap

Establece si los elementos flex se fuerzan a una línea o pueden envolverse en múltiples líneas.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-flex-nowrap` | `flex-wrap: nowrap` | Todos los elementos en una línea |
| `.ion-flex-wrap` | `flex-wrap: wrap` | Elementos se envuelven en múltiples líneas (arriba a abajo) |
| `.ion-flex-wrap-reverse` | `flex-wrap: wrap-reverse` | Elementos se envuelven (abajo a arriba) |

### Clases Responsivas de Contenedor Flex

Todas las propiedades de contenedor flex tienen versiones responsivas usando el formato `.ion-{property}-{breakpoint}-{modifier}`.

**Ejemplo:**

```html
<!-- Centrado en móvil, space-between en tablets -->
<div class="ion-display-flex ion-justify-content-center ion-justify-content-md-between">
  <ion-chip>Chip 1</ion-chip>
  <ion-chip>Chip 2</ion-chip>
  <ion-chip>Chip 3</ion-chip>
</div>
```

### ⚠️ Clases Flex Deprecadas

| Clase Deprecada | Reemplazo |
|----------------|-----------|
| `.ion-nowrap` | `.ion-flex-nowrap` |
| `.ion-wrap` | `.ion-flex-wrap` |
| `.ion-wrap-reverse` | `.ion-flex-wrap-reverse` |

---

## Propiedades de Elementos Flex

Las propiedades de elementos flex controlan cómo los elementos flex individuales se comportan dentro de su contenedor flex.

### Align Self

Sobrescribe el valor de `align-items` para un elemento flex individual.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-align-self-start` | `align-self: flex-start` | Elemento empaquetado al inicio del eje transversal |
| `.ion-align-self-end` | `align-self: flex-end` | Elemento empaquetado al final del eje transversal |
| `.ion-align-self-center` | `align-self: center` | Elemento centrado en el eje transversal |
| `.ion-align-self-baseline` | `align-self: baseline` | Elemento alineado por su línea base |
| `.ion-align-self-stretch` | `align-self: stretch` | Elemento estirado para llenar el contenedor |
| `.ion-align-self-auto` | `align-self: auto` | Elemento posicionado según `align-items` del padre |

**Ejemplo:**

```html
<div class="ion-display-flex ion-align-items-start" style="height: 200px;">
  <ion-button>Normal</ion-button>
  <ion-button class="ion-align-self-center">Centrado</ion-button>
  <ion-button class="ion-align-self-end">Al final</ion-button>
</div>
```

### Flex

Propiedad shorthand para `flex-grow`, `flex-shrink` y `flex-basis`.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-flex-1` | `flex: 1` | Elemento crece y se encoge equitativamente con otros |
| `.ion-flex-auto` | `flex: auto` | Elemento crece/se encoge basado en su tamaño de contenido |
| `.ion-flex-initial` | `flex: initial` | Elemento se encoge pero no crece |
| `.ion-flex-none` | `flex: none` | Elemento no crece ni se encoge |

**Ejemplo:**

```html
<div class="ion-display-flex">
  <div class="ion-flex-1" style="background: lightblue;">
    Este div ocupa el espacio disponible
  </div>
  <div class="ion-flex-none" style="background: lightcoral; width: 100px;">
    Este div tiene ancho fijo
  </div>
</div>
```

### Flex Grow

Establece el factor de crecimiento del elemento flex.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-flex-grow-0` | `flex-grow: 0` | Elemento no crece más allá de su tamaño de contenido |
| `.ion-flex-grow-1` | `flex-grow: 1` | Elemento crece para llenar el espacio disponible |

### Flex Shrink

Establece el factor de encogimiento del elemento flex.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-flex-shrink-0` | `flex-shrink: 0` | Elemento no se encoge por debajo de su tamaño de contenido |
| `.ion-flex-shrink-1` | `flex-shrink: 1` | Elemento se encoge proporcionalmente cuando el contenedor es pequeño |

### Order

Establece el orden para colocar un elemento en un contenedor flex o grid.

| Clase | Propiedad CSS | Descripción |
|-------|--------------|-------------|
| `.ion-order-first` | `order: -1` | Elemento aparece primero |
| `.ion-order-0` | `order: 0` | Elemento aparece en su orden natural |
| `.ion-order-1` a `.ion-order-12` | `order: 1-12` | Elemento aparece después de elementos con orden menor |
| `.ion-order-last` | `order: 13` | Elemento aparece último |

**Ejemplo:**

```html
<div class="ion-display-flex">
  <div class="ion-order-3">Tercero (aparece primero en HTML)</div>
  <div class="ion-order-1">Primero</div>
  <div class="ion-order-2">Segundo</div>
</div>
```

### Clases Responsivas de Elementos Flex

Todas las propiedades de elementos flex tienen versiones responsivas usando `.ion-{property}-{breakpoint}-{modifier}`.

---

## Bordes

### Sin Borde

La clase `.ion-no-border` se puede usar para remover bordes de componentes Ionic. Se puede aplicar a `ion-header` e `ion-footer`.

```html
<ion-header class="ion-no-border">
  <ion-toolbar>
    <ion-title>Header sin borde</ion-title>
  </ion-toolbar>
</ion-header>

<ion-footer class="ion-no-border">
  <ion-toolbar>
    <ion-title>Footer sin borde</ion-title>
  </ion-toolbar>
</ion-footer>
```

---

## Modo Oscuro (Dark Mode)

Ionic facilita el cambio de paletas en tu app, incluyendo soporte para esquemas de colores oscuros. El modo oscuro tiene soporte en todo el sistema en iOS y Android.

### Habilitando la Paleta Oscura

Hay tres formas de habilitar la paleta oscura en Ionic:

#### 1. Siempre (Always)

Muestra siempre el modo oscuro, independientemente de la configuración del sistema.

**En `src/styles.css` (Angular) o `src/global.scss`:**

```css
@import '@ionic/angular/css/palettes/dark.always.css';
```

#### 2. Según Sistema (System)

Automáticamente detecta la preferencia del sistema del usuario.

```css
@import '@ionic/angular/css/palettes/dark.system.css';
```

Esto usa la media query `prefers-color-scheme` para detectar la preferencia del usuario.

#### 3. Con Clase CSS (Class)

Permite controlar el modo oscuro mediante una clase CSS, ideal para implementar un toggle.

```css
@import '@ionic/angular/css/palettes/dark.class.css';
```

**Ejemplo de implementación con toggle:**

```typescript
// ejemplo.component.ts
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-ejemplo',
  templateUrl: './ejemplo.component.html'
})
export class EjemploComponent implements OnInit {
  paletteToggle = false;

  ngOnInit() {
    // Verifica la preferencia del usuario
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Inicializa la paleta oscura basándose en la preferencia
    this.initializeDarkPalette(prefersDark.matches);
    
    // Escucha cambios en la preferencia del sistema
    prefersDark.addEventListener('change', (mediaQuery) => 
      this.initializeDarkPalette(mediaQuery.matches)
    );
  }

  initializeDarkPalette(isDark: boolean) {
    this.paletteToggle = isDark;
    this.toggleDarkPalette(isDark);
  }

  toggleChange(event: CustomEvent) {
    this.toggleDarkPalette(event.detail.checked);
  }

  toggleDarkPalette(shouldAdd: boolean) {
    document.documentElement.classList.toggle('ion-palette-dark', shouldAdd);
  }
}
```

```html
<!-- ejemplo.component.html -->
<ion-content>
  <ion-list>
    <ion-item>
      <ion-toggle 
        [(ngModel)]="paletteToggle" 
        (ionChange)="toggleChange($event)"
        justify="space-between">
        Modo Oscuro
      </ion-toggle>
    </ion-item>
  </ion-list>
</ion-content>
```

### Ajustando Componentes de UI del Sistema

Para asegurar que los componentes del sistema (como scrollbars) también respeten el modo oscuro:

**En el `<head>` de tu `index.html`:**

```html
<meta name="color-scheme" content="light dark" />
```

**O en tu CSS:**

```css
:root {
  color-scheme: light dark;
}
```

Esto afecta elementos como:
- Scrollbars
- Formularios nativos
- Otros controles del sistema

### Variables de la Paleta Oscura de Ionic

Ionic proporciona variables CSS predefinidas para el modo oscuro que puedes personalizar:

```css
/* En tu archivo variables.css o theme/variables.scss */

/* Personalización para modo oscuro en iOS */
:root.ios.ion-palette-dark {
  --ion-background-color: #000000;
  --ion-toolbar-background: #0d0d0d;
  --ion-item-background: #1c1c1d;
  --ion-text-color: #ffffff;
}

/* Personalización para modo oscuro en Material Design */
:root.md.ion-palette-dark {
  --ion-background-color: #121212;
  --ion-toolbar-background: #1e1e1e;
  --ion-item-background: #1c1c1d;
  --ion-text-color: #ffffff;
}
```

### ⚠️ Importante sobre Especificidad

Evita apuntar a los selectores `.ios` o `.md` directamente para sobrescribir la paleta oscura de Ionic, ya que estas clases se agregan a cada componente y tendrán prioridad sobre las variables definidas globalmente. En su lugar, apunta a las clases específicas de modo en el elemento `:root`:

```css
/* ❌ Incorrecto - baja especificidad */
.ios {
  --ion-item-background: #custom-color;
}

/* ✅ Correcto - alta especificidad */
:root.ios {
  --ion-item-background: #custom-color;
}
```

### Prevenir Parpadeo al Cambiar Paletas

Para evitar el efecto de parpadeo al cambiar entre paletas:

```css
/* En tu archivo global.css o styles.css */
ion-item {
  --transition: none;
}
```

---

## Breakpoints de Ionic

Ionic usa breakpoints en media queries para aplicar estilos según el tamaño de pantalla:

| Nombre | Ancho Mínimo | Uso Típico |
|--------|-------------|-----------|
| `xs` | 0px | Teléfonos móviles pequeños |
| `sm` | 576px | Teléfonos móviles grandes |
| `md` | 768px | Tablets |
| `lg` | 992px | Laptops/Desktops pequeños |
| `xl` | 1200px | Desktops grandes |

**Ejemplos de uso:**

```html
<!-- Ocultar en móviles, mostrar en tablets -->
<div class="ion-display-none ion-display-md-block">
  Visible solo en tablets y superiores
</div>

<!-- Columna en móvil, fila en desktop -->
<div class="ion-display-flex ion-flex-column ion-flex-lg-row">
  <div>Elemento 1</div>
  <div>Elemento 2</div>
</div>

<!-- Texto centrado en móvil, alineado al inicio en desktop -->
<div class="ion-text-center ion-text-lg-start">
  <h2>Título Responsivo</h2>
</div>
```

---

## Mejores Prácticas

### 1. Usa las Clases de Ionic en Lugar de CSS Personalizado

❌ **Evitar:**

```css
/* styles.css */
.my-custom-class {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}
```

✅ **Preferir:**

```html
<div class="ion-display-flex ion-justify-content-center ion-align-items-center ion-padding">
  <!-- Contenido -->
</div>
```

### 2. Combina Clases para Layouts Complejos

```html
<!-- Card con sombra, padding y centrado -->
<ion-card class="ion-padding ion-text-center">
  <ion-card-header>
    <ion-card-title class="ion-text-uppercase">Título</ion-card-title>
  </ion-card-header>
  <ion-card-content>
    Contenido del card
  </ion-card-content>
</ion-card>
```

### 3. Usa Clases Responsivas para Mobile-First

```html
<!-- Mobile-first: stack vertical en móvil, horizontal en tablet -->
<div class="ion-display-flex ion-flex-column ion-flex-md-row ion-justify-content-md-between">
  <ion-button expand="block" class="ion-margin-bottom ion-margin-md-0">
    Botón 1
  </ion-button>
  <ion-button expand="block">
    Botón 2
  </ion-button>
</div>
```

### 4. Aprovecha las Utilidades de Espaciado

```html
<!-- Lista con espaciado consistente -->
<ion-list>
  <ion-item class="ion-padding-vertical">
    <ion-label>Item con padding vertical</ion-label>
  </ion-item>
  <ion-item class="ion-margin-top">
    <ion-label>Item con margin top</ion-label>
  </ion-item>
</ion-list>
```

### 5. Implementa Dark Mode desde el Inicio

```typescript
// app.component.ts
export class AppComponent implements OnInit {
  ngOnInit() {
    // Detectar preferencia del sistema
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    document.documentElement.classList.toggle('ion-palette-dark', prefersDark.matches);
    
    // Escuchar cambios
    prefersDark.addEventListener('change', (e) => {
      document.documentElement.classList.toggle('ion-palette-dark', e.matches);
    });
  }
}
```

### 6. Usa Variables CSS para Valores Personalizados

Si necesitas valores diferentes a los predeterminados (16px), usa variables CSS:

```css
/* En tu archivo variables.css */
:root {
  --ion-padding: 20px;
  --ion-margin: 20px;
}

/* Para pantallas pequeñas */
@media (max-width: 576px) {
  :root {
    --ion-padding: 12px;
    --ion-margin: 12px;
  }
}
```

### 7. Evita Clases Deprecadas

Actualiza tu código para usar las nuevas clases:

```html
<!-- ❌ Deprecado -->
<div class="ion-hide-md-down">Contenido</div>

<!-- ✅ Actualizado -->
<div class="ion-display-none ion-display-lg-block">Contenido</div>
```

### 8. Mantén la Consistencia

Establece convenciones en tu equipo:

```html
<!-- Ejemplo de patrón consistente para cards -->
<ion-card class="ion-margin ion-padding">
  <ion-card-header class="ion-no-padding">
    <ion-card-title class="ion-text-capitalize">
      <!-- Título -->
    </ion-card-title>
  </ion-card-header>
  <ion-card-content class="ion-no-padding ion-margin-top">
    <!-- Contenido -->
  </ion-card-content>
</ion-card>
```

---

## Recursos Adicionales

- 📖 [Documentación Oficial de CSS Utilities](https://ionicframework.com/docs/layout/css-utilities)
- 🌙 [Documentación de Dark Mode](https://ionicframework.com/docs/theming/dark-mode)
- 🎨 [Tematización de Ionic](https://ionicframework.com/docs/theming/basics)
- 📱 [Estilos de Plataforma](https://ionicframework.com/docs/theming/platform-styles)
- 🔧 [Variables CSS](https://ionicframework.com/docs/theming/css-variables)

---

## Conclusión

Las utilidades CSS de Ionic proporcionan una manera poderosa y consistente de estilizar aplicaciones sin necesidad de escribir CSS personalizado. Al usar estas clases:

✅ Reduces la cantidad de CSS personalizado  
✅ Mejoras la consistencia visual  
✅ Facilitas el mantenimiento del código  
✅ Aprovechas el diseño responsivo integrado  
✅ Soportas dark mode de manera nativa  

**Recuerda**: Siempre prefiere las clases utilitarias de Ionic sobre CSS personalizado cuando sea posible. Tu código será más limpio, mantenible y consistente.

---

*Documento creado el 15 de enero de 2026 por GitHub Copilot para el proyecto ezekl-budget*
