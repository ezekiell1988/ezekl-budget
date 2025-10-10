import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonMenuButton,
  IonGrid,
  IonRow,
  IonCol,
  IonButtons,
  IonButton,
  IonIcon,
  MenuController,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { menu, notifications, search, ellipsisVertical } from 'ionicons/icons';

@Component({
  selector: 'app-header',
  templateUrl: './app-header.component.html',
  styleUrls: ['./app-header.component.scss'],
  imports: [
    CommonModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonMenuButton,
    IonGrid,
    IonRow,
    IonCol,
    IonButtons,
    IonButton,
    IonIcon,
  ],
})
export class AppHeaderComponent {
  @Input() title: string = 'Ezekl Budget';
  @Input() showMenu: boolean = true;
  @Input() showActions: boolean = false;
  @Input() color: string = 'primary';

  constructor(private menuController: MenuController) {
    // Registrar iconos necesarios
    addIcons({
      menu,
      notifications,
      search,
      ellipsisVertical,
    });
  }

  /**
   * Abrir el menú lateral
   */
  async openMenu() {
    await this.menuController.open('main-menu');
  }

  /**
   * Acciones adicionales del header
   */
  onSearchClick() {
    // Implementar búsqueda global
    console.log('Búsqueda global');
  }

  onNotificationsClick() {
    // Implementar notificaciones
    console.log('Mostrar notificaciones');
  }

  onMoreClick() {
    // Implementar menú contextual
    console.log('Más opciones');
  }
}
