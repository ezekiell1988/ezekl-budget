# Exam Question Viewer

Una página interactiva para visualizar PDFs de exámenes con preguntas asociadas, con navegación bidireccional entre el PDF y las preguntas.

## Características

### 📄 Visualización de PDF
- Renderizado de PDFs usando PDF.js
- **Carga progresiva**: Renderiza las primeras 20 páginas inmediatamente para uso rápido
- **Lazy loading**: Carga páginas adicionales automáticamente al hacer scroll (10 páginas por lote)
- **Carga en background**: Después de la carga inicial, continúa cargando TODAS las páginas restantes en background sin bloquear la UI
- Navegación por páginas (anterior/siguiente)
- Indicador de página actual
- Click en el PDF para buscar pregunta asociada a la página actual
- Navegación inteligente que pre-carga páginas cercanas cuando saltas a una página específica

### ❓ Lista de Preguntas
- Navegación por preguntas con controles anterior/siguiente
- Input numérico para ir directamente a una pregunta específica
- Carga automática de preguntas no cargadas al buscar por número
- Infinite scroll para carga progresiva de preguntas (20 por lote)
- **Carga en background**: Después de la carga inicial, continúa cargando TODAS las preguntas restantes en background
- Pull to refresh para actualizar
- Mostrar número de pregunta, páginas asociadas
- Mostrar pregunta corta y respuesta correcta
- Click en pregunta para navegar al PDF

### 🔄 Navegación Bidireccional
- **PDF → Pregunta**: Click en el PDF busca la pregunta asociada a la página actual y hace scroll hasta ella
- **Pregunta → PDF**: Click en una pregunta navega a la página del PDF donde aparece
- Resaltado temporal de la pregunta al navegar desde el PDF

### 📱 Responsive
- Layout split 80/20 (PDF/Preguntas) en desktop
- Layout vertical en móviles
- Adaptación automática del tamaño del PDF al contenedor

## Estructura de Archivos

```
exam-question/
├── exam-question.page.ts       # Lógica del componente
├── exam-question.page.html     # Template
├── exam-question.page.scss     # Estilos
└── exam-question.ts            # Placeholder (deprecated)

services/
└── exam-question.service.ts    # Servicio para gestionar preguntas

assets/pdfs/
├── az-204.pdf                  # PDF del examen AZ-204 (idExam=1)
└── dp-300.pdf                  # PDF del examen DP-300 (idExam=2)
```

## Configuración de PDFs

Los PDFs disponibles se configuran en el archivo `exam-question.page.ts`:

```typescript
const AVAILABLE_PDFS: ExamPdf[] = [
  { id: 1, filename: 'az-204.pdf', displayName: 'AZ-204: Developing Solutions for Microsoft Azure', path: '/assets/pdfs/az-204.pdf' },
  { id: 2, filename: 'dp-300.pdf', displayName: 'DP-300: Administering Microsoft Azure SQL Solutions', path: '/assets/pdfs/dp-300.pdf' },
];
```

Para agregar un nuevo PDF:
1. Coloca el PDF en `src/assets/pdfs/`
2. Agrega una entrada en `AVAILABLE_PDFS` con el ID correspondiente
3. Asegúrate de que el backend tenga preguntas con ese `idExam`

## API Backend

El servicio consume el endpoint `/api/exam-questions/{idExam}/questions.json` con los siguientes parámetros:

- `search`: Término de búsqueda (opcional)
- `sort`: Campo de ordenamiento (`numberQuestion_asc` o `numberQuestion_desc`)
- `page`: Número de página (default: 1)
- `itemPerPage`: Elementos por página (default: 10, max: 100)

### Respuesta esperada:

```json
{
  "total": 100,
  "data": [
    {
      "numberQuestion": 1,
      "startPage": 5,
      "endPage": 7,
      "shortQuestion": "¿Qué es Azure...?",
      "correctAnswer": "A",
      "explanation": "...",
      ...
    }
  ]
}
```

## Uso

1. Selecciona un examen del dropdown superior
2. El PDF se carga automáticamente a la izquierda
3. Las preguntas se cargan a la derecha con scroll infinito
4. **Navegación del PDF:**
   - Click en el PDF para buscar pregunta de esa página
   - Usa los botones anterior/siguiente o el input numérico para navegar páginas
5. **Navegación de Preguntas:**
   - Click en una pregunta para ir a su página en el PDF
   - Usa los botones anterior/siguiente para moverte entre preguntas
   - Ingresa un número de pregunta para ir directamente a ella
   - Si la pregunta no está cargada, el sistema la cargará automáticamente

## Dependencias

- **PDF.js**: Librería para renderizar PDFs (cargada desde CDN en `index.html`)
- **Ionic Angular**: Framework UI
- **RxJS**: Programación reactiva

## Notas Técnicas

### PDF.js
Se carga desde CDN en `src/index.html`:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
```

### Sincronización PDF-Preguntas
- Las preguntas deben tener `startPage` y `endPage` para la navegación bidireccional
- Si una pregunta no tiene páginas asociadas, solo se mostrará en la lista sin navegación al PDF
- Si una página del PDF no tiene pregunta asociada, se muestra un mensaje informativo

### Manejo de Restauración de Estado (iOS/iPad)
- El sistema guarda automáticamente el estado (examen, página PDF, número de pregunta) en localStorage
- Al cargar la página, se restaura el último estado guardado (si tiene menos de 24 horas)

**Arquitectura de Carga Unificada**:
El sistema usa un flujo de carga unificado controlado por `initialLoadComplete`:
1. Se muestran **skeletons** en PDF y preguntas hasta que AMBOS estén listos
2. PDF y preguntas se cargan en **paralelo** para mayor velocidad
3. Los controles de navegación están **deshabilitados** hasta que todo esté listo
4. El `IntersectionObserver` solo procesa eventos cuando `initialLoadComplete = true`
5. Una vez todo listo, se restaura la posición guardada (página PDF y pregunta)
6. Solo entonces se habilitan los controles y se inicia la carga en background

**Estados de Control**:
- `pdfReady`: TRUE cuando el PDF y sus páginas iniciales están renderizados
- `questionsReady`: TRUE cuando las preguntas iniciales están cargadas
- `initialLoadComplete`: TRUE cuando AMBOS están listos (PDF + preguntas)
- `isRestoringState`: Evita guardar estado durante la restauración
- `hasRestoredState`: Previene restauraciones múltiples

**Beneficios**:
- Elimina race conditions entre PDF y preguntas
- Evita bucles de scroll/recarga en iOS/iPad
- El usuario ve un skeleton claro hasta que todo está listo
- La restauración de posición es precisa porque ocurre después de la carga completa

### Navegación de Preguntas
- Los controles de navegación incluyen botones anterior/siguiente y un input numérico
- El input muestra el número de la pregunta actual
- Si introduces un número de pregunta no cargada, el sistema:
  1. Calcula cuántas páginas de datos necesita cargar
  2. Carga progresivamente hasta encontrar la pregunta
  3. Navega automáticamente a ella
  4. También navega al PDF si la pregunta tiene página asociada
- El contador muestra "Pregunta X de Y" donde Y es el total de preguntas del examen

### Performance
- **Carga inicial rápida**: Solo renderiza las primeras 20 páginas del PDF para que el usuario pueda empezar a usar la app inmediatamente
- **Lazy loading con scroll**: Las páginas se cargan automáticamente en lotes de 10 al hacer scroll
- **Carga en background inteligente**: 
  - Después de 2 segundos de la carga inicial, comienza a cargar automáticamente TODAS las páginas restantes
  - Usa `requestIdleCallback` para no interferir con la interacción del usuario
  - Las páginas se cargan en lotes de 10 durante períodos de inactividad del navegador
  - Una vez completada, todo el PDF está disponible sin necesidad de scroll
- **Pre-carga inteligente**: Cuando navegas a una página específica, se pre-cargan 5 páginas antes y después
- **Infinite scroll de preguntas**: Carga 20 preguntas a la vez con scroll
- **Carga background de preguntas**: 
  - Después de 2 segundos, comienza a cargar automáticamente todas las preguntas restantes
  - Usa `requestIdleCallback` para no bloquear la UI
  - Carga en lotes de 20 durante períodos de inactividad
- Intersection Observer con rootMargin de 500px para anticipar la carga de páginas
- Logs en consola cuando se completa la carga total ("✅ Todas las páginas/preguntas cargadas en background")

## Mejoras Futuras

- [ ] Zoom en el PDF
- [ ] Modo pantalla completa para el PDF
- [ ] Búsqueda de texto en preguntas
- [ ] Filtros por dificultad/tema
- [ ] Modo práctica (mostrar/ocultar respuestas)
- [ ] Favoritos y marcadores
- [ ] Historial de preguntas revisadas
- [ ] Exportar preguntas a PDF/CSV
