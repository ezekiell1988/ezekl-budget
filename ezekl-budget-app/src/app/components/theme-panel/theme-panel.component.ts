import {
  Component,
  Output,
  EventEmitter,
  OnInit,
  ChangeDetectorRef,
} from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgScrollbarModule } from "ngx-scrollbar";
import {
  IonFab,
  IonFabButton,
  IonIcon,
  IonMenu,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonContent,
  IonList,
  IonItem,
  IonLabel,
  IonToggle,
  MenuController,
  AlertController,
} from "@ionic/angular/standalone";
import Swal from "sweetalert2";
import { addIcons } from "ionicons";
import {
  settingsOutline,
  closeOutline,
  checkmarkOutline,
  colorPaletteOutline,
  moonOutline,
  textOutline,
  refreshOutline,
} from "ionicons/icons";
import { AppVariablesService } from "../../service/app-variables.service";
import { AppSettings } from "../../service/app-settings.service";
import { MenuStateService } from "../../service/menu-state.service";
import { LoggerService } from "../../service/logger.service";
import { ResponsiveComponent } from "../../shared/responsive-component.base";

declare var bootstrap: any;

@Component({
  selector: "theme-panel",
  templateUrl: "./theme-panel.component.html",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    NgScrollbarModule,
    IonFab,
    IonFabButton,
    IonIcon,
    IonMenu,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonButtons,
    IonButton,
    IonContent,
    IonList,
    IonItem,
    IonLabel,
    IonToggle,
  ],
})
export class ThemePanelComponent extends ResponsiveComponent implements OnInit {
  @Output() appDarkModeChanged = new EventEmitter<boolean>();
  @Output() appThemeChanged = new EventEmitter<boolean>();
  appVariables = this.appVariablesService.getAppVariables();

  // Color actual del toolbar para Ionic
  toolbarColor: string = "#00acac";

  constructor(
    public appSettings: AppSettings,
    private appVariablesService: AppVariablesService,
    private menuController: MenuController,
    private alertController: AlertController,
    private cdr: ChangeDetectorRef,
    private menuStateService: MenuStateService,
    private logger: LoggerService
  ) {
    super();
    // Registrar iconos de Ionic para versión móvil
    addIcons({
      settingsOutline, // Botón flotante de configuración
      closeOutline, // Botón cerrar menú
      checkmarkOutline, // Indicador de color seleccionado
      colorPaletteOutline, // Ícono de selector de color
      moonOutline, // Ícono de modo oscuro
      textOutline, // Ícono de modo RTL
      refreshOutline, // Botón restaurar configuración
    });
  }

  // Estado del panel (web)
  active: boolean = false;

  // Estado del FAB (móvil)
  showFab: boolean = true;

  // Variables de estado de los checkboxes
  // NOTA: Aunque algunas opciones no se usan en móvil, se mantienen
  // estas variables para compatibilidad con la versión desktop (Color-Admin)
  appThemeDarkModeCheckbox: boolean = false; // Usado en móvil y desktop
  appHeaderFixedCheckbox: boolean = true; // Solo desktop
  appHeaderInverseCheckbox: boolean = false; // Solo desktop
  appSidebarFixedCheckbox: boolean = true; // Solo desktop
  appSidebarGridCheckbox: boolean = false; // Solo desktop
  appGradientEnabledCheckbox: boolean = false; // Solo desktop
  appRtlEnabledCheckbox: boolean = false; // Usado en móvil y desktop

  selectedTheme = "teal";
  themes = [
    "red",
    "pink",
    "orange",
    "yellow",
    "lime",
    "green",
    "teal",
    "cyan",
    "blue",
    "purple",
    "indigo",
    "gray-500",
  ];

  toggleThemePanel() {
    if (localStorage) {
      localStorage["appThemePanelActive"] = !this.active;
    }
    this.active = !this.active;
  }

  async openMobileSettings() {
    await this.menuController.open("settings-menu");
    this.logger.debug("Menú de configuración abierto");
  }

  async closeMobileSettings() {
    await this.menuController.close("settings-menu");
    this.logger.debug("Menú de configuración cerrado");
  }

  /**
   * Limpia todas las configuraciones del tema guardadas en localStorage
   * y recarga la aplicación para aplicar los valores por defecto
   */
  resetLocalStorage() {
    if (this.isMobile()) {
      this.resetLocalStorageMobile();
    } else {
      this.resetLocalStorageWeb();
    }
  }

  /**
   * Versión WEB: Usa SweetAlert2 para la confirmación
   */
  private resetLocalStorageWeb() {
    Swal.fire({
      title: "¿Restaurar Configuración?",
      text: "¿Estás seguro de que deseas restaurar la configuración predeterminada? Esto recargará la aplicación.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#00acac",
      cancelButtonColor: "#6c757d",
      confirmButtonText: "Sí, restaurar",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        this.clearThemeSettings();
        window.location.reload();
      }
    });
  }

  /**
   * Versión MÓVIL: Usa Ionic AlertController para la confirmación
   */
  private async resetLocalStorageMobile() {
    const alert = await this.alertController.create({
      header: "¿Restaurar Configuración?",
      message:
        "¿Estás seguro de que deseas restaurar la configuración predeterminada? Esto recargará la aplicación.",
      buttons: [
        {
          text: "Cancelar",
          role: "cancel",
          cssClass: "secondary",
        },
        {
          text: "Sí, restaurar",
          handler: () => {
            this.clearThemeSettings();
            window.location.reload();
          },
        },
      ],
    });

    await alert.present();
  }

  /**
   * Limpia todas las configuraciones del tema del localStorage
   * NOTA: Limpia todas las opciones (tanto móvil como desktop) para mantener
   * consistencia entre plataformas cuando el usuario restaura la configuración
   */
  private clearThemeSettings() {
    const keysToRemove = [
      "appTheme", // Color del tema (móvil y desktop)
      "appThemePanelActive", // Estado del panel (solo desktop)
      "appDarkMode", // Modo oscuro (móvil y desktop)
      "appHeaderFixed", // Solo desktop
      "appHeaderInverse", // Solo desktop
      "appSidebarFixed", // Solo desktop
      "appSidebarGrid", // Solo desktop
      "appGradientEnabled", // Solo desktop
      "appRtlMode", // RTL mode (no implementado actualmente)
    ];

    keysToRemove.forEach((key) => {
      localStorage.removeItem(key);
    });
  }

  ngOnInit() {
    // Escuchar cuando se abre/cierra el menú del sidebar para ocultar/mostrar el FAB
    this.menuStateService.getSidebarMenuState().subscribe((isOpen) => {
      if (isOpen) {
        this.showFab = false;
      } else {
        // Pequeño delay para evitar que el FAB capture el evento de click
        setTimeout(() => {
          this.showFab = true;
        }, 300);
      }
      this.cdr.detectChanges();
    });

    var elm = document.querySelectorAll('[data-bs-toggle="tooltip"]');

    for (var i = 0; i < elm.length; i++) {
      new bootstrap.Tooltip(elm[i]);
    }
    if (localStorage) {
      if (localStorage["appThemePanelActive"]) {
        this.active =
          localStorage["appThemePanelActive"] == "true" ? true : false;
      }
      if (localStorage["appTheme"]) {
        this.toggleTheme(localStorage["appTheme"]);
      } else if (this.isMobile()) {
        // Inicializar con el tema por defecto
        setTimeout(() => this.updateIonicThemeColors(), 100);
      }
      if (
        localStorage["appDarkMode"] &&
        localStorage["appDarkMode"] === "true"
      ) {
        this.appThemeDarkModeCheckbox = true;
        this.appSettings.appDarkMode = true; // Asegurar que el servicio tenga el valor correcto
        this.appDarkModeChanged.emit(true);
      }
      if (
        localStorage["appHeaderFixed"] &&
        localStorage["appHeaderFixed"] !== "true"
      ) {
        this.appHeaderFixedCheckbox = false;
      }
      if (
        localStorage["appHeaderInverse"] &&
        localStorage["appHeaderInverse"] === "true"
      ) {
        this.appHeaderInverseCheckbox = true;
      }
      if (
        localStorage["appSidebarFixed"] &&
        localStorage["appSidebarFixed"] !== "true"
      ) {
        this.appSidebarFixedCheckbox = false;
      }
      if (
        localStorage["appSidebarGrid"] &&
        localStorage["appSidebarGrid"] === "true"
      ) {
        this.appSidebarGridCheckbox = true;
      }
      if (
        localStorage["appGradientEnabled"] &&
        localStorage["appGradientEnabled"] === "true"
      ) {
        this.appGradientEnabledCheckbox = true;
      }
      if (localStorage["appRtlMode"] === "true") {
        this.appRtlEnabledCheckbox = true;
        document.documentElement.setAttribute("dir", "rtl");
      }
    }
  }

  toggleTheme(theme, event?: Event) {
    // Prevenir que el menú se cierre al hacer clic en el chip
    if (event) {
      event.stopPropagation();
      event.preventDefault();
    }

    this.appSettings.appTheme = theme;
    this.selectedTheme = theme;
    this.appThemeChanged.emit(true);
    if (localStorage) {
      localStorage["appTheme"] = theme;
    }

    // Actualizar variables de Ionic en móvil
    if (this.isMobile()) {
      // Esperar a que las clases CSS se apliquen y las variables se actualicen
      setTimeout(() => this.updateIonicThemeColors(), 150);
    }
  }

  /**
   * Actualiza las variables de color de Ionic leyendo desde las variables CSS del template
   */
  private updateIonicThemeColors() {
    const root = document.documentElement;
    const styles = getComputedStyle(root);

    // Leer el color del tema seleccionado desde las variables CSS
    const themeColor = styles
      .getPropertyValue(`--bs-${this.selectedTheme}`)
      .trim();

    if (themeColor && themeColor.startsWith("#")) {
      const rgb = this.hexToRgb(themeColor);

      if (rgb) {
        // Actualizar propiedad reactiva
        this.toolbarColor = themeColor;

        // Actualizar variables de Ionic
        root.style.setProperty("--ion-color-theme", themeColor);
        root.style.setProperty(
          "--ion-color-theme-rgb",
          `${rgb.r}, ${rgb.g}, ${rgb.b}`
        );

        // Calcular shade (10% más oscuro) y tint (10% más claro)
        const shade = this.adjustBrightness(themeColor, -10);
        const tint = this.adjustBrightness(themeColor, 10);

        root.style.setProperty("--ion-color-theme-shade", shade);
        root.style.setProperty("--ion-color-theme-tint", tint);

        // Forzar detección de cambios en Angular
        this.cdr.detectChanges();
      }
    }
  }

  /**
   * Convierte color hexadecimal a RGB
   */
  private hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    hex = hex.replace("#", "");
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    if (isNaN(r) || isNaN(g) || isNaN(b)) return null;
    return { r, g, b };
  }

  /**
   * Ajusta el brillo de un color hexadecimal
   */
  private adjustBrightness(hex: string, percent: number): string {
    const rgb = this.hexToRgb(hex);
    if (!rgb) return hex;

    const adjust = (value: number) => {
      const adjusted = value + (value * percent) / 100;
      return Math.min(255, Math.max(0, Math.round(adjusted)));
    };

    const r = adjust(rgb.r).toString(16).padStart(2, "0");
    const g = adjust(rgb.g).toString(16).padStart(2, "0");
    const b = adjust(rgb.b).toString(16).padStart(2, "0");

    return `#${r}${g}${b}`;
  }

  // ============================================================
  // FUNCIONES PÚBLICAS
  // toggleDarkMode y toggleRtlEnabled: Detectan plataforma y ejecutan lógica correspondiente
  // Las demás opciones solo se usan en Desktop (Color-Admin)
  // ============================================================

  toggleDarkMode(e: any) {
    if (this.isMobile()) {
      this.toggleDarkModeMobile(e);
    } else {
      this.toggleDarkModeWeb(e);
    }
  }

  toggleRtlEnabled(e: any) {
    if (this.isMobile()) {
      this.toggleRtlEnabledMobile(e);
    } else {
      this.toggleRtlEnabledWeb(e);
    }
  }

  // ============================================================
  // FUNCIONES WEB (Bootstrap)
  // ============================================================

  private toggleDarkModeWeb(e: Event) {
    const checked = (e as any).srcElement?.checked || false;
    this.appSettings.appDarkMode = checked;
    this.appDarkModeChanged.emit(true);

    if (localStorage) {
      localStorage["appDarkMode"] = checked;
    }
  }

  private toggleHeaderFixedWeb(e: Event) {
    const checked = (e as any).srcElement?.checked || false;
    this.appSettings.appHeaderFixed = checked;

    if (localStorage) {
      localStorage["appHeaderFixed"] = checked;
    }
    if (!checked && this.appSettings.appSidebarFixed === true) {
      alert(
        "La opción de Encabezado Predeterminado con Barra Lateral Fija no está soportada. Se procederá con Encabezado Predeterminado y Barra Lateral Predeterminada."
      );
      this.appSettings.appSidebarFixed = false;
      this.appSidebarFixedCheckbox = false;
      if (localStorage) {
        localStorage["appSidebarFixed"] = false;
      }
    }
  }

  private toggleHeaderInverseWeb(e: Event) {
    const checked = (e as any).srcElement?.checked || false;
    this.appSettings.appHeaderInverse = checked;
    if (localStorage) {
      localStorage["appHeaderInverse"] = checked;
    }
  }

  private toggleSidebarFixedWeb(e: Event) {
    const checked = (e as any).srcElement?.checked || false;
    this.appSettings.appSidebarFixed = checked;

    if (localStorage) {
      localStorage["appSidebarFixed"] = checked;
    }
    if (checked && this.appSettings.appHeaderFixed !== true) {
      alert(
        "La opción de Encabezado Predeterminado con Barra Lateral Fija no está soportada. Se procederá con Encabezado Fijo y Barra Lateral Fija."
      );
      this.appSettings.appHeaderFixed = true;
      this.appHeaderFixedCheckbox = true;
      if (localStorage) {
        localStorage["appHeaderFixed"] = true;
      }
    }
  }

  private toggleSidebarGridWeb(e: Event) {
    const checked = (e as any).srcElement?.checked || false;
    this.appSettings.appSidebarGrid = checked;
    if (localStorage) {
      localStorage["appSidebarGrid"] = checked;
    }
  }

  private toggleGradientEnabledWeb(e: Event) {
    const checked = (e as any).srcElement?.checked || false;
    this.appSettings.appGradientEnabled = checked;
    if (localStorage) {
      localStorage["appGradientEnabled"] = checked;
    }
  }

  private toggleRtlEnabledWeb(e: Event) {
    const isRtl = (e as any).srcElement?.checked || false;
    if (isRtl) {
      document.documentElement.setAttribute("dir", "rtl");
    } else {
      document.documentElement.removeAttribute("dir");
    }
    if (localStorage) {
      localStorage.setItem("appRtlMode", isRtl.toString());
    }
  }

  // ============================================================
  // FUNCIONES MOBILE (Ionic)
  // Incluye toggleDarkMode y toggleRtlEnabled que son relevantes
  // para la interfaz móvil de Ionic
  // ============================================================

  private toggleDarkModeMobile(e: any) {
    const checked = e.detail?.checked || false;
    this.appSettings.appDarkMode = checked;
    this.appDarkModeChanged.emit(true);

    // Ionic dark mode: solo clase .dark en body
    if (checked) {
      document.body.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
    }

    if (localStorage) {
      localStorage["appDarkMode"] = checked;
    }
  }

  private toggleRtlEnabledMobile(e: any) {
    const isRtl = e.detail?.checked || false;

    // Actualizar dirección del documento
    if (isRtl) {
      document.documentElement.setAttribute("dir", "rtl");
    } else {
      document.documentElement.removeAttribute("dir");
    }

    if (localStorage) {
      localStorage.setItem("appRtlMode", isRtl.toString());
    }
  }
}
