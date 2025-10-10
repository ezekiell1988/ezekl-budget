import { Component, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonMenuButton,
  IonButtons,
  IonButton,
  IonIcon,
  IonSearchbar,
  MenuController,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { menu, notifications, search, ellipsisVertical, close } from 'ionicons/icons';

@Component({
  selector: 'app-header',
  templateUrl: './app-header.component.html',
  styleUrls: ['./app-header.component.scss'],
  imports: [
    CommonModule,
    FormsModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonMenuButton,
    IonButtons,
    IonButton,
    IonIcon,
    IonSearchbar,
  ],
})
export class AppHeaderComponent {
  @Input() title: string = 'Ezekl Budget';
  @Input() showMenu: boolean = true;
  @Input() showActions: boolean = false;
  @Input() color: string = 'primary';
  @Input() showSearch: boolean = false; // Nueva propiedad para controlar si se muestra el search
  @Input() searchPlaceholder: string = 'Buscar...';

  @Output() searchChange = new EventEmitter<string>();
  @Output() searchToggle = new EventEmitter<boolean>();
  @Output() notificationsClick = new EventEmitter<void>();
  @Output() moreClick = new EventEmitter<void>();

  @ViewChild(IonSearchbar) searchbar!: IonSearchbar;

  searchText: string = '';
  isSearchActive: boolean = false;

  constructor(private menuController: MenuController) {
    // Registrar iconos necesarios
    addIcons({
      menu,
      notifications,
      search,
      ellipsisVertical,
      close,
    });
  }

  /**
   * Abrir el menú lateral
   */
  async openMenu() {
    await this.menuController.open('main-menu');
  }

  /**
   * Toggle del modo búsqueda
   */
  onSearchClick() {
    this.isSearchActive = !this.isSearchActive;
    this.searchToggle.emit(this.isSearchActive);

    // Limpiar búsqueda al cerrar
    if (!this.isSearchActive) {
      this.searchText = '';
      this.searchChange.emit('');
    } else {
      // Dar foco al searchbar cuando se abre
      setTimeout(() => {
        this.searchbar?.setFocus();
      }, 100);
    }
  }

  /**
   * Evento cuando cambia el texto de búsqueda
   */
  onSearchInput(event: any) {
    this.searchText = event.target.value || '';
    this.searchChange.emit(this.searchText);
  }

  /**
   * Limpiar búsqueda
   */
  onSearchClear() {
    this.searchText = '';
    this.searchChange.emit('');
  }

  /**
   * Notificaciones
   */
  onNotificationsClick() {
    this.notificationsClick.emit();
  }

  /**
   * Menú contextual
   */
  onMoreClick() {
    this.moreClick.emit();
  }
}
