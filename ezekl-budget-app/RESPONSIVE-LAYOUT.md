# Sistema de Layout Responsivo: Color-Admin + Ionic

## Descripción General

Este sistema permite que la aplicación muestre diferentes interfaces según el tamaño de pantalla:
- **Desktop (≥ 768px)**: Usa el template **Color-Admin** completo
- **Mobile (< 768px)**: Usa componentes de **Ionic** para una experiencia nativa

## Arquitectura

```
src/app/
├── service/
│   └── platform-detector.service.ts   # Detecta el modo de plataforma
├── shared/
│   └── responsive-component.base.ts   # Clase base para componentes responsivos
├── layouts/
│   └── mobile-layout/                 # Layout principal de Ionic
│       └── mobile-layout.component.ts
├── assets/
│   └── styles/
│       └── ionic-mobile.css           # CSS de Ionic (carga dinámica)
└── pages/
    └── home/
        ├── home.ts                    # Lógica compartida
        └── home.html                  # Template dual (desktop/mobile)
```

## Cómo Funciona

### 1. Detección de Plataforma

El servicio `PlatformDetectorService` usa Angular CDK BreakpointObserver para detectar cambios en el tamaño de pantalla:

```typescript
// Se inyecta automáticamente y maneja todo
constructor(private platformDetector: PlatformDetectorService) {}

// Propiedades disponibles:
platformDetector.isMobile     // boolean
platformDetector.isDesktop    // boolean
platformDetector.platformMode$  // Observable<'mobile' | 'desktop'>
```

### 2. CSS Dinámico

- Los estilos de **Color-Admin** siempre están cargados
- Los estilos de **Ionic** (`ionic-mobile.css`) se cargan dinámicamente solo en móvil
- Las clases `.ionic-mode` y `.desktop-mode` se agregan al `<body>` automáticamente

### 3. Templates Duales

Cada componente puede tener secciones diferentes según el modo:

```html
@if (isMobile()) {
  <!-- Contenido Ionic para móviles -->
  <ion-card>
    <ion-card-content>Mobile View</ion-card-content>
  </ion-card>
}

@if (isDesktop()) {
  <!-- Contenido Color-Admin para desktop -->
  <panel title="Desktop View">
    Desktop content
  </panel>
}
```

## Crear un Componente Responsivo

### Paso 1: Actualizar el TypeScript

```typescript
import { Component, computed, signal, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
// Importar componentes de Ionic que necesites
import { IonCard, IonCardContent, IonButton } from '@ionic/angular/standalone';
// Importar servicio de detección
import { PlatformDetectorService, PlatformMode } from '../../service/platform-detector.service';

@Component({
  selector: 'my-component',
  templateUrl: './my-component.html',
  standalone: true,
  imports: [
    CommonModule,
    // Componentes de Color-Admin
    PanelComponent,
    // Componentes de Ionic
    IonCard,
    IonCardContent,
    IonButton
  ]
})
export class MyComponent implements OnDestroy {
  // Signals para manejo reactivo
  platformMode = signal<PlatformMode>('desktop');
  isMobile = computed(() => this.platformMode() === 'mobile');
  isDesktop = computed(() => this.platformMode() === 'desktop');
  
  private subscription: Subscription | null = null;

  // TU LÓGICA DE NEGOCIO AQUÍ
  // Esta lógica es compartida entre ambos layouts
  myData = { ... };
  
  myMethod(): void {
    // Funciona igual en ambos layouts
  }

  constructor(private platformDetector: PlatformDetectorService) {
    this.subscription = this.platformDetector.platformMode$.subscribe(mode => {
      this.platformMode.set(mode);
    });
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }
}
```

### Paso 2: Crear el Template Dual

```html
<!-- ===== MOBILE (Ionic) ===== -->
@if (isMobile()) {
  <ion-card>
    <ion-card-header>
      <ion-card-title>{{ myData.title }}</ion-card-title>
    </ion-card-header>
    <ion-card-content>
      {{ myData.content }}
      <ion-button (click)="myMethod()">Acción</ion-button>
    </ion-card-content>
  </ion-card>
}

<!-- ===== DESKTOP (Color-Admin) ===== -->
@if (isDesktop()) {
  <panel [title]="myData.title">
    {{ myData.content }}
    <button class="btn btn-primary" (click)="myMethod()">Acción</button>
  </panel>
}
```

## Componentes de Ionic Disponibles

Los componentes de Ionic se importan individualmente (standalone):

```typescript
import { 
  IonApp, 
  IonContent,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonList,
  IonItem,
  IonLabel,
  IonIcon,
  IonBadge,
  IonRefresher,
  IonRefresherContent,
  IonMenu,
  IonMenuButton,
  IonFab,
  IonFabButton,
  IonModal,
  IonToast,
  IonLoading,
  // ... más componentes
} from '@ionic/angular/standalone';
```

## Íconos de Ionicons

```typescript
import { addIcons } from 'ionicons';
import { 
  homeOutline, 
  personOutline, 
  settingsOutline 
} from 'ionicons/icons';

// En el constructor:
addIcons({ homeOutline, personOutline, settingsOutline });

// En el template:
<ion-icon name="home-outline"></ion-icon>
```

## Clases CSS Utilitarias

```html
<!-- Solo visible en móvil -->
<div class="ionic-only">Solo móvil</div>
<div class="mobile-only">Solo móvil</div>

<!-- Solo visible en desktop -->
<div class="desktop-only">Solo desktop</div>
```

## Buenas Prácticas

### 1. Lógica Compartida
Mantén **toda la lógica** en el archivo `.ts`. Los templates solo deben renderizar datos.

### 2. Métodos Reutilizables
Usa los mismos métodos para ambos layouts:
```typescript
// ✅ Bien - Un método para ambos
handleSubmit(): void { ... }

// ❌ Mal - Métodos duplicados
handleSubmitMobile(): void { ... }
handleSubmitDesktop(): void { ... }
```

### 3. Datos Consistentes
Los mismos datos deben mostrarse en ambos layouts, solo cambia la presentación:
```typescript
// ✅ Una sola fuente de datos
users$ = this.userService.getUsers();
```

### 4. Servicios Agnósticos
Los servicios no deben saber sobre el layout:
```typescript
// ✅ Bien
@Injectable()
export class UserService {
  getUsers(): Observable<User[]> { ... }
}

// ❌ Mal
getMobileUsers() / getDesktopUsers()
```

## Testing

Para probar ambos layouts:

1. **Chrome DevTools**: Usa el modo responsive (F12 → Toggle device toolbar)
2. **Resize Window**: Cambia el tamaño de la ventana del navegador
3. **Simuladores**: Usa simuladores de iOS/Android

## Troubleshooting

### Los estilos de Ionic no se aplican
- Verifica que `ionic-mobile.css` existe en `src/assets/styles/`
- Revisa la consola del navegador por errores de carga

### Conflictos de estilos
- Usa las clases `.ionic-mode` y `.desktop-mode` para scope
- Evita estilos globales que afecten ambos layouts

### El modo no cambia
- Verifica que `PlatformDetectorService` está en providers
- Revisa la consola por errores de suscripción

## Recursos

- [Ionic Angular Standalone](https://ionicframework.com/docs/angular/build-options#standalone-based-applications)
- [Angular CDK Layout](https://material.angular.io/cdk/layout/overview)
- [Color-Admin Template](https://seantheme.com/color-admin/)
