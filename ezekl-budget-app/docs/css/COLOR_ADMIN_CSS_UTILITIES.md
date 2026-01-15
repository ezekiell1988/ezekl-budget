# Guía Completa: Utilidades CSS de Color Admin Template

> **Última actualización**: 15 de enero de 2026  
> **Template**: Color Admin Angular 20  
> **Proyecto**: ezekl-budget

## 📋 Tabla de Contenidos

- [Introducción](#introducción)
- [Clases Generales](#clases-generales)
- [Width y Height](#width-y-height)
- [Texto y Fuentes](#texto-y-fuentes)
- [Margin](#margin)
- [Padding](#padding)
- [Colores de Fondo](#colores-de-fondo)
- [Colores de Texto](#colores-de-texto)
- [Guía de Migración](#guía-de-migración)
- [Mejores Prácticas](#mejores-prácticas)

---

## Introducción

El template Color Admin proporciona un conjunto completo de clases CSS predefinidas que pueden ser utilizadas en cualquier elemento para modificar el estilo, posicionamiento, espaciado y colores sin necesidad de escribir CSS personalizado.

### ⚠️ Importante

Todas las clases CSS predefinidas sobrescribirán el estilo CSS definido en tus clases, **A MENOS QUE** se declare `!important` en tu estilo CSS personalizado.

---

## Clases Generales

### Row Space

Clases para controlar el espaciado entre filas.

| Clase | Descripción |
|-------|-------------|
| `.row-space-0` | Sin espacio entre filas |
| `.row-space-2` | Espacio de 2px entre filas |
| `.row-space-4` | Espacio de 4px entre filas |
| `.row-space-6` | Espacio de 6px entre filas |
| `.row-space-8` | Espacio de 8px entre filas |
| `.row-space-10` | Espacio de 10px entre filas |
| `.row-space-12` | Espacio de 12px entre filas |
| `.row-space-14` | Espacio de 14px entre filas |
| `.row-space-16` | Espacio de 16px entre filas |

**Ejemplo:**
```html
<div class="row row-space-10">
  <div class="col-md-6">Columna 1</div>
  <div class="col-md-6">Columna 2</div>
</div>
```

### Table

Clases para tablas.

| Clase | Descripción |
|-------|-------------|
| `.table-valign-middle` | Alineación vertical al centro |
| `.table-hover-bg-gray-200` | Fondo gris 200 al hacer hover |
| `.table-hover-bg-gray-300` | Fondo gris 300 al hacer hover |
| `.table-hover-bg-gray-500` | Fondo gris 500 al hacer hover |
| `.table-hover-bg-gray-600` | Fondo gris 600 al hacer hover |
| `.table-hover-bg-gray-700` | Fondo gris 700 al hacer hover |
| `.table-hover-bg-gray-800` | Fondo gris 800 al hacer hover |
| `.table-hover-bg-gray-900` | Fondo gris 900 al hacer hover |
| `.table-hover-bg-dark` | Fondo oscuro al hacer hover |
| `.table-td-valign-middle` | Alineación vertical al centro en celdas |
| `.table-th-valign-middle` | Alineación vertical al centro en encabezados |
| `.table-borderless` | Tabla sin bordes |
| `.table-border-0` | Sin borde |
| `.table-striped-columns` | Columnas rayadas |

**Ejemplo:**
```html
<table class="table table-hover table-valign-middle table-hover-bg-gray-200">
  <thead>
    <tr>
      <th>Nombre</th>
      <th>Email</th>
      <th>Acción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Juan Pérez</td>
      <td>juan@example.com</td>
      <td><button class="btn btn-sm btn-primary">Editar</button></td>
    </tr>
  </tbody>
</table>
```

### Float

Clases para el posicionamiento flotante.

| Clase | Descripción |
|-------|-------------|
| `.float-start` | Flota a la izquierda (inicio) |
| `.float-end` | Flota a la derecha (final) |
| `.float-none` | Sin flotamiento |
| `.float-left` | Flota a la izquierda |
| `.float-right` | Flota a la derecha |

### Border Radius

Clases para controlar los bordes redondeados.

| Clase | Descripción |
|-------|-------------|
| `.rounded` | Bordes redondeados estándar |
| `.rounded-0` | Sin bordes redondeados |
| `.rounded-1` | Bordes redondeados nivel 1 |
| `.rounded-2` | Bordes redondeados nivel 2 |
| `.rounded-3` | Bordes redondeados nivel 3 |
| `.rounded-4` | Bordes redondeados nivel 4 |
| `.rounded-5` | Bordes redondeados nivel 5 |
| `.rounded-top` | Solo esquinas superiores redondeadas |
| `.rounded-end` | Solo esquinas del final redondeadas |
| `.rounded-bottom` | Solo esquinas inferiores redondeadas |
| `.rounded-start` | Solo esquinas del inicio redondeadas |
| `.rounded-circle` | Bordes completamente circulares |
| `.rounded-pill` | Bordes en forma de píldora |

**Ejemplo:**
```html
<div class="card rounded-3">
  <div class="card-body">
    Contenido con bordes redondeados nivel 3
  </div>
</div>

<img src="avatar.jpg" class="rounded-circle" width="50" height="50" alt="Avatar">
```

### Display

Clases para controlar la visualización.

| Clase | Descripción |
|-------|-------------|
| `.d-none` | Ocultar elemento |
| `.d-inline` | Display inline |
| `.d-inline-block` | Display inline-block |
| `.d-block` | Display block |
| `.d-grid` | Display grid |
| `.d-table` | Display table |
| `.d-table-row` | Display table-row |
| `.d-table-cell` | Display table-cell |
| `.d-flex` | Display flex |
| `.d-inline-flex` | Display inline-flex |
| `.d-sm-*` | Display para pantallas small y superiores |
| `.d-md-*` | Display para pantallas medium y superiores |
| `.d-lg-*` | Display para pantallas large y superiores |
| `.d-xl-*` | Display para pantallas extra large y superiores |

**Ejemplo:**
```html
<!-- Ocultar en móvil, mostrar en desktop -->
<div class="d-none d-lg-block">
  Visible solo en pantallas grandes
</div>

<!-- Flex container -->
<div class="d-flex justify-content-between align-items-center">
  <span>Inicio</span>
  <span>Fin</span>
</div>
```

### Overflow

Clases para controlar el overflow.

| Clase | Descripción |
|-------|-------------|
| `.overflow-auto` | Overflow automático |
| `.overflow-hidden` | Overflow oculto |
| `.overflow-visible` | Overflow visible |
| `.overflow-scroll` | Overflow con scroll |
| `.overflow-x-auto` | Overflow horizontal automático |
| `.overflow-y-auto` | Overflow vertical automático |
| `.overflow-x-hidden` | Overflow horizontal oculto |
| `.overflow-y-hidden` | Overflow vertical oculto |

### Flex

Clases para flexbox.

| Clase | Descripción |
|-------|-------------|
| `.d-flex` | Activa flexbox |
| `.d-inline-flex` | Flexbox inline |
| `.flex-row` | Dirección en fila |
| `.flex-row-reverse` | Dirección en fila invertida |
| `.flex-column` | Dirección en columna |
| `.flex-column-reverse` | Dirección en columna invertida |
| `.flex-wrap` | Permite envolver elementos |
| `.flex-nowrap` | Sin envolver elementos |
| `.flex-wrap-reverse` | Envolver en reversa |
| `.flex-fill` | Llenar espacio disponible |
| `.flex-grow-0` | No crecer |
| `.flex-grow-1` | Crecer proporcionalmente |
| `.flex-shrink-0` | No encoger |
| `.flex-shrink-1` | Encoger proporcionalmente |
| `.justify-content-start` | Justificar al inicio |
| `.justify-content-end` | Justificar al final |
| `.justify-content-center` | Justificar al centro |
| `.justify-content-between` | Espacio entre elementos |
| `.justify-content-around` | Espacio alrededor de elementos |
| `.justify-content-evenly` | Espacio uniforme |
| `.align-items-start` | Alinear al inicio |
| `.align-items-end` | Alinear al final |
| `.align-items-center` | Alinear al centro |
| `.align-items-baseline` | Alinear a la línea base |
| `.align-items-stretch` | Estirar elementos |
| `.align-content-start` | Alinear contenido al inicio |
| `.align-content-end` | Alinear contenido al final |
| `.align-content-center` | Alinear contenido al centro |
| `.align-content-between` | Espacio entre contenido |
| `.align-content-around` | Espacio alrededor del contenido |
| `.align-content-stretch` | Estirar contenido |
| `.align-self-auto` | Alineación automática |
| `.align-self-start` | Auto-alinear al inicio |
| `.align-self-end` | Auto-alinear al final |
| `.align-self-center` | Auto-alinear al centro |
| `.align-self-baseline` | Auto-alinear a línea base |
| `.align-self-stretch` | Auto-estirar |

**Ejemplo:**
```html
<div class="d-flex justify-content-between align-items-center">
  <button class="btn btn-primary">Izquierda</button>
  <button class="btn btn-secondary">Centro</button>
  <button class="btn btn-success">Derecha</button>
</div>

<div class="d-flex flex-column flex-lg-row">
  <div class="flex-fill">Columna 1</div>
  <div class="flex-fill">Columna 2</div>
  <div class="flex-fill">Columna 3</div>
</div>
```

### Borders

Clases para bordes.

| Clase | Descripción |
|-------|-------------|
| `.border` | Borde en todos los lados |
| `.border-0` | Sin borde |
| `.border-top` | Borde superior |
| `.border-top-0` | Sin borde superior |
| `.border-end` | Borde derecho |
| `.border-end-0` | Sin borde derecho |
| `.border-bottom` | Borde inferior |
| `.border-bottom-0` | Sin borde inferior |
| `.border-start` | Borde izquierdo |
| `.border-start-0` | Sin borde izquierdo |
| `.border-primary` | Borde color primario |
| `.border-secondary` | Borde color secundario |
| `.border-success` | Borde color éxito |
| `.border-danger` | Borde color peligro |
| `.border-warning` | Borde color advertencia |
| `.border-info` | Borde color información |
| `.border-light` | Borde color claro |
| `.border-dark` | Borde color oscuro |
| `.border-white` | Borde color blanco |
| `.border-1` | Grosor de borde 1px |
| `.border-2` | Grosor de borde 2px |
| `.border-3` | Grosor de borde 3px |
| `.border-4` | Grosor de borde 4px |
| `.border-5` | Grosor de borde 5px |

**Ejemplo:**
```html
<div class="card border border-primary border-3 rounded-3">
  <div class="card-body">
    Card con borde primario de 3px
  </div>
</div>
```

### Position

Clases para posicionamiento.

| Clase | Descripción |
|-------|-------------|
| `.position-static` | Posición estática |
| `.position-relative` | Posición relativa |
| `.position-absolute` | Posición absoluta |
| `.position-fixed` | Posición fija |
| `.position-sticky` | Posición pegajosa |
| `.top-0` | Top: 0 |
| `.top-50` | Top: 50% |
| `.top-100` | Top: 100% |
| `.bottom-0` | Bottom: 0 |
| `.bottom-50` | Bottom: 50% |
| `.bottom-100` | Bottom: 100% |
| `.start-0` | Start (left): 0 |
| `.start-50` | Start: 50% |
| `.start-100` | Start: 100% |
| `.end-0` | End (right): 0 |
| `.end-50` | End: 50% |
| `.end-100` | End: 100% |
| `.translate-middle` | Centrar con transform |
| `.translate-middle-x` | Centrar horizontalmente |
| `.translate-middle-y` | Centrar verticalmente |

**Ejemplo:**
```html
<div class="position-relative" style="height: 200px;">
  <div class="position-absolute top-0 start-0">
    Esquina superior izquierda
  </div>
  <div class="position-absolute top-50 start-50 translate-middle">
    Centro absoluto
  </div>
  <div class="position-absolute bottom-0 end-0">
    Esquina inferior derecha
  </div>
</div>
```

### Interactions

Clases para interacciones de usuario.

| Clase | Descripción |
|-------|-------------|
| `.user-select-all` | Seleccionar todo el texto |
| `.user-select-auto` | Selección automática |
| `.user-select-none` | No permitir selección |
| `.pe-none` | Sin eventos de puntero |
| `.pe-auto` | Eventos de puntero automáticos |
| `.cursor-pointer` | Cursor de puntero |
| `.cursor-default` | Cursor predeterminado |

**Ejemplo:**
```html
<div class="user-select-none">
  Este texto no se puede seleccionar
</div>

<div class="cursor-pointer" onclick="alert('Clicked!')">
  Haz clic aquí
</div>
```

### Shadows

Clases para sombras.

| Clase | Descripción |
|-------|-------------|
| `.shadow-none` | Sin sombra |
| `.shadow-sm` | Sombra pequeña |
| `.shadow` | Sombra estándar |
| `.shadow-lg` | Sombra grande |
| `.shadow-xl` | Sombra extra grande |
| `.shadow-xxl` | Sombra doble extra grande |

**Ejemplo:**
```html
<div class="card shadow-lg">
  <div class="card-body">
    Card con sombra grande
  </div>
</div>
```

### Visibility

Clases para visibilidad.

| Clase | Descripción |
|-------|-------------|
| `.visible` | Elemento visible |
| `.invisible` | Elemento invisible (ocupa espacio) |
| `.opacity-0` | Opacidad 0% |
| `.opacity-25` | Opacidad 25% |
| `.opacity-50` | Opacidad 50% |
| `.opacity-75` | Opacidad 75% |
| `.opacity-100` | Opacidad 100% |

---

## Width y Height

### Width (Ancho)

#### Porcentajes

| Clase | Valor |
|-------|-------|
| `.w-0` | width: 0% |
| `.w-25` | width: 25% |
| `.w-50` | width: 50% |
| `.w-75` | width: 75% |
| `.w-100` | width: 100% |
| `.w-auto` | width: auto |

#### Píxeles

| Clase | Valor |
|-------|-------|
| `.w-50px` | width: 50px |
| `.w-100px` | width: 100px |
| `.w-150px` | width: 150px |
| `.w-200px` | width: 200px |
| `.w-250px` | width: 250px |
| `.w-300px` | width: 300px |
| `.w-350px` | width: 350px |
| `.w-400px` | width: 400px |
| `.w-450px` | width: 450px |
| `.w-500px` | width: 500px |

#### Viewport Width

| Clase | Valor |
|-------|-------|
| `.vw-10` | width: 10vw |
| `.vw-20` | width: 20vw |
| `.vw-25` | width: 25vw |
| `.vw-30` | width: 30vw |
| `.vw-40` | width: 40vw |
| `.vw-50` | width: 50vw |
| `.vw-60` | width: 60vw |
| `.vw-70` | width: 70vw |
| `.vw-75` | width: 75vw |
| `.vw-80` | width: 80vw |
| `.vw-90` | width: 90vw |
| `.vw-100` | width: 100vw |

### Height (Alto)

#### Porcentajes

| Clase | Valor |
|-------|-------|
| `.h-0` | height: 0% |
| `.h-25` | height: 25% |
| `.h-50` | height: 50% |
| `.h-75` | height: 75% |
| `.h-100` | height: 100% |
| `.h-auto` | height: auto |

#### Píxeles

| Clase | Valor |
|-------|-------|
| `.h-50px` | height: 50px |
| `.h-100px` | height: 100px |
| `.h-150px` | height: 150px |
| `.h-200px` | height: 200px |
| `.h-250px` | height: 250px |
| `.h-300px` | height: 300px |
| `.h-350px` | height: 350px |
| `.h-400px` | height: 400px |
| `.h-450px` | height: 450px |
| `.h-500px` | height: 500px |

#### Viewport Height

| Clase | Valor |
|-------|-------|
| `.vh-10` | height: 10vh |
| `.vh-20` | height: 20vh |
| `.vh-25` | height: 25vh |
| `.vh-30` | height: 30vh |
| `.vh-40` | height: 40vh |
| `.vh-50` | height: 50vh |
| `.vh-60` | height: 60vh |
| `.vh-70` | height: 70vh |
| `.vh-75` | height: 75vh |
| `.vh-80` | height: 80vh |
| `.vh-90` | height: 90vh |
| `.vh-100` | height: 100vh |

**Ejemplo:**
```html
<!-- Card de ancho fijo -->
<div class="card w-300px">
  <div class="card-body">
    Card de 300px de ancho
  </div>
</div>

<!-- Sección a pantalla completa -->
<section class="vh-100 d-flex align-items-center justify-content-center">
  <h1>Contenido centrado en toda la pantalla</h1>
</section>

<!-- Ancho responsivo -->
<div class="w-100 w-lg-50">
  100% en móvil, 50% en desktop
</div>
```

---

## Texto y Fuentes

### Font Size

| Clase | Valor |
|-------|-------|
| `.fs-8px` | font-size: 8px |
| `.fs-10px` | font-size: 10px |
| `.fs-12px` | font-size: 12px |
| `.fs-14px` | font-size: 14px |
| `.fs-16px` | font-size: 16px |
| `.fs-18px` | font-size: 18px |
| `.fs-20px` | font-size: 20px |
| `.fs-24px` | font-size: 24px |
| `.fs-30px` | font-size: 30px |
| `.fs-36px` | font-size: 36px |

### Font Weight

| Clase | Valor |
|-------|-------|
| `.fw-100` | font-weight: 100 (Thin) |
| `.fw-200` | font-weight: 200 (Extra Light) |
| `.fw-300` | font-weight: 300 (Light) |
| `.fw-400` | font-weight: 400 (Normal) |
| `.fw-500` | font-weight: 500 (Medium) |
| `.fw-600` | font-weight: 600 (Semi Bold) |
| `.fw-700` | font-weight: 700 (Bold) |
| `.fw-800` | font-weight: 800 (Extra Bold) |
| `.fw-900` | font-weight: 900 (Black) |
| `.fw-bold` | font-weight: bold |
| `.fw-normal` | font-weight: normal |

### Text Align

| Clase | Valor |
|-------|-------|
| `.text-start` | text-align: left |
| `.text-end` | text-align: right |
| `.text-center` | text-align: center |
| `.text-justify` | text-align: justify |

### Text Overflow

| Clase | Descripción |
|-------|-------------|
| `.text-truncate` | Trunca el texto con ellipsis |
| `.text-wrap` | Permite envolver el texto |
| `.text-nowrap` | No permite envolver el texto |
| `.text-break` | Rompe palabras largas |

### Line Height

| Clase | Valor |
|-------|-------|
| `.lh-1` | line-height: 1 |
| `.lh-sm` | line-height: 1.25 |
| `.lh-base` | line-height: 1.5 |
| `.lh-lg` | line-height: 2 |

### Italics

| Clase | Descripción |
|-------|-------------|
| `.fst-italic` | Texto en cursiva |
| `.fst-normal` | Texto normal (no cursiva) |

### Text Decoration

| Clase | Descripción |
|-------|-------------|
| `.text-decoration-none` | Sin decoración |
| `.text-decoration-underline` | Texto subrayado |
| `.text-decoration-line-through` | Texto tachado |

### Reset Color

| Clase | Descripción |
|-------|-------------|
| `.text-reset` | Resetea el color heredado |
| `.text-body` | Color de texto del body |
| `.text-muted` | Texto atenuado (gris) |

### Text Transform

| Clase | Valor |
|-------|-------|
| `.text-lowercase` | Texto en minúsculas |
| `.text-uppercase` | Texto en MAYÚSCULAS |
| `.text-capitalize` | Primera Letra En Mayúscula |

### Word Break

| Clase | Descripción |
|-------|-------------|
| `.text-break` | Permite romper palabras largas |

### Monospace

| Clase | Descripción |
|-------|-------------|
| `.font-monospace` | Fuente monoespaciada |

**Ejemplo:**
```html
<h1 class="fs-36px fw-700 text-center text-uppercase">
  Título Principal
</h1>

<p class="fs-14px fw-400 text-justify lh-lg">
  Párrafo con tamaño de fuente 14px, peso normal, justificado y altura de línea grande.
</p>

<div class="w-200px">
  <p class="text-truncate">
    Este es un texto muy largo que será truncado con puntos suspensivos
  </p>
</div>

<span class="fs-12px fw-600 text-uppercase text-muted">
  Etiqueta pequeña
</span>
```

---

## Margin

Todas las clases de margin siguen el patrón: `.m{lado}-{tamaño}`

### Margin en Todos los Lados

| Clase | Valor |
|-------|-------|
| `.m-0` | margin: 0 |
| `.m-1` | margin: 0.25rem (4px) |
| `.m-2` | margin: 0.5rem (8px) |
| `.m-3` | margin: 1rem (16px) |
| `.m-4` | margin: 1.5rem (24px) |
| `.m-5` | margin: 3rem (48px) |
| `.m-auto` | margin: auto |

### Margin Top

| Clase | Valor |
|-------|-------|
| `.mt-0` | margin-top: 0 |
| `.mt-1` | margin-top: 0.25rem |
| `.mt-2` | margin-top: 0.5rem |
| `.mt-3` | margin-top: 1rem |
| `.mt-4` | margin-top: 1.5rem |
| `.mt-5` | margin-top: 3rem |
| `.mt-auto` | margin-top: auto |
| `.mt-n1` | margin-top: -0.25rem |
| `.mt-n2` | margin-top: -0.5rem |
| `.mt-n3` | margin-top: -1rem |
| `.mt-n4` | margin-top: -1.5rem |
| `.mt-n5` | margin-top: -3rem |

### Margin Right

| Clase | Valor |
|-------|-------|
| `.me-0` | margin-right: 0 |
| `.me-1` | margin-right: 0.25rem |
| `.me-2` | margin-right: 0.5rem |
| `.me-3` | margin-right: 1rem |
| `.me-4` | margin-right: 1.5rem |
| `.me-5` | margin-right: 3rem |
| `.me-auto` | margin-right: auto |
| `.me-n1` | margin-right: -0.25rem |
| `.me-n2` | margin-right: -0.5rem |
| `.me-n3` | margin-right: -1rem |
| `.me-n4` | margin-right: -1.5rem |
| `.me-n5` | margin-right: -3rem |

### Margin Bottom

| Clase | Valor |
|-------|-------|
| `.mb-0` | margin-bottom: 0 |
| `.mb-1` | margin-bottom: 0.25rem |
| `.mb-2` | margin-bottom: 0.5rem |
| `.mb-3` | margin-bottom: 1rem |
| `.mb-4` | margin-bottom: 1.5rem |
| `.mb-5` | margin-bottom: 3rem |
| `.mb-auto` | margin-bottom: auto |
| `.mb-n1` | margin-bottom: -0.25rem |
| `.mb-n2` | margin-bottom: -0.5rem |
| `.mb-n3` | margin-bottom: -1rem |
| `.mb-n4` | margin-bottom: -1.5rem |
| `.mb-n5` | margin-bottom: -3rem |

### Margin Left

| Clase | Valor |
|-------|-------|
| `.ms-0` | margin-left: 0 |
| `.ms-1` | margin-left: 0.25rem |
| `.ms-2` | margin-left: 0.5rem |
| `.ms-3` | margin-left: 1rem |
| `.ms-4` | margin-left: 1.5rem |
| `.ms-5` | margin-left: 3rem |
| `.ms-auto` | margin-left: auto |
| `.ms-n1` | margin-left: -0.25rem |
| `.ms-n2` | margin-left: -0.5rem |
| `.ms-n3` | margin-left: -1rem |
| `.ms-n4` | margin-left: -1.5rem |
| `.ms-n5` | margin-left: -3rem |

### Margin Horizontal y Vertical

| Clase | Descripción |
|-------|-------------|
| `.mx-0` a `.mx-5` | Margin horizontal (left + right) |
| `.mx-auto` | Margin horizontal automático (centra el elemento) |
| `.my-0` a `.my-5` | Margin vertical (top + bottom) |
| `.my-auto` | Margin vertical automático |

**Ejemplo:**
```html
<!-- Espaciado entre elementos -->
<div class="mb-3">
  <label>Campo 1</label>
  <input type="text" class="form-control">
</div>
<div class="mb-3">
  <label>Campo 2</label>
  <input type="text" class="form-control">
</div>

<!-- Centrar un elemento -->
<div class="w-300px mx-auto">
  Elemento centrado horizontalmente
</div>

<!-- Separación entre botones -->
<button class="btn btn-primary me-2">Guardar</button>
<button class="btn btn-secondary">Cancelar</button>
```

---

## Padding

Todas las clases de padding siguen el patrón: `.p{lado}-{tamaño}`

### Padding en Todos los Lados

| Clase | Valor |
|-------|-------|
| `.p-0` | padding: 0 |
| `.p-1` | padding: 0.25rem (4px) |
| `.p-2` | padding: 0.5rem (8px) |
| `.p-3` | padding: 1rem (16px) |
| `.p-4` | padding: 1.5rem (24px) |
| `.p-5` | padding: 3rem (48px) |

### Padding Top

| Clase | Valor |
|-------|-------|
| `.pt-0` | padding-top: 0 |
| `.pt-1` | padding-top: 0.25rem |
| `.pt-2` | padding-top: 0.5rem |
| `.pt-3` | padding-top: 1rem |
| `.pt-4` | padding-top: 1.5rem |
| `.pt-5` | padding-top: 3rem |

### Padding Right

| Clase | Valor |
|-------|-------|
| `.pe-0` | padding-right: 0 |
| `.pe-1` | padding-right: 0.25rem |
| `.pe-2` | padding-right: 0.5rem |
| `.pe-3` | padding-right: 1rem |
| `.pe-4` | padding-right: 1.5rem |
| `.pe-5` | padding-right: 3rem |

### Padding Bottom

| Clase | Valor |
|-------|-------|
| `.pb-0` | padding-bottom: 0 |
| `.pb-1` | padding-bottom: 0.25rem |
| `.pb-2` | padding-bottom: 0.5rem |
| `.pb-3` | padding-bottom: 1rem |
| `.pb-4` | padding-bottom: 1.5rem |
| `.pb-5` | padding-bottom: 3rem |

### Padding Left

| Clase | Valor |
|-------|-------|
| `.ps-0` | padding-left: 0 |
| `.ps-1` | padding-left: 0.25rem |
| `.ps-2` | padding-left: 0.5rem |
| `.ps-3` | padding-left: 1rem |
| `.ps-4` | padding-left: 1.5rem |
| `.ps-5` | padding-left: 3rem |

### Padding Horizontal y Vertical

| Clase | Descripción |
|-------|-------------|
| `.px-0` a `.px-5` | Padding horizontal (left + right) |
| `.py-0` a `.py-5` | Padding vertical (top + bottom) |

**Ejemplo:**
```html
<!-- Card con padding personalizado -->
<div class="card">
  <div class="card-body p-4">
    Contenido con padding de 24px
  </div>
</div>

<!-- Lista sin padding -->
<ul class="list-group">
  <li class="list-group-item py-3 px-4">
    Item con padding vertical 16px y horizontal 24px
  </li>
</ul>

<!-- Botón con padding extra -->
<button class="btn btn-primary px-5 py-3">
  Botón Grande
</button>
```

---

## Colores de Fondo

### Paleta Principal

#### Blue (Azul)

| Clase | Descripción |
|-------|-------------|
| `.bg-blue` | Fondo azul base |
| `.bg-blue-100` | Azul muy claro |
| `.bg-blue-200` | Azul claro |
| `.bg-blue-300` | Azul claro medio |
| `.bg-blue-400` | Azul medio claro |
| `.bg-blue-500` | Azul medio |
| `.bg-blue-600` | Azul medio oscuro |
| `.bg-blue-700` | Azul oscuro medio |
| `.bg-blue-800` | Azul oscuro |
| `.bg-blue-900` | Azul muy oscuro |

#### Indigo

| Clase | Descripción |
|-------|-------------|
| `.bg-indigo` | Fondo índigo base |
| `.bg-indigo-100` a `.bg-indigo-900` | Variaciones de índigo |

#### Purple (Morado)

| Clase | Descripción |
|-------|-------------|
| `.bg-purple` | Fondo morado base |
| `.bg-purple-100` a `.bg-purple-900` | Variaciones de morado |

#### Aqua (Agua)

| Clase | Descripción |
|-------|-------------|
| `.bg-aqua` | Fondo aqua base |
| `.bg-aqua-100` a `.bg-aqua-900` | Variaciones de aqua |

#### Teal (Verde azulado)

| Clase | Descripción |
|-------|-------------|
| `.bg-teal` | Fondo teal base |
| `.bg-teal-100` a `.bg-teal-900` | Variaciones de teal |

#### Green (Verde)

| Clase | Descripción |
|-------|-------------|
| `.bg-green` | Fondo verde base |
| `.bg-green-100` a `.bg-green-900` | Variaciones de verde |

#### Lime (Lima)

| Clase | Descripción |
|-------|-------------|
| `.bg-lime` | Fondo lima base |
| `.bg-lime-100` a `.bg-lime-900` | Variaciones de lima |

#### Orange (Naranja)

| Clase | Descripción |
|-------|-------------|
| `.bg-orange` | Fondo naranja base |
| `.bg-orange-100` a `.bg-orange-900` | Variaciones de naranja |

#### Yellow (Amarillo)

| Clase | Descripción |
|-------|-------------|
| `.bg-yellow` | Fondo amarillo base |
| `.bg-yellow-100` a `.bg-yellow-900` | Variaciones de amarillo |

#### Red (Rojo)

| Clase | Descripción |
|-------|-------------|
| `.bg-red` | Fondo rojo base |
| `.bg-red-100` a `.bg-red-900` | Variaciones de rojo |

#### Pink (Rosa)

| Clase | Descripción |
|-------|-------------|
| `.bg-pink` | Fondo rosa base |
| `.bg-pink-100` a `.bg-pink-900` | Variaciones de rosa |

### Paleta Neutra

#### Black (Negro)

| Clase | Descripción |
|-------|-------------|
| `.bg-black` | Fondo negro base |
| `.bg-black-100` a `.bg-black-900` | Variaciones de negro |

#### Grey (Gris)

| Clase | Descripción |
|-------|-------------|
| `.bg-gray` | Fondo gris base |
| `.bg-gray-100` | Gris muy claro |
| `.bg-gray-200` | Gris claro |
| `.bg-gray-300` | Gris claro medio |
| `.bg-gray-400` | Gris medio claro |
| `.bg-gray-500` | Gris medio |
| `.bg-gray-600` | Gris medio oscuro |
| `.bg-gray-700` | Gris oscuro medio |
| `.bg-gray-800` | Gris oscuro |
| `.bg-gray-900` | Gris muy oscuro |

#### Silver (Plateado)

| Clase | Descripción |
|-------|-------------|
| `.bg-silver` | Fondo plateado base |
| `.bg-silver-100` a `.bg-silver-900` | Variaciones de plateado |

#### White (Blanco)

| Clase | Descripción |
|-------|-------------|
| `.bg-white` | Fondo blanco base |
| `.bg-white-100` a `.bg-white-900` | Variaciones de blanco |

### Colores de Bootstrap

| Clase | Descripción |
|-------|-------------|
| `.bg-primary` | Color primario de Bootstrap |
| `.bg-secondary` | Color secundario |
| `.bg-success` | Color de éxito (verde) |
| `.bg-danger` | Color de peligro (rojo) |
| `.bg-warning` | Color de advertencia (amarillo) |
| `.bg-info` | Color de información (azul claro) |
| `.bg-light` | Color claro |
| `.bg-dark` | Color oscuro |
| `.bg-body` | Color del body |
| `.bg-transparent` | Fondo transparente |

### Background Utilities

| Clase | Descripción |
|-------|-------------|
| `.bg-gradient` | Aplica gradiente al fondo |
| `.bg-opacity-10` | Opacidad de fondo 10% |
| `.bg-opacity-25` | Opacidad de fondo 25% |
| `.bg-opacity-50` | Opacidad de fondo 50% |
| `.bg-opacity-75` | Opacidad de fondo 75% |
| `.bg-opacity-100` | Opacidad de fondo 100% |

**Ejemplo:**
```html
<!-- Tarjetas con diferentes colores -->
<div class="row">
  <div class="col-md-4">
    <div class="card bg-blue-500 text-white">
      <div class="card-body">Card Azul</div>
    </div>
  </div>
  <div class="col-md-4">
    <div class="card bg-green-500 text-white">
      <div class="card-body">Card Verde</div>
    </div>
  </div>
  <div class="col-md-4">
    <div class="card bg-red-500 text-white">
      <div class="card-body">Card Rojo</div>
    </div>
  </div>
</div>

<!-- Alertas personalizadas -->
<div class="alert bg-yellow-100 border border-yellow-500">
  <strong>Advertencia:</strong> Mensaje importante
</div>

<!-- Fondo con opacidad -->
<div class="bg-primary bg-opacity-25 p-3">
  Fondo primario con 25% de opacidad
</div>
```

---

## Colores de Texto

### Paleta Principal de Texto

Todas las clases de color de fondo tienen su equivalente para texto, reemplazando `bg-` por `text-`:

#### Blue (Azul)
- `.text-blue`, `.text-blue-100` a `.text-blue-900`

#### Indigo
- `.text-indigo`, `.text-indigo-100` a `.text-indigo-900`

#### Purple (Morado)
- `.text-purple`, `.text-purple-100` a `.text-purple-900`

#### Aqua
- `.text-aqua`, `.text-aqua-100` a `.text-aqua-900`

#### Teal
- `.text-teal`, `.text-teal-100` a `.text-teal-900`

#### Green (Verde)
- `.text-green`, `.text-green-100` a `.text-green-900`

#### Lime
- `.text-lime`, `.text-lime-100` a `.text-lime-900`

#### Orange (Naranja)
- `.text-orange`, `.text-orange-100` a `.text-orange-900`

#### Yellow (Amarillo)
- `.text-yellow`, `.text-yellow-100` a `.text-yellow-900`

#### Red (Rojo)
- `.text-red`, `.text-red-100` a `.text-red-900`

#### Pink (Rosa)
- `.text-pink`, `.text-pink-100` a `.text-pink-900`

### Paleta Neutra de Texto

#### Black (Negro)
- `.text-black`, `.text-black-100` a `.text-black-900`

#### Grey (Gris)
- `.text-gray`, `.text-gray-100` a `.text-gray-900`

#### Silver (Plateado)
- `.text-silver`, `.text-silver-100` a `.text-silver-900`

#### White (Blanco)
- `.text-white`, `.text-white-100` a `.text-white-900`

### Colores de Bootstrap para Texto

| Clase | Descripción |
|-------|-------------|
| `.text-primary` | Texto color primario |
| `.text-secondary` | Texto color secundario |
| `.text-success` | Texto color éxito |
| `.text-danger` | Texto color peligro |
| `.text-warning` | Texto color advertencia |
| `.text-info` | Texto color información |
| `.text-light` | Texto color claro |
| `.text-dark` | Texto color oscuro |
| `.text-body` | Texto color del body |
| `.text-muted` | Texto atenuado |
| `.text-white` | Texto blanco |
| `.text-black-50` | Texto negro 50% opacidad |
| `.text-white-50` | Texto blanco 50% opacidad |

### Text Opacity

| Clase | Descripción |
|-------|-------------|
| `.text-opacity-25` | Opacidad de texto 25% |
| `.text-opacity-50` | Opacidad de texto 50% |
| `.text-opacity-75` | Opacidad de texto 75% |
| `.text-opacity-100` | Opacidad de texto 100% |

**Ejemplo:**
```html
<!-- Títulos con colores -->
<h1 class="text-blue-700 fw-700">Título Principal</h1>
<h2 class="text-green-600 fw-600">Subtítulo</h2>

<!-- Badges con colores personalizados -->
<span class="badge bg-blue-500 text-white">Nuevo</span>
<span class="badge bg-green-500 text-white">Activo</span>
<span class="badge bg-red-500 text-white">Urgente</span>

<!-- Texto con diferentes opacidades -->
<p class="text-dark">Texto normal</p>
<p class="text-dark text-opacity-75">Texto 75% opacidad</p>
<p class="text-dark text-opacity-50">Texto 50% opacidad</p>
<p class="text-dark text-opacity-25">Texto 25% opacidad</p>

<!-- Estado de un elemento -->
<div class="d-flex align-items-center">
  <span class="badge bg-green-100 text-green-800 me-2">●</span>
  <span class="text-green-700 fw-500">En línea</span>
</div>
```

---

## Guía de Migración

### De CSS Personalizado a Clases Utilitarias

#### ❌ Antes (CSS Personalizado)

```css
/* custom.css */
.my-card {
  width: 300px;
  padding: 20px;
  margin-bottom: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.my-title {
  font-size: 24px;
  font-weight: 700;
  color: #0d6efd;
  text-align: center;
  margin-bottom: 10px;
}

.my-text {
  font-size: 14px;
  line-height: 1.5;
  color: #6c757d;
}
```

```html
<div class="my-card">
  <h3 class="my-title">Título</h3>
  <p class="my-text">Contenido del card</p>
</div>
```

#### ✅ Después (Clases Utilitarias)

```html
<div class="card w-300px p-3 mb-3 bg-light rounded-3 shadow-sm">
  <h3 class="fs-24px fw-700 text-primary text-center mb-2">Título</h3>
  <p class="fs-14px lh-base text-muted">Contenido del card</p>
</div>
```

### Ejemplos de Conversión Común

#### Layout con Flexbox

❌ **Antes:**
```css
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```

✅ **Después:**
```html
<div class="d-flex justify-content-between align-items-center px-4 py-3 bg-white shadow-sm">
  <!-- Contenido -->
</div>
```

#### Botón Personalizado

❌ **Antes:**
```css
.btn-custom {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  background-color: #0d6efd;
  color: white;
  border-radius: 8px;
  border: none;
}
```

✅ **Después:**
```html
<button class="btn bg-primary text-white px-4 py-3 fs-16px fw-600 rounded-3 border-0">
  Botón
</button>
```

#### Grid Responsivo

❌ **Antes:**
```css
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  padding: 20px;
}
```

✅ **Después:**
```html
<div class="row row-space-10 p-3">
  <div class="col-lg-3 col-md-4 col-sm-6"><!-- Item --></div>
  <div class="col-lg-3 col-md-4 col-sm-6"><!-- Item --></div>
  <div class="col-lg-3 col-md-4 col-sm-6"><!-- Item --></div>
  <div class="col-lg-3 col-md-4 col-sm-6"><!-- Item --></div>
</div>
```

---

## Mejores Prácticas

### 1. Combina Clases para Componentes Complejos

```html
<!-- Card de Producto -->
<div class="card shadow-lg rounded-3 overflow-hidden">
  <img src="product.jpg" class="w-100 h-200px" style="object-fit: cover;">
  <div class="card-body p-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <span class="badge bg-success-100 text-success-800 fs-12px fw-600">Nuevo</span>
      <span class="text-gray-600 fs-14px">$99.99</span>
    </div>
    <h5 class="fs-18px fw-600 text-dark mb-2">Nombre del Producto</h5>
    <p class="fs-14px text-gray-600 mb-3 text-truncate">Descripción corta del producto</p>
    <button class="btn btn-primary w-100 py-2">Agregar al Carrito</button>
  </div>
</div>
```

### 2. Usa Clases Responsivas

```html
<!-- Navegación Responsiva -->
<nav class="d-flex flex-column flex-lg-row justify-content-between align-items-start align-items-lg-center p-3">
  <div class="mb-3 mb-lg-0">Logo</div>
  <div class="d-flex flex-column flex-lg-row">
    <a href="#" class="me-lg-3 mb-2 mb-lg-0">Inicio</a>
    <a href="#" class="me-lg-3 mb-2 mb-lg-0">Productos</a>
    <a href="#" class="me-lg-3 mb-2 mb-lg-0">Contacto</a>
  </div>
</nav>
```

### 3. Mantén la Consistencia en Espaciado

```html
<!-- Formulario Consistente -->
<form>
  <div class="mb-3">
    <label class="form-label fw-500">Nombre</label>
    <input type="text" class="form-control">
  </div>
  <div class="mb-3">
    <label class="form-label fw-500">Email</label>
    <input type="email" class="form-control">
  </div>
  <div class="mb-3">
    <label class="form-label fw-500">Mensaje</label>
    <textarea class="form-control" rows="4"></textarea>
  </div>
  <button type="submit" class="btn btn-primary px-4 py-2">Enviar</button>
</form>
```

### 4. Aprovecha los Colores Semánticos

```html
<!-- Estados y Alertas -->
<div class="alert bg-green-100 border border-green-500 text-green-800 mb-3">
  <i class="fas fa-check-circle me-2"></i>
  Operación exitosa
</div>

<div class="alert bg-yellow-100 border border-yellow-500 text-yellow-800 mb-3">
  <i class="fas fa-exclamation-triangle me-2"></i>
  Advertencia importante
</div>

<div class="alert bg-red-100 border border-red-500 text-red-800 mb-3">
  <i class="fas fa-times-circle me-2"></i>
  Error en la operación
</div>
```

### 5. Crea Patrones Reutilizables

```html
<!-- Patrón de Tarjeta Estadística -->
<div class="card bg-gradient-primary text-white rounded-3 shadow-lg">
  <div class="card-body p-4">
    <div class="d-flex justify-content-between align-items-start mb-3">
      <div>
        <div class="fs-12px fw-500 text-opacity-75 mb-1">Total Ventas</div>
        <div class="fs-30px fw-700">$45,231</div>
      </div>
      <div class="bg-white bg-opacity-25 rounded-circle p-3">
        <i class="fas fa-dollar-sign fs-24px"></i>
      </div>
    </div>
    <div class="d-flex align-items-center">
      <span class="badge bg-white bg-opacity-25 me-2">+12.5%</span>
      <span class="fs-12px text-opacity-75">vs mes anterior</span>
    </div>
  </div>
</div>
```

### 6. Optimiza para Dark Mode

```html
<!-- Componente Compatible con Dark Mode -->
<div class="card bg-white bg-dark-100 border border-gray-200 border-dark-700">
  <div class="card-body">
    <h5 class="text-dark text-white-dark fw-600 mb-3">Título</h5>
    <p class="text-gray-600 text-gray-400-dark">
      Contenido que se adapta a dark mode
    </p>
  </div>
</div>
```

### 7. Usa Variables de Breakpoints

```html
<!-- Layout Adaptativo -->
<div class="container-fluid">
  <div class="row">
    <!-- Sidebar: oculto en móvil, visible en tablet+ -->
    <div class="col-lg-3 d-none d-lg-block">
      <aside class="sticky-top">Sidebar</aside>
    </div>
    
    <!-- Contenido principal -->
    <div class="col-lg-9">
      <main>Contenido principal</main>
    </div>
  </div>
</div>
```

### 8. Combina Utilidades con Componentes Bootstrap

```html
<!-- Tabla Mejorada -->
<div class="table-responsive">
  <table class="table table-hover table-valign-middle">
    <thead class="bg-gray-100">
      <tr>
        <th class="fw-600 text-uppercase fs-12px text-gray-600">Producto</th>
        <th class="fw-600 text-uppercase fs-12px text-gray-600">Precio</th>
        <th class="fw-600 text-uppercase fs-12px text-gray-600">Stock</th>
        <th class="fw-600 text-uppercase fs-12px text-gray-600">Estado</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="fw-500">Producto 1</td>
        <td class="text-gray-600">$29.99</td>
        <td class="text-gray-600">150</td>
        <td><span class="badge bg-success-100 text-success-800">Disponible</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## Recursos Adicionales

- 📂 **Ubicación del Helper**: `src/app/pages/helper/helper-css/`
- 🎨 **Variables de Color**: Revisa el archivo de variables SCSS del template
- 📱 **Breakpoints de Bootstrap 5**: 
  - sm: 576px
  - md: 768px
  - lg: 992px
  - xl: 1200px
  - xxl: 1400px

---

## Conclusión

Las clases CSS utilitarias del template Color Admin proporcionan una forma poderosa y eficiente de construir interfaces sin escribir CSS personalizado. Al seguir estas convenciones:

✅ Reduces el tamaño del CSS personalizado  
✅ Mejoras la mantenibilidad del código  
✅ Aceleras el desarrollo  
✅ Mantienes consistencia visual  
✅ Facilitas el trabajo en equipo  

**Recuerda**: Todas estas clases sobrescribirán tus estilos personalizados a menos que uses `!important`. Prefiere siempre las clases utilitarias sobre CSS personalizado cuando sea posible.

---

*Documento creado el 15 de enero de 2026 por GitHub Copilot para el proyecto ezekl-budget - Color Admin Template*
