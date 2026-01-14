import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { 
  IonApp,
  IonRouterOutlet
} from '@ionic/angular/standalone';
import { SidebarComponent, ThemePanelComponent } from '../../components';
import { AppSettings, AppVariablesService } from '../../service';

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

  constructor(
    private router: Router,
    public appSettings: AppSettings,
    private appVariablesService: AppVariablesService
  ) {
    this.appVariables = this.appVariablesService.getAppVariables();
  }

  ngOnInit() {
    // Aplicar dark mode inicial si está activado (Ionic)
    if (this.appSettings.appDarkMode) {
      document.body.classList.add('dark');
    }
    
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
    // Ionic dark mode: solo clase .dark en body
    if (this.appSettings.appDarkMode) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
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
