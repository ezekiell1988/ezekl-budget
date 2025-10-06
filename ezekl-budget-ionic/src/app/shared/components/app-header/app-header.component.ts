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
} from '@ionic/angular/standalone';


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
  ],
})
export class AppHeaderComponent {
  @Input() title: string = 'Ezekl Budget';
  @Input() showLogout: boolean = true;

  // El header ahora solo muestra título y botón de menú
  // El logout se maneja completamente desde el side-menu
}
