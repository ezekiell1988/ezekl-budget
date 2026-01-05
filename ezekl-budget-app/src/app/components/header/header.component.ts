import {
  Component,
  Input,
  Output,
  EventEmitter,
  Renderer2,
  OnDestroy,
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
export class HeaderComponent extends ResponsiveComponent implements OnDestroy {
  @Input() appSidebarTwo;
  @Input() pageTitle = 'EzekL Budget'; // Para versión móvil
  @Output() appSidebarEndToggled = new EventEmitter<boolean>();
  @Output() appSidebarMobileToggled = new EventEmitter<boolean>();
  @Output() appSidebarEndMobileToggled = new EventEmitter<boolean>();

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

  override ngOnDestroy() {
    this.appSettings.appHeaderMegaMenuMobileToggled = false;
    super.ngOnDestroy();
  }

  constructor(private renderer: Renderer2, public appSettings: AppSettings) {
    super();
    
    // Registrar íconos de Ionicons para el header móvil
    addIcons({
      notificationsOutline,
      menuOutline
    });
  }
}
