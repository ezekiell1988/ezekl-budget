import { Injectable, OnDestroy } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { BehaviorSubject, Observable, Subscription } from 'rxjs';
import { distinctUntilChanged, map } from 'rxjs/operators';
import { AppSettings } from './app-settings.service';
import { LoggerService } from './logger.service';

export type PlatformMode = 'mobile' | 'desktop';

@Injectable({
  providedIn: 'root'
})
export class PlatformDetectorService implements OnDestroy {
  private readonly MOBILE_BREAKPOINT = '(max-width: 768px)';
  
  // Detectar modo inicial SÍNCRONAMENTE usando window.matchMedia
  private getInitialMode(): PlatformMode {
    if (typeof window !== 'undefined') {
      return window.matchMedia(this.MOBILE_BREAKPOINT).matches ? 'mobile' : 'desktop';
    }
    return 'desktop';
  }
  
  private platformModeSubject = new BehaviorSubject<PlatformMode>(this.getInitialMode());
  private ionicStylesLoaded = false;
  private desktopStylesLoaded = false;
  private ionicStyleElements: HTMLLinkElement[] = [];
  private desktopStyleElements: HTMLLinkElement[] = [];
  private subscription: Subscription;
  private loadingOverlay: HTMLDivElement | null = null;

  // Archivos CSS compilados que se cargan dinámicamente
  private readonly DESKTOP_CSS_FILES = ['desktop.css'];
  private readonly IONIC_CSS_FILES = ['mobile.css'];

  /**
   * Observable que emite el modo actual de la plataforma
   */
  platformMode$: Observable<PlatformMode> = this.platformModeSubject.asObservable();

  /**
   * Indica si es modo móvil
   */
  isMobile$: Observable<boolean> = this.platformMode$.pipe(
    map(mode => mode === 'mobile'),
    distinctUntilChanged()
  );

  /**
   * Indica si es modo desktop
   */
  isDesktop$: Observable<boolean> = this.platformMode$.pipe(
    map(mode => mode === 'desktop'),
    distinctUntilChanged()
  );

  constructor(
    private breakpointObserver: BreakpointObserver,
    private appSettings: AppSettings,
    private logger: LoggerService
  ) {
    this.logger.debug('PlatformDetectorService initialized');
    
    // Limpiar TODOS los estilos que puedan existir
    this.cleanAllStyles();
    
    // Cargar estilos según el modo inicial
    const initialMode = this.getInitialMode();
    this.logger.debug(`Initial platform mode: ${initialMode}`);
    
    this.updateBodyClasses(initialMode);
    
    // Cargar CSS inmediatamente
    if (initialMode === 'mobile') {
      this.loadIonicStyles();
    } else {
      this.loadDesktopStyles();
    }
    
    this.initializeBreakpointObserver();
  }

  private initializeBreakpointObserver(): void {
    this.subscription = this.breakpointObserver
      .observe([this.MOBILE_BREAKPOINT])
      .pipe(distinctUntilChanged())
      .subscribe(result => {
        const newMode: PlatformMode = result.matches ? 'mobile' : 'desktop';
        this.onPlatformModeChange(newMode);
      });
  }

  private onPlatformModeChange(mode: PlatformMode): void {
    const previousMode = this.platformModeSubject.value;
    
    if (previousMode !== mode) {
      // 1. Mostrar loading primero
      this.showLoadingOverlay();
      
      // 2. Esperar a que el loading se renderice, luego cambiar estilos
      requestAnimationFrame(() => {
        this.platformModeSubject.next(mode);
        this.updateBodyClasses(mode);
        this.handleStylesChange(mode);
      });
    }
  }

  private updateBodyClasses(mode: PlatformMode): void {
    const body = document.body;
    
    if (mode === 'mobile') {
      body.classList.add('ionic-mode');
      body.classList.remove('desktop-mode');
    } else {
      body.classList.add('desktop-mode');
      body.classList.remove('ionic-mode');
    }
  }

  private handleStylesChange(mode: PlatformMode): void {
    this.logger.debug(`Platform mode changed to: ${mode}`);
    
    // Resetear flag de estilos cargados
    this.appSettings.stylesLoaded = false;
    
    // 2. Limpiar TODOS los estilos anteriores (síncrono)
    this.cleanAllStyles();
    
    // 3. Cargar estilos según el nuevo modo (asíncrono - oculta loading al terminar)
    if (mode === 'mobile') {
      this.loadIonicStyles();
    } else {
      this.loadDesktopStyles();
    }
  }

  /**
   * Carga dinámicamente los estilos de Ionic
   */
  private loadIonicStyles(): void {
    if (this.ionicStylesLoaded) {
      this.logger.debug('Ionic styles already loaded, skipping...');
      return;
    }

    this.logger.debug('Loading Ionic CSS files dynamically...');
    this.logger.debug(`Files to load: ${JSON.stringify(this.IONIC_CSS_FILES)}`);
    
    let loadedCount = 0;
    const totalFiles = this.IONIC_CSS_FILES.length;

    this.IONIC_CSS_FILES.forEach((href, index) => {
      const linkElement = document.createElement('link');
      linkElement.id = `ionic-dynamic-styles-${index}`;
      linkElement.rel = 'stylesheet';
      linkElement.href = href;
      
      this.logger.debug(`Creating link for: ${href}`);
      
      linkElement.onload = () => {
        loadedCount++;
        this.logger.debug(`Loaded ${loadedCount}/${totalFiles}: ${href}`);
        if (loadedCount === totalFiles) {
          this.appSettings.stylesLoaded = true;
          this.logger.debug('All Ionic CSS files loaded successfully');
          // 4. Ocultar loading solo cuando TODOS los estilos estén cargados y aplicados
          setTimeout(() => this.hideLoadingOverlay(), 150);
        }
      };
      
      linkElement.onerror = (error) => {
        this.logger.error(`Failed to load Ionic CSS: ${href}`, error);
        loadedCount++;
        if (loadedCount === totalFiles) {
          this.logger.warn('Some CSS files failed to load, but continuing...');
          this.appSettings.stylesLoaded = true;
          // Ocultar loading incluso si hubo errores
          setTimeout(() => this.hideLoadingOverlay(), 150);
        }
      };
      
      document.head.appendChild(linkElement);
      this.ionicStyleElements.push(linkElement);
    });

    this.ionicStylesLoaded = true;
  }

  /**
   * Descarga los estilos de Ionic
   */
  private unloadIonicStyles(): void {
    if (!this.ionicStylesLoaded || this.ionicStyleElements.length === 0) return;

    this.logger.debug('Unloading Ionic CSS files...');
    this.ionicStyleElements.forEach(element => element.remove());
    this.ionicStyleElements = [];
    this.ionicStylesLoaded = false;
    
    this.logger.debug('All Ionic CSS files unloaded');
  }

  /**
   * Carga dinámicamente los estilos de Desktop (Color-Admin)
   */
  private loadDesktopStyles(): void {
    if (this.desktopStylesLoaded) {
      this.logger.debug('Desktop styles already loaded, skipping...');
      return;
    }

    this.logger.debug('Loading Desktop CSS files dynamically...');
    this.logger.debug(`Files to load: ${JSON.stringify(this.DESKTOP_CSS_FILES)}`);
    
    let loadedCount = 0;
    const totalFiles = this.DESKTOP_CSS_FILES.length;

    this.DESKTOP_CSS_FILES.forEach((href, index) => {
      const linkElement = document.createElement('link');
      linkElement.id = `desktop-dynamic-styles-${index}`;
      linkElement.rel = 'stylesheet';
      linkElement.href = href;
      
      this.logger.debug(`Creating link for: ${href}`);
      
      linkElement.onload = () => {
        loadedCount++;
        this.logger.debug(`Loaded ${loadedCount}/${totalFiles}: ${href}`);
        if (loadedCount === totalFiles) {
          this.appSettings.stylesLoaded = true;
          this.logger.debug('All Desktop CSS files loaded successfully');
          // 4. Ocultar loading solo cuando TODOS los estilos estén cargados y aplicados
          setTimeout(() => this.hideLoadingOverlay(), 150);
        }
      };
      
      linkElement.onerror = (error) => {
        this.logger.error(`Failed to load Desktop CSS: ${href}`, error);
        loadedCount++;
        if (loadedCount === totalFiles) {
          this.logger.warn('Some CSS files failed to load, but continuing...');
          this.appSettings.stylesLoaded = true;
          // Ocultar loading incluso si hubo errores
          setTimeout(() => this.hideLoadingOverlay(), 150);
        }
      };
      
      document.head.appendChild(linkElement);
      this.desktopStyleElements.push(linkElement);
    });

    this.desktopStylesLoaded = true;
  }

  /**
   * Descarga los estilos de Desktop
   */
  private unloadDesktopStyles(): void {
    if (!this.desktopStylesLoaded || this.desktopStyleElements.length === 0) return;

    this.logger.debug('Unloading Desktop CSS files...');
    this.desktopStyleElements.forEach(element => element.remove());
    this.desktopStyleElements = [];
    this.desktopStylesLoaded = false;
    
    this.logger.debug('All Desktop CSS files unloaded');
  }

  /**
   * Limpia TODOS los estilos dinámicos (Ionic y Desktop)
   */
  private cleanAllStyles(): void {
    this.logger.debug('Cleaning all dynamic styles...');
    
    // Remover estilos de Ionic
    this.unloadIonicStyles();
    
    // Remover estilos de Desktop
    this.unloadDesktopStyles();
    
    // Limpiar cualquier link de estilo dinámico que pueda quedar
    const dynamicLinks = document.querySelectorAll('link[id^="ionic-dynamic-"], link[id^="desktop-dynamic-"]');
    dynamicLinks.forEach(link => link.remove());
    
    this.logger.debug('All dynamic styles cleaned');
  }

  /**
   * Muestra un overlay de loading durante la transición de estilos
   */
  private showLoadingOverlay(): void {
    if (this.loadingOverlay) return;

    this.logger.debug('Showing loading overlay');
    
    const overlay = document.createElement('div');
    overlay.id = 'platform-transition-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: #1a1a1a;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 999999;
      opacity: 0;
      transition: opacity 0.2s ease-in-out;
    `;

    const spinner = document.createElement('div');
    spinner.style.cssText = `
      width: 50px;
      height: 50px;
      border: 3px solid rgba(255, 255, 255, 0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    `;

    // Agregar animación de spin
    const style = document.createElement('style');
    style.textContent = `
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(style);

    overlay.appendChild(spinner);
    document.body.appendChild(overlay);
    this.loadingOverlay = overlay;

    // Fade in
    requestAnimationFrame(() => {
      overlay.style.opacity = '1';
    });
  }

  /**
   * Oculta el overlay de loading
   */
  private hideLoadingOverlay(): void {
    if (!this.loadingOverlay) return;

    this.logger.debug('Hiding loading overlay');
    
    const overlay = this.loadingOverlay;
    overlay.style.opacity = '0';

    setTimeout(() => {
      overlay.remove();
      this.loadingOverlay = null;
    }, 200);
  }

  /**
   * Obtiene el modo actual de forma síncrona
   */
  get currentMode(): PlatformMode {
    return this.platformModeSubject.value;
  }

  /**
   * Verifica si actualmente está en modo móvil
   */
  get isMobile(): boolean {
    return this.currentMode === 'mobile';
  }

  /**
   * Verifica si actualmente está en modo desktop
   */
  get isDesktop(): boolean {
    return this.currentMode === 'desktop';
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
    this.unloadIonicStyles();
  }
}
