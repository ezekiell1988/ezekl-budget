import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  IonTabs,
  IonTabBar,
  IonTabButton,
  IonIcon,
  IonLabel,
  IonGrid,
  IonRow,
  IonCol,
  ViewWillLeave,
  ViewDidLeave
} from '@ionic/angular/standalone';
import { RouterModule, RouterOutlet } from '@angular/router';
// Los iconos se importan y registran globalmente en main.ts



@Component({
  selector: 'app-crm',
  templateUrl: './crm.page.html',
  styleUrls: ['./crm.page.scss'],
  imports: [
    CommonModule,
    RouterModule,
    RouterOutlet,
    IonTabs,
    IonTabBar,
    IonTabButton,
    IonIcon,
    IonLabel,
    IonGrid,
    IonRow,
    IonCol
  ]
})
export class CrmPage implements OnInit, ViewWillLeave, ViewDidLeave {

  constructor() {
    // Los iconos se registran globalmente en main.ts
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
