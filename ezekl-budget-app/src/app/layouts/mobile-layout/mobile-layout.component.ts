import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { 
  IonApp,
  IonRouterOutlet
} from '@ionic/angular/standalone';
import { SidebarComponent, ThemePanelComponent } from '../../components';
import { AppSettings, AppVariablesService, LoggerService } from '../../service';

@Component({
  selector: 'app-mobile-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    IonApp,
    IonRouterOutlet,
    SidebarComponent,
    ThemePanelComponent
  ],
  templateUrl: './mobile-layout.component.html',
  styleUrls: ['./mobile-layout.component.scss']
})
export class MobileLayoutComponent implements OnInit {
  pageTitle = 'Ezekl Budget';
  appVariables: any;
  private readonly logger = inject(LoggerService).getLogger('MobileLayout');

  constructor(
    private router: Router,
    public appSettings: AppSettings,
    private appVariablesService: AppVariablesService
  ) {
    this.appVariables = this.appVariablesService.getAppVariables();
  }

  ngOnInit() {
    this.logger.debug('ngOnInit - appDarkMode:', this.appSettings.appDarkMode);
    this.logger.debug('documentElement classes before:', document.documentElement.className);
    
    // Aplicar dark mode inicial si está activado (Ionic)
    // Ionic requiere la clase .ion-palette-dark en el elemento html
    // También sincronizar con desktop usando data-bs-theme
    if (this.appSettings.appDarkMode) {
      document.documentElement.classList.add('ion-palette-dark');
      document.documentElement.setAttribute('data-bs-theme', 'dark');
      this.logger.debug('Dark mode aplicado');
    }
    
    this.logger.debug('documentElement classes after:', document.documentElement.className);
    this.logger.debug('Computed --ion-background-color:', getComputedStyle(document.documentElement).getPropertyValue('--ion-background-color'));
    
    // Actualizar título según la ruta
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.updatePageTitle();
    });
    
    // Establecer título inicial
    this.updatePageTitle();
  }

  private updatePageTitle() {
    const url = this.router.url;
    if (url.includes('/login')) {
      this.pageTitle = 'Iniciar Sesión';
    } else if (url.includes('/home')) {
      this.pageTitle = this.appSettings.nameCompany || 'Ezekl Budget';
    } else if (url.includes('/dashboard')) {
      this.pageTitle = 'Dashboard';
    } else if (url.includes('/users')) {
      this.pageTitle = 'Usuarios';
    } else {
      this.pageTitle = this.appSettings.nameCompany || 'Ezekl Budget';
    }
  }

  onAppDarkModeChanged(val: boolean): void {
    this.logger.debug('onAppDarkModeChanged - val:', val, '- appDarkMode:', this.appSettings.appDarkMode);
    
    // Ionic dark mode: clase .ion-palette-dark en html (documentElement)
    // Según documentación: https://ionicframework.com/docs/theming/dark-mode
    // También sincronizar con desktop agregando data-bs-theme para compatibilidad
    if (this.appSettings.appDarkMode) {
      document.documentElement.classList.add('ion-palette-dark');
      document.documentElement.setAttribute('data-bs-theme', 'dark');
      this.logger.debug('Dark mode activado - classes:', document.documentElement.className);
    } else {
      document.documentElement.classList.remove('ion-palette-dark');
      document.documentElement.removeAttribute('data-bs-theme');
      this.logger.debug('Dark mode desactivado');
    }
    
    this.appVariables = this.appVariablesService.getAppVariables();
    this.appVariablesService.variablesReload.emit();
    document.dispatchEvent(new CustomEvent('theme-change'));
  }

  onAppThemeChanged(val: boolean): void {
    const newTheme = 'theme-' + this.appSettings.appTheme;
    for (let x = 0; x < document.body.classList.length; x++) {
      if ((document.body.classList[x]).indexOf('theme-') > -1 && document.body.classList[x] !== newTheme) {
        document.body.classList.remove(document.body.classList[x]);
      }
    }
    document.body.classList.add(newTheme);
    this.appVariables = this.appVariablesService.getAppVariables();
    this.appVariablesService.variablesReload.emit();
  }
}
