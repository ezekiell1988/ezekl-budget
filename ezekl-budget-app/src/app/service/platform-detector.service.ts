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
  private ionicStyleElement: HTMLLinkElement | null = null;
  private subscription: Subscription;

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
    // Cargar estilos inmediatamente si el modo inicial es móvil
    const initialMode = this.getInitialMode();
    if (initialMode === 'mobile') {
      this.updateBodyClasses('mobile');
      this.loadIonicStyles();
    } else {
      this.updateBodyClasses('desktop');
      // En desktop, marcar estilos como listos inmediatamente
      this.appSettings.stylesLoaded = true;
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
      this.platformModeSubject.next(mode);
      this.updateBodyClasses(mode);
      this.handleStylesChange(mode);
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
    if (mode === 'mobile') {
      this.loadIonicStyles();
    } else {
      this.unloadIonicStyles();
    }
  }

  /**
   * Carga dinámicamente los estilos de Ionic
   */
  private loadIonicStyles(): void {
    if (this.ionicStylesLoaded) return;

    // Cargar archivo CSS externo en lugar de inline styles
    this.ionicStyleElement = document.createElement('link');
    this.ionicStyleElement.id = 'ionic-dynamic-styles';
    this.ionicStyleElement.rel = 'stylesheet';
    this.ionicStyleElement.href = 'assets/css/ionic-mobile.css';
    
    // Esperar a que el CSS se cargue completamente
    this.ionicStyleElement.onload = () => {
      this.appSettings.stylesLoaded = true;
    };
    
    this.ionicStyleElement.onerror = () => {
      this.logger.error('Error al cargar estilos de Ionic');
      this.appSettings.stylesLoaded = true; // Marcar como listo para no bloquear
    };
    
    document.head.appendChild(this.ionicStyleElement);
    this.ionicStylesLoaded = true;
  }

  /**
   * Descarga los estilos de Ionic
   */
  private unloadIonicStyles(): void {
    if (!this.ionicStylesLoaded || !this.ionicStyleElement) return;

    this.ionicStyleElement.remove();
    this.ionicStyleElement = null;
    this.ionicStylesLoaded = false;
    
    this.logger.debug('Ionic styles unloaded');
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
