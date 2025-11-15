import { Component, OnInit, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonIcon,
  IonContent,
  IonInput,
  IonSelect,
  IonSelectOption,
  IonSpinner,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  ModalController,
  ToastController
} from '@ionic/angular/standalone';

import { addIcons } from 'ionicons';
import {
  closeOutline,
  saveOutline
} from 'ionicons/icons';

import {
  AccountingAccount,
  AccountingAccountService,
  AccountingAccountCreateRequest,
  AccountingAccountUpdateRequest
} from '../../services/accounting-account';

export interface AccountingAccountFormData {
  idAccountingAccountFather?: number;
  codeAccountingAccount: string;
  nameAccountingAccount: string;
}

@Component({
  selector: 'app-account-form-modal',
  templateUrl: './account-form-modal.component.html',
  styleUrls: ['./account-form-modal.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonButtons,
    IonButton,
    IonIcon,
    IonContent,
    IonInput,
    IonSelect,
    IonSelectOption,
    IonSpinner,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonItem,
    IonLabel
  ]
})
export class AccountFormModalComponent implements OnInit {
  @Input() account?: AccountingAccount; // Si se pasa, es modo edición
  @Input() availableParentAccounts: AccountingAccount[] = [];

  private formBuilder = inject(FormBuilder);
  private modalCtrl = inject(ModalController);
  private toastController = inject(ToastController);
  private accountService = inject(AccountingAccountService);

  accountForm!: FormGroup;
  isEditMode = false;
  isLoading = false;

  constructor() {
    // Registrar iconos
    addIcons({
      closeOutline,
      saveOutline
    });
  }

  ngOnInit() {
    this.isEditMode = !!this.account;
    this.initializeForm();
  }

  /**
   * Inicializa el formulario
   */
  private initializeForm(): void {
    this.accountForm = this.formBuilder.group({
      idAccountingAccountFather: [
        this.account?.idAccountingAccountFather || null
      ],
      codeAccountingAccount: [
        this.account?.codeAccountingAccount || '',
        [
          Validators.required,
          Validators.maxLength(50)
        ]
      ],
      nameAccountingAccount: [
        this.account?.nameAccountingAccount || '',
        [
          Validators.required,
          Validators.maxLength(255)
        ]
      ]
    });
  }

  /**
   * Getters para facilitar el acceso a los controles del formulario
   */
  get idAccountingAccountFather() { return this.accountForm.get('idAccountingAccountFather'); }
  get codeAccountingAccount() { return this.accountForm.get('codeAccountingAccount'); }
  get nameAccountingAccount() { return this.accountForm.get('nameAccountingAccount'); }

  /**
   * Métodos para obtener mensajes de error usando las propiedades nativas de Ionic
   */
  getParentAccountErrorText(): string {
    const control = this.idAccountingAccountFather;
    if (control?.invalid && control?.touched) {
      // Por ahora no hay validaciones específicas para la cuenta padre
    }
    return '';
  }

  getCodeErrorText(): string {
    const control = this.codeAccountingAccount;
    if (control?.invalid && control?.touched) {
      if (control.errors?.['required']) {
        return 'El código de cuenta es requerido';
      }
      if (control.errors?.['maxlength']) {
        return 'El código no puede exceder 50 caracteres';
      }
    }
    return '';
  }

  getNameErrorText(): string {
    const control = this.nameAccountingAccount;
    if (control?.invalid && control?.touched) {
      if (control.errors?.['required']) {
        return 'El nombre de la cuenta es requerido';
      }
      if (control.errors?.['maxlength']) {
        return 'El nombre no puede exceder 255 caracteres';
      }
    }
    return '';
  }

  /**
   * Maneja el envío del formulario
   */
  async onSubmit(): Promise<void> {
    if (this.accountForm.valid && !this.isLoading) {
      this.isLoading = true;

      try {
        const formData: AccountingAccountFormData = this.accountForm.value;

        if (this.isEditMode && this.account) {
          await this.updateAccount(formData);
        } else {
          await this.createAccount(formData);
        }
      } catch (error) {
        console.error('Error en el formulario:', error);
      } finally {
        this.isLoading = false;
      }
    } else {
      // Marcar todos los campos como touched para mostrar errores
      this.accountForm.markAllAsTouched();
    }
  }

  /**
   * Crea una nueva cuenta contable
   */
  private async createAccount(formData: AccountingAccountFormData): Promise<void> {
    try {
      const createData: AccountingAccountCreateRequest = {
        idAccountingAccountFather: formData.idAccountingAccountFather || undefined,
        codeAccountingAccount: formData.codeAccountingAccount,
        nameAccountingAccount: formData.nameAccountingAccount
      };

      // Usar el método optimista que maneja rollback automáticamente
      const result = await this.accountService.createAccountingAccountOptimistic(createData).toPromise();

      if (result && result.success && result.account) {
        // Mostrar toast de éxito
        const toast = await this.toastController.create({
          message: `Cuenta contable "${result.account.nameAccountingAccount}" creada exitosamente`,
          duration: 3000,
          color: 'success',
          position: 'top'
        });
        await toast.present();

        // Cerrar modal con datos de respuesta
        this.modalCtrl.dismiss({
          action: 'created',
          account: result.account
        });
      }

    } catch (error: any) {
      console.error('Error creando cuenta contable:', error);

      // El rollback ya se hizo automáticamente en el servicio
      let errorMessage = 'Error al crear la cuenta contable';
      if (error.error) {
        errorMessage = error.error.detail || error.error.message || errorMessage;
      }

      const toast = await this.toastController.create({
        message: errorMessage,
        duration: 5000,
        color: 'danger',
        position: 'top'
      });
      await toast.present();
    }
  }

  /**
   * Actualiza una cuenta contable existente
   */
  private async updateAccount(formData: AccountingAccountFormData): Promise<void> {
    try {
      if (!this.account) {
        throw new Error('No hay cuenta para actualizar');
      }

      const updateData: AccountingAccountUpdateRequest = {};

      // Solo incluir campos que han cambiado
      if (formData.idAccountingAccountFather !== this.account.idAccountingAccountFather) {
        updateData.idAccountingAccountFather = formData.idAccountingAccountFather;
      }
      if (formData.codeAccountingAccount !== this.account.codeAccountingAccount) {
        updateData.codeAccountingAccount = formData.codeAccountingAccount;
      }
      if (formData.nameAccountingAccount !== this.account.nameAccountingAccount) {
        updateData.nameAccountingAccount = formData.nameAccountingAccount;
      }

      // Solo hacer la petición si hay cambios
      if (Object.keys(updateData).length === 0) {
        const toast = await this.toastController.create({
          message: 'No hay cambios que guardar',
          duration: 2000,
          color: 'warning',
          position: 'top'
        });
        await toast.present();
        this.dismiss();
        return;
      }

      const result = await this.accountService.updateAccountingAccountOptimistic(
        this.account.idAccountingAccount,
        updateData
      ).toPromise();

      if (result && result.success) {
        // Mostrar toast de éxito
        const toast = await this.toastController.create({
          message: `Cuenta contable actualizada exitosamente`,
          duration: 3000,
          color: 'success',
          position: 'top'
        });
        await toast.present();

        // Cerrar modal con datos de respuesta
        this.modalCtrl.dismiss({
          action: 'updated',
          account: result.account
        });
      }

    } catch (error: any) {
      console.error('Error actualizando cuenta contable:', error);

      let errorMessage = 'Error al actualizar la cuenta contable';
      if (error.error) {
        errorMessage = error.error.detail || error.error.message || errorMessage;
      }

      const toast = await this.toastController.create({
        message: errorMessage,
        duration: 5000,
        color: 'danger',
        position: 'top'
      });
      await toast.present();
    }
  }

  /**
   * Cierra el modal sin guardar
   */
  dismiss(): void {
    this.modalCtrl.dismiss({
      action: 'cancelled'
    });
  }
}
