import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  // IonHeader, IonToolbar, IonTitle no usados
  IonContent,
  IonGrid,
  // IonRow, IonCol no usados
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonIcon,
  ViewWillLeave,
  ViewDidLeave
} from '@ionic/angular/standalone';
import { RouterModule } from '@angular/router';
import { addIcons } from 'ionicons';
import { homeOutline } from 'ionicons/icons';

import { AppHeaderComponent } from '../shared/components/app-header/app-header.component';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  imports: [
    CommonModule,
    RouterModule,
    // IonHeader, IonToolbar, IonTitle no usados - usa AppHeaderComponent
    IonContent,
    IonGrid,
    // IonRow, IonCol no usados
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonIcon,
    AppHeaderComponent,
  ],
})
export class HomePage implements OnInit, ViewWillLeave, ViewDidLeave {

  constructor() {
    // Registrar iconos necesarios
    addIcons({
      homeOutline,
    });
  }

  ngOnInit() {
  }

  /**
   * Ionic lifecycle: Antes de salir de la vista
   * Quita el focus de cualquier elemento para evitar conflictos aria-hidden
   */
  ionViewWillLeave() {
    // Quitar focus de cualquier elemento activo
    const activeElement = document.activeElement as HTMLElement;
    if (activeElement && activeElement.blur) {
      activeElement.blur();
    }
  }

  /**
   * Ionic lifecycle: Después de salir de la vista
   * Limpieza adicional si es necesaria
   */
  ionViewDidLeave() {
    // Limpieza adicional si es necesaria
  }

}
