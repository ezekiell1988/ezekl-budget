import { Component, HostListener, OnInit, OnDestroy, signal, computed } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { Router, NavigationStart } from "@angular/router";
import { Subscription } from "rxjs";
import { AppVariablesService } from "./service/app-variables.service";
import { AppSettings } from "./service/app-settings.service";
import { PlatformDetectorService, PlatformMode } from "./service/platform-detector.service";
import { HeaderComponent } from "./components/header/header.component";
import { SidebarComponent } from "./components/sidebar/sidebar.component";
import { SidebarRightComponent } from "./components/sidebar-right/sidebar-right.component";
import { TopMenuComponent } from "./components/top-menu/top-menu.component";
import { ThemePanelComponent } from "./components/theme-panel/theme-panel.component";
import { MobileLayoutComponent } from "./layouts/mobile-layout/mobile-layout.component";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    HeaderComponent,
    SidebarComponent,
    SidebarRightComponent,
    TopMenuComponent,
    ThemePanelComponent,
    MobileLayoutComponent,
  ],
})
export class AppComponent implements OnInit, OnDestroy {
  // Signals para manejo reactivo del modo de plataforma
  platformMode = signal<PlatformMode>('desktop');
  isMobile = computed(() => this.platformMode() === 'mobile');
  isDesktop = computed(() => this.platformMode() === 'desktop');
  
  private platformSubscription: Subscription | null = null;

  constructor(
    router: Router,
    public appSettings: AppSettings,
    private appVariablesService: AppVariablesService,
    private platformDetector: PlatformDetectorService
  ) {
    router.events.subscribe((e) => {
      if (e instanceof NavigationStart) {
        if (window.innerWidth < 768) {
          this.appSettings.appSidebarMobileToggled = false;
          this.appSettings.appSidebarEndMobileToggled = false;
        }
      }
    });
  }

  // window scroll
  appHasScroll;

  appVariables = this.appVariablesService.getAppVariables();

  ngOnInit() {
    // Suscribirse a cambios de modo de plataforma
    this.platformSubscription = this.platformDetector.platformMode$.subscribe(mode => {
      this.platformMode.set(mode);
    });
    
    // page settings
    if (this.appSettings.appDarkMode) {
      this.onAppDarkModeChanged(true);
    }

    if (localStorage) {
      if (localStorage["appDarkMode"]) {
        this.appSettings.appDarkMode =
          localStorage["appDarkMode"] === "true" ? true : false;
        if (this.appSettings.appDarkMode) {
          this.onAppDarkModeChanged(true);
        }
      }
      if (localStorage["appHeaderFixed"]) {
        this.appSettings.appHeaderFixed =
          localStorage["appHeaderFixed"] === "true" ? true : false;
      }
      if (localStorage["appHeaderInverse"]) {
        this.appSettings.appHeaderInverse =
          localStorage["appHeaderInverse"] === "true" ? true : false;
      }
      if (localStorage["appSidebarFixed"]) {
        this.appSettings.appSidebarFixed =
          localStorage["appSidebarFixed"] === "true" ? true : false;
      }
      if (localStorage["appSidebarMinified"]) {
        this.appSettings.appSidebarMinified =
          localStorage["appSidebarMinified"] === "true" ? true : false;
      }
      if (localStorage["appSidebarGrid"]) {
        this.appSettings.appSidebarGrid =
          localStorage["appSidebarGrid"] === "true" ? true : false;
      }
      if (localStorage["appGradientEnabled"]) {
        this.appSettings.appGradientEnabled =
          localStorage["appGradientEnabled"] === "true" ? true : false;
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
  }

  // set page minified
  onAppSidebarMinifiedToggled(): void {
    this.appSettings.appSidebarMinified = !this.appSettings.appSidebarMinified;
    if (localStorage) {
      localStorage["appSidebarMinified"] = this.appSettings.appSidebarMinified;
    }
  }

  // set app sidebar end toggled
  onAppSidebarEndToggled(): void {
    this.appSettings.appSidebarEndToggled =
      !this.appSettings.appSidebarEndToggled;
  }

  // hide mobile sidebar
  onAppSidebarMobileToggled(): void {
    this.appSettings.appSidebarMobileToggled =
      !this.appSettings.appSidebarMobileToggled;
  }

  // toggle right mobile sidebar
  onAppSidebarEndMobileToggled(): void {
    this.appSettings.appSidebarEndMobileToggled =
      !this.appSettings.appSidebarEndMobileToggled;
  }

  onAppDarkModeChanged(val: boolean): void {
    if (this.appSettings.appDarkMode) {
      document.documentElement.setAttribute("data-bs-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-bs-theme");
    }
    this.appVariables = this.appVariablesService.getAppVariables();
    this.appVariablesService.variablesReload.emit();
    document.dispatchEvent(new CustomEvent("theme-change"));
  }

  onAppThemeChanged(): void {
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

  ngOnDestroy(): void {
    if (this.platformSubscription) {
      this.platformSubscription.unsubscribe();
    }
  }
}
