import { Injectable, OnDestroy } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { BehaviorSubject, Observable, Subscription } from 'rxjs';
import { distinctUntilChanged, map } from 'rxjs/operators';

export type PlatformMode = 'mobile' | 'desktop';

@Injectable({
  providedIn: 'root'
})
export class PlatformDetectorService implements OnDestroy {
  private readonly MOBILE_BREAKPOINT = '(max-width: 768px)';
  
  private platformModeSubject = new BehaviorSubject<PlatformMode>('desktop');
  private ionicStylesLoaded = false;
  private ionicStyleElement: HTMLStyleElement | null = null;
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

  constructor(private breakpointObserver: BreakpointObserver) {
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

    // Crear elemento style inline en lugar de cargar archivo externo
    this.ionicStyleElement = document.createElement('style');
    this.ionicStyleElement.id = 'ionic-dynamic-styles';
    this.ionicStyleElement.textContent = this.getIonicStyles();
    
    document.head.appendChild(this.ionicStyleElement);
    this.ionicStylesLoaded = true;
    
    console.log('[PlatformDetector] Ionic styles loaded');
  }

  /**
   * Retorna los estilos de Ionic como string
   */
  private getIonicStyles(): string {
    return `
      /* Ionic Mobile Styles - Cargado dinámicamente */
      
      /* Ocultar elementos de Color-Admin en modo móvil */
      body.ionic-mode #header.app-header,
      body.ionic-mode #sidebar.app-sidebar,
      body.ionic-mode .app-sidebar-end,
      body.ionic-mode .theme-panel,
      body.ionic-mode .top-menu,
      body.ionic-mode .float-sub-menu-container {
        display: none !important;
      }

      body.ionic-mode #app,
      body.ionic-mode #content.app-content {
        display: none !important;
      }

      body.ionic-mode {
        overflow: hidden;
        margin: 0;
        padding: 0;
      }

      body.ionic-mode .ionic-only {
        display: block !important;
      }

      body.ionic-mode .desktop-only {
        display: none !important;
      }

      body.ionic-mode ion-app {
        display: block !important;
        width: 100%;
        height: 100vh;
        position: fixed;
        top: 0;
        left: 0;
      }

      body.ionic-mode ion-content {
        --padding-start: 0;
        --padding-end: 0;
        --padding-top: 0;
        --padding-bottom: 0;
        --background: var(--ion-background-color);
      }
      
      body.ionic-mode .ion-padding {
        padding: 16px;
      }

      /* Variables de tema para Ionic */
      body.ionic-mode {
        --ion-background-color: var(--bs-body-bg, #ffffff);
        --ion-text-color: var(--bs-body-color, #212529);
        --ion-font-family: var(--bs-font-sans-serif, system-ui, -apple-system, sans-serif);
        --ion-color-primary: var(--app-theme, #348fe2);
        --ion-color-primary-rgb: 52, 143, 226;
        --ion-color-primary-contrast: #ffffff;
        --ion-color-primary-shade: #2e7ec7;
        --ion-color-primary-tint: #489ae5;
      }

      /* Componentes de Ionic */
      body.ionic-mode ion-toolbar {
        --background: var(--app-theme, #348fe2);
        --color: #ffffff;
      }

      body.ionic-mode ion-title {
        font-weight: 600;
      }

      body.ionic-mode ion-tab-bar {
        --background: var(--bs-body-bg, #ffffff);
        border-top: 1px solid var(--bs-border-color, #dee2e6);
      }

      body.ionic-mode ion-tab-button {
        --color: var(--bs-secondary-color, #6c757d);
        --color-selected: var(--app-theme, #348fe2);
      }

      body.ionic-mode ion-menu {
        --background: var(--bs-body-bg, #ffffff);
      }

      body.ionic-mode ion-menu ion-content {
        --background: var(--bs-body-bg, #ffffff);
      }

      body.ionic-mode ion-item {
        --background: transparent;
        --color: var(--bs-body-color, #212529);
        --border-color: var(--bs-border-color, #dee2e6);
      }

      body.ionic-mode ion-card {
        --background: var(--bs-body-bg, #ffffff);
        border-radius: 0.375rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        margin: 16px;
      }

      body.ionic-mode ion-card-header {
        padding: 1rem;
      }

      body.ionic-mode ion-card-content {
        padding: 1rem;
      }

      body.ionic-mode ion-list {
        --background: transparent;
      }

      body.ionic-mode ion-button {
        --border-radius: 0.375rem;
        font-weight: 500;
      }

      body.ionic-mode ion-input,
      body.ionic-mode ion-textarea,
      body.ionic-mode ion-select {
        --background: var(--bs-body-bg, #ffffff);
        --color: var(--bs-body-color, #212529);
        --placeholder-color: var(--bs-secondary-color, #6c757d);
      }

      body.ionic-mode ion-fab-button {
        --background: var(--app-theme, #348fe2);
        --color: #ffffff;
      }

      body.ionic-mode ion-spinner {
        --color: var(--app-theme, #348fe2);
      }

      body.ionic-mode ion-badge {
        --background: var(--app-theme, #348fe2);
        --color: #ffffff;
      }

      /* Estilos personalizados para la app */
      body.ionic-mode .balance-card {
        background: linear-gradient(135deg, var(--app-theme, #348fe2), #1e5aa8);
        color: white;
      }

      body.ionic-mode .balance-card ion-card-header {
        color: white;
      }

      body.ionic-mode .balance-card ion-card-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
      }

      body.ionic-mode .balance-card ion-card-content {
        color: white;
      }

      body.ionic-mode .balance-amount {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 16px;
      }

      body.ionic-mode .balance-details {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      body.ionic-mode .balance-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9rem;
        opacity: 0.9;
      }

      body.ionic-mode .balance-item ion-icon {
        font-size: 1.2rem;
      }

      body.ionic-mode .balance-item.income ion-icon {
        color: #4ade80 !important;
      }

      body.ionic-mode .balance-item.expense ion-icon {
        color: #f87171 !important;
      }

      /* Dark mode */
      body.ionic-mode[data-bs-theme="dark"] {
        --ion-background-color: var(--bs-body-bg, #212529);
        --ion-text-color: var(--bs-body-color, #dee2e6);
      }

      body.ionic-mode[data-bs-theme="dark"] ion-toolbar {
        --background: var(--bs-dark, #1a1d20);
      }

      body.ionic-mode[data-bs-theme="dark"] ion-tab-bar {
        --background: var(--bs-dark, #1a1d20);
        border-top-color: var(--bs-border-color, #495057);
      }

      body.ionic-mode[data-bs-theme="dark"] ion-card {
        --background: var(--bs-dark, #2b2f32);
      }

      body.ionic-mode[data-bs-theme="dark"] .balance-card {
        background: linear-gradient(135deg, #1e3a5f, #0f1f33);
      }
    `;
  }

  /**
   * Descarga los estilos de Ionic
   */
  private unloadIonicStyles(): void {
    if (!this.ionicStylesLoaded || !this.ionicStyleElement) return;

    this.ionicStyleElement.remove();
    this.ionicStyleElement = null;
    this.ionicStylesLoaded = false;
    
    console.log('[PlatformDetector] Ionic styles unloaded');
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
