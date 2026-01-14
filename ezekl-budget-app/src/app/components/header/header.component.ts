import {
  Component,
  Input,
  Output,
  EventEmitter,
  Renderer2,
  OnInit,
  OnDestroy,
  ChangeDetectorRef,
  effect,
} from "@angular/core";
import { CommonModule } from "@angular/common";
import { 
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonMenuButton,
  IonButton,
  IonIcon
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { notificationsOutline, menuOutline } from 'ionicons/icons';
import { AppSettings } from "../../service/app-settings.service";
import { AuthService, LoggerService, Logger } from '../../service';
import { ResponsiveComponent } from '../../shared/responsive-component.base';

declare var slideToggle: any;

@Component({
  selector: "header",
  templateUrl: "./header.component.html",
  standalone: true,
  imports: [
    CommonModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonButtons,
    IonMenuButton,
    IonButton,
    IonIcon
  ],
})
export class HeaderComponent extends ResponsiveComponent implements OnInit, OnDestroy {
  private readonly logger: Logger;
  
  @Input() appSidebarTwo;
  @Input() pageTitle = 'Ezekl Budget'; // Para versión móvil
  @Input() color = 'theme'; // Color del toolbar para versión móvil
  @Output() appSidebarEndToggled = new EventEmitter<boolean>();
  @Output() appSidebarMobileToggled = new EventEmitter<boolean>();
  @Output() appSidebarEndMobileToggled = new EventEmitter<boolean>();
  
  currentUser: any = null;

  toggleAppSidebarMobile() {
    this.appSidebarMobileToggled.emit(true);
  }

  toggleAppSidebarEnd() {
    this.appSidebarEndToggled.emit(true);
  }

  toggleAppSidebarEndMobile() {
    this.appSidebarEndMobileToggled.emit(true);
  }

  toggleAppTopMenuMobile() {
    var target = document.querySelector(".app-top-menu");
    if (target) {
      slideToggle(target);
    }
  }

  toggleAppHeaderMegaMenuMobile() {
    this.appSettings.appHeaderMegaMenuMobileToggled =
      !this.appSettings.appHeaderMegaMenuMobileToggled;
  }

  isAuthenticated(): boolean {
    return this.authService.isAuthenticated();
  }

  logout(): void {
    this.authService.logout().subscribe({
      next: () => {
        this.logger.success('Sesión cerrada exitosamente');
      },
      error: (error) => {
        this.logger.error('Error al cerrar sesión:', error);
        this.authService.clearSession();
      }
    });
  }

  override ngOnDestroy() {
    this.appSettings.appHeaderMegaMenuMobileToggled = false;
    super.ngOnDestroy();
  }

  ngOnInit() {
    // La inicialización del effect se hace en el constructor
  }

  constructor(
    private renderer: Renderer2, 
    public appSettings: AppSettings,
    private authService: AuthService,
    private cdr: ChangeDetectorRef,
    loggerService: LoggerService
  ) {
    super();
    this.logger = loggerService.getLogger('HeaderComponent');
    
    // Registrar íconos de Ionicons para el header móvil
    addIcons({
      notificationsOutline,
      menuOutline
    });
    
    // Escuchar cambios en el usuario autenticado usando effect
    effect(() => {
      this.currentUser = this.authService.currentUser();
      // Forzar detección de cambios
      this.cdr.detectChanges();
    });
  }
}
