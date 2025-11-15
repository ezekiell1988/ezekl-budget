import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonIcon,
  IonContent,
  IonInput,
  IonTextarea,
  IonSpinner,
  ModalController,
  ToastController
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  closeOutline,
  saveOutline
} from 'ionicons/icons';

import { Company, CompanyService } from '../../services/company';

export interface CompanyFormData {
  codeCompany: string;
  nameCompany: string;
  descriptionCompany: string;
}

@Component({
  selector: 'app-company-form-modal',
  templateUrl: './company-form-modal.component.html',
  styleUrls: ['./company-form-modal.component.scss'],
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
    IonTextarea,
    IonSpinner
  ]
})
export class CompanyFormModalComponent implements OnInit {
  @Input() company?: Company; // Si se pasa, es modo edición

  companyForm!: FormGroup;
  isEditMode = false;
  isLoading = false;

  constructor(
    private formBuilder: FormBuilder,
    private modalCtrl: ModalController,
    private toastController: ToastController,
    private companyService: CompanyService
  ) {
    // Registrar iconos
    addIcons({
      closeOutline,
      saveOutline
    });
  }

  ngOnInit() {
    this.isEditMode = !!this.company;
    this.initializeForm();
  }

  /**
   * Inicializa el formulario
   */
  private initializeForm(): void {
    this.companyForm = this.formBuilder.group({
      codeCompany: [
        this.company?.codeCompany || '',
        [
          Validators.required,
          Validators.maxLength(20)
        ]
      ],
      nameCompany: [
        this.company?.nameCompany || '',
        [
          Validators.required,
          Validators.maxLength(100)
        ]
      ],
      descriptionCompany: [
        this.company?.descriptionCompany || '',
        [
          Validators.required,
          Validators.maxLength(500)
        ]
      ]
    });
  }

  /**
   * Getters para facilitar el acceso a los controles del formulario
   */
  get codeCompany() { return this.companyForm.get('codeCompany'); }
  get nameCompany() { return this.companyForm.get('nameCompany'); }
  get descriptionCompany() { return this.companyForm.get('descriptionCompany'); }

  /**
   * Métodos para obtener mensajes de error usando las propiedades nativas de Ionic
   */
  getCodeErrorText(): string {
    const control = this.codeCompany;
    if (control?.invalid && control?.touched) {
      if (control.errors?.['required']) {
        return 'El código/cédula es requerido';
      }
      if (control.errors?.['maxlength']) {
        return 'El código no puede exceder 20 caracteres';
      }
    }
    return '';
  }

  getNameErrorText(): string {
    const control = this.nameCompany;
    if (control?.invalid && control?.touched) {
      if (control.errors?.['required']) {
        return 'El nombre de la compañía es requerido';
      }
      if (control.errors?.['maxlength']) {
        return 'El nombre no puede exceder 100 caracteres';
      }
    }
    return '';
  }

  getDescriptionErrorText(): string {
    const control = this.descriptionCompany;
    if (control?.invalid && control?.touched) {
      if (control.errors?.['required']) {
        return 'La descripción es requerida';
      }
      if (control.errors?.['maxlength']) {
        return 'La descripción no puede exceder 500 caracteres';
      }
    }
    return '';
  }

  /**
   * Maneja el envío del formulario
   */
  async onSubmit(): Promise<void> {
    if (this.companyForm.valid && !this.isLoading) {
      this.isLoading = true;

      try {
        const formData: CompanyFormData = this.companyForm.value;

        if (this.isEditMode && this.company) {
          await this.updateCompany(formData);
        } else {
          await this.createCompany(formData);
        }
      } catch (error) {
        console.error('Error en formulario:', error);
      } finally {
        this.isLoading = false;
      }
    } else {
      // Marcar todos los campos como touched para mostrar errores
      this.companyForm.markAllAsTouched();
    }
  }

  /**
   * Crea una nueva compañía
   */
  private async createCompany(formData: CompanyFormData): Promise<void> {
    try {
      // Usar el método optimista que maneja rollback automáticamente
      const result = await this.companyService.createCompanyOptimistic(formData).toPromise();

      if (result && result.success && result.company) {
        const toast = await this.toastController.create({
          message: `Compañía "${formData.nameCompany}" creada exitosamente`,
          duration: 3000,
          position: 'bottom',
          color: 'success',
          icon: 'checkmark-circle-outline'
        });
        await toast.present();

        // Cerrar modal con resultado (incluyendo el ID real del servidor)
        this.modalCtrl.dismiss({
          action: 'created',
          data: result.company
        });
      }

    } catch (error: any) {
      console.error('Error creando compañía:', error);

      // El rollback ya se hizo automáticamente en el servicio
      let errorMessage = 'Error al crear la compañía';
      if (error.error) {
        errorMessage = error.error;
      }

      const toast = await this.toastController.create({
        message: errorMessage,
        duration: 3000,
        position: 'bottom',
        color: 'danger',
        icon: 'alert-circle-outline'
      });
      await toast.present();
    }
  }

  /**
   * Actualiza una compañía existente
   */
  private async updateCompany(formData: CompanyFormData): Promise<void> {
    try {
      if (!this.company) return;

      // Usar el método optimista que maneja rollback automáticamente
      const result = await this.companyService.updateCompanyOptimistic(this.company.idCompany, formData).toPromise();

      if (result && result.success && result.company) {
        const toast = await this.toastController.create({
          message: `Compañía "${formData.nameCompany}" actualizada exitosamente`,
          duration: 3000,
          position: 'bottom',
          color: 'success',
          icon: 'checkmark-circle-outline'
        });
        await toast.present();

        // Cerrar modal con resultado
        this.modalCtrl.dismiss({
          action: 'updated',
          data: result.company
        });
      }

    } catch (error: any) {
      console.error('Error actualizando compañía:', error);

      // El rollback ya se hizo automáticamente en el servicio
      let errorMessage = 'Error al actualizar la compañía';
      if (error.error) {
        errorMessage = error.error;
      }

      const toast = await this.toastController.create({
        message: errorMessage,
        duration: 3000,
        position: 'bottom',
        color: 'danger',
        icon: 'alert-circle-outline'
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
