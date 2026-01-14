import { Component, HostListener, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, NavigationStart } from '@angular/router';
import { AppSettings } from '../../service/app-settings.service';
import { AppVariablesService } from '../../service/app-variables.service';
import { HeaderComponent } from '../../components/header/header.component';
import { SidebarComponent } from '../../components/sidebar/sidebar.component';
import { SidebarRightComponent } from '../../components/sidebar-right/sidebar-right.component';
import { TopMenuComponent } from '../../components/top-menu/top-menu.component';
import { ThemePanelComponent } from '../../components/theme-panel/theme-panel.component';

@Component({
  selector: 'app-desktop-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    HeaderComponent,
    SidebarComponent,
    SidebarRightComponent,
    TopMenuComponent,
    ThemePanelComponent
  ],
  templateUrl: './desktop-layout.component.html',
  styleUrls: ['./desktop-layout.component.scss']
})
export class DesktopLayoutComponent implements OnInit {
  appHasScroll = false;
  hasScrolled = false;
  appVariables;

  constructor(
    private router: Router,
    public appSettings: AppSettings,
    private appVariablesService: AppVariablesService
  ) {
    // Manejar toggle de sidebar en navegación (mobile)
    this.router.events.subscribe((e) => {
      if (e instanceof NavigationStart) {
        if (window.innerWidth < 768) {
          this.appSettings.appSidebarMobileToggled = false;
          this.appSettings.appSidebarEndMobileToggled = false;
        }
      }
    });

    this.appVariables = this.appVariablesService.getAppVariables();
  }

  ngOnInit() {
    // Configuración de tema oscuro
    if (this.appSettings.appDarkMode) {
      this.onAppDarkModeChanged(true);
    }

    // Cargar configuraciones desde localStorage
    if (localStorage) {
      if (localStorage["appDarkMode"]) {
        this.appSettings.appDarkMode = localStorage["appDarkMode"] === "true";
        if (this.appSettings.appDarkMode) {
          this.onAppDarkModeChanged(true);
        }
      }
      if (localStorage["appHeaderFixed"]) {
        this.appSettings.appHeaderFixed = localStorage["appHeaderFixed"] === "true";
      }
      if (localStorage["appHeaderInverse"]) {
        this.appSettings.appHeaderInverse = localStorage["appHeaderInverse"] === "true";
      }
      if (localStorage["appSidebarFixed"]) {
        this.appSettings.appSidebarFixed = localStorage["appSidebarFixed"] === "true";
      }
      if (localStorage["appSidebarMinified"]) {
        this.appSettings.appSidebarMinified = localStorage["appSidebarMinified"] === "true";
      }
      if (localStorage["appSidebarGrid"]) {
        this.appSettings.appSidebarGrid = localStorage["appSidebarGrid"] === "true";
      }
      if (localStorage["appGradientEnabled"]) {
        this.appSettings.appGradientEnabled = localStorage["appGradientEnabled"] === "true";
      }
    }
  }

  @HostListener("window:scroll")
  onWindowScroll() {
    const doc = document.documentElement;
    const top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
    if (top > 0 && this.appSettings.appHeaderFixed) {
      this.appHasScroll = true;
    } else {
      this.appHasScroll = false;
    }
    this.hasScrolled = top > 0;
  }

  onAppSidebarMinifiedToggled(val: boolean) {
    this.appSettings.appSidebarMinified = val;
    if (localStorage) {
      localStorage["appSidebarMinified"] = val.toString();
    }
  }

  onAppSidebarMobileToggled(val: boolean) {
    this.appSettings.appSidebarMobileToggled = val;
  }

  onAppSidebarEndToggled(val: boolean) {
    this.appSettings.appSidebarEndToggled = val;
  }

  onAppSidebarEndMobileToggled(val: boolean) {
    this.appSettings.appSidebarEndMobileToggled = val;
  }

  onAppDarkModeChanged(val: boolean) {
    // Bootstrap/Color-Admin dark mode: data-bs-theme="dark"
    // También sincronizar con Ionic agregando .ion-palette-dark para compatibilidad
    if (this.appSettings.appDarkMode) {
      document.documentElement.setAttribute("data-bs-theme", "dark");
      document.documentElement.classList.add("ion-palette-dark");
    } else {
      document.documentElement.removeAttribute("data-bs-theme");
      document.documentElement.classList.remove("ion-palette-dark");
    }
    this.appVariables = this.appVariablesService.getAppVariables();
    this.appVariablesService.variablesReload.emit();
    document.dispatchEvent(new CustomEvent("theme-change"));
  }

  onAppThemeChanged(val: string) {
    const newTheme = "theme-" + this.appSettings.appTheme;
    for (let x = 0; x < document.body.classList.length; x++) {
      if (
        document.body.classList[x].indexOf("theme-") > -1 &&
        document.body.classList[x] !== newTheme
      ) {
        document.body.classList.remove(document.body.classList[x]);
      }
    }
    document.body.classList.add(newTheme);
    this.appVariables = this.appVariablesService.getAppVariables();
    this.appVariablesService.variablesReload.emit();
  }

  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}
