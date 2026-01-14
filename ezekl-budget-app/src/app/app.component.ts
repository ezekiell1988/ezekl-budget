import { Component, OnInit, OnDestroy, signal, computed, ChangeDetectorRef, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Subscription } from "rxjs";
import { PlatformDetectorService, PlatformMode, LoggerService } from "./service";
import { AppSettings } from "./service/app-settings.service";
import { MobileLayoutComponent, DesktopLayoutComponent } from "./layouts";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  standalone: true,
  imports: [
    CommonModule,
    MobileLayoutComponent,
    DesktopLayoutComponent,
  ],
})
export class AppComponent implements OnInit, OnDestroy {
  // Signals para manejo reactivo del modo de plataforma
  // Detectar modo inicial SÍNCRONAMENTE para evitar flash de layout incorrecto
  private getInitialMode(): PlatformMode {
    if (typeof window !== 'undefined') {
      return window.matchMedia('(max-width: 768px)').matches ? 'mobile' : 'desktop';
    }
    return 'desktop';
  }
  
  platformMode = signal<PlatformMode>(this.getInitialMode());
  isMobile = computed(() => this.platformMode() === 'mobile');
  isDesktop = computed(() => this.platformMode() === 'desktop');
  
  private platformSubscription: Subscription | null = null;
  private readonly logger = inject(LoggerService).getLogger('AppComponent');

  constructor(
    private platformDetector: PlatformDetectorService,
    private cdr: ChangeDetectorRef,
    private appSettings: AppSettings
  ) {}

  ngOnInit() {
    // Suscribirse a cambios de modo de plataforma
    this.platformSubscription = this.platformDetector.platformMode$.subscribe(mode => {
      // Solo actualizar si cambió
      if (this.platformMode() !== mode) {
        this.platformMode.set(mode);
        this.cdr.detectChanges();
      }
    });
    
    // Verificar si todo está listo para ocultar el loader
    this.checkAndHideLoader();
  }
  
  /**
   * Verifica periódicamente si la configuración y los estilos están listos
   * para ocultar el loader inicial
   */
  private checkAndHideLoader(): void {
    const checkInterval = setInterval(() => {
      const configReady = this.appSettings.configLoaded;
      const stylesReady = this.appSettings.stylesLoaded;
      
      if (configReady && stylesReady) {
        clearInterval(checkInterval);
        this.hideLoader();
      }
    }, 100); // Verificar cada 100ms
    
    // Timeout de seguridad: ocultar loader después de 5 segundos máximo
    setTimeout(() => {
      clearInterval(checkInterval);
      if (this.isLoaderVisible()) {
        this.logger.warn('Timeout de carga - mostrando app');
        this.hideLoader();
      }
    }, 5000);
  }
  
  /**
   * Oculta el loader inicial con una animación suave
   */
  private hideLoader(): void {
    const loader = document.getElementById('app-loader');
    
    if (loader) {
      loader.style.opacity = '0';
      setTimeout(() => {
        loader.remove();
      }, 500); // Esperar a que termine la transición
    } else {
      this.logger.warn('Loader ya fue removido');
    }
  }
  
  /**
   * Verifica si el loader está visible
   */
  private isLoaderVisible(): boolean {
    const loader = document.getElementById('app-loader');
    return loader !== null;
  }

  ngOnDestroy(): void {
    if (this.platformSubscription) {
      this.platformSubscription.unsubscribe();
    }
  }
}
