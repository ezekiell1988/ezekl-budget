import { Directive, OnDestroy, inject, signal, computed } from '@angular/core';
import { Subscription } from 'rxjs';
import { PlatformDetectorService, PlatformMode } from '../service/platform-detector.service';

/**
 * Clase base abstracta para componentes que necesitan
 * manejar diferentes templates según el tamaño de pantalla.
 * 
 * Uso:
 * 1. Extender esta clase en tu componente
 * 2. Usar las señales isMobile/isDesktop en el template
 * 3. Usar @if(isMobile()) o @if(isDesktop()) para renderizar
 *    diferentes secciones del template
 * 
 * Ejemplo:
 * ```typescript
 * @Component({...})
 * export class MyComponent extends ResponsiveComponent {
 *   // Tu lógica aquí
 * }
 * ```
 * 
 * En el template:
 * ```html
 * @if (isMobile()) {
 *   <!-- Template Ionic -->
 * } @else {
 *   <!-- Template Color-Admin -->
 * }
 * ```
 */
@Directive()
export abstract class ResponsiveComponent implements OnDestroy {
  protected platformDetector = inject(PlatformDetectorService);
  private subscription: Subscription | null = null;

  // Signal reactivo para el modo de plataforma
  protected platformMode = signal<PlatformMode>(this.platformDetector.currentMode);

  // Signals computados para uso en templates
  protected isMobile = computed(() => this.platformMode() === 'mobile');
  protected isDesktop = computed(() => this.platformMode() === 'desktop');

  constructor() {
    this.initSubscription();
  }

  private initSubscription(): void {
    this.subscription = this.platformDetector.platformMode$.subscribe(mode => {
      this.platformMode.set(mode);
      this.onPlatformModeChange(mode);
    });
  }

  /**
   * Hook que se ejecuta cuando cambia el modo de plataforma.
   * Sobrescribir en componentes hijos si se necesita lógica adicional.
   */
  protected onPlatformModeChange(mode: PlatformMode): void {
    // Override en componentes hijos si es necesario
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }
}
