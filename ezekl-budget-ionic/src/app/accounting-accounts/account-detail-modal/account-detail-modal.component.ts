/**
 * Componente Modal para mostrar detalles de una cuenta contable
 */

import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonIcon,
  IonContent,
  IonList,
  IonItem,
  IonLabel,
  IonNote,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  ModalController
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { close } from 'ionicons/icons';
import { AccountingAccount } from '../../services/accounting-account';

@Component({
  selector: 'app-account-detail-modal',
  templateUrl: './account-detail-modal.component.html',
  styleUrls: ['./account-detail-modal.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonButtons,
    IonButton,
    IonIcon,
    IonContent,
    IonList,
    IonItem,
    IonLabel,
    IonNote,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent
  ]
})
export class AccountDetailModalComponent {
  @Input() account!: AccountingAccount;

  constructor(private modalCtrl: ModalController) {
    // Registrar iconos
    addIcons({ close });
  }

  /**
   * Cierra el modal
   */
  dismiss() {
    this.modalCtrl.dismiss();
  }
}
