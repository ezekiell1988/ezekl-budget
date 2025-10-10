import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AppHeaderComponent } from '../../shared/components/app-header/app-header.component';
import {
  IonContent,
  IonHeader,
  IonTitle,
  IonToolbar,
  IonGrid,
  IonRow,
  IonCol,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  IonButton,
  IonIcon,
  IonList,
  IonSearchbar,
  IonSelect,
  IonSelectOption,
  IonInput,
  IonTextarea,
  IonSpinner,
  IonRefresher,
  IonRefresherContent,
  IonInfiniteScroll,
  IonInfiniteScrollContent,
  IonAlert,
  IonModal,
  IonButtons,
  IonBackButton,
  IonBadge,
  IonChip,
  AlertController,
  ToastController,
  ModalController,
  LoadingController
} from '@ionic/angular/standalone';

import { addIcons } from 'ionicons';
import {
  add,
  createOutline,
  trashOutline,
  eyeOutline,
  refreshOutline,
  searchOutline,
  filterOutline,
  closeOutline,
  saveOutline
} from 'ionicons/icons';

import { Subject } from 'rxjs';
import { takeUntil, debounceTime, distinctUntilChanged } from 'rxjs/operators';

import { CrmService } from '../../shared/services/crm.service';
import {
  CaseResponse,
  CaseCreateRequest,
  CaseUpdateRequest,
  CasesListResponse,
  CRMListParams,
  CaseStatus,
  CasePriority,
  CaseOrigin
} from '../../shared/models/crm.models';

@Component({
  selector: 'app-crm-cases',
  templateUrl: './cases.page.html',
  styleUrls: ['./cases.page.scss'],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    AppHeaderComponent,
    IonContent,
    IonHeader,
    IonTitle,
    IonToolbar,
    IonGrid,
    IonRow,
    IonCol,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonItem,
    IonLabel,
    IonButton,
    IonIcon,
    IonList,
    IonSearchbar,
    IonSelect,
    IonSelectOption,
    IonInput,
    IonTextarea,
    IonSpinner,
    IonRefresher,
    IonRefresherContent,
    IonInfiniteScroll,
    IonInfiniteScrollContent,
    IonModal,
    IonButtons,
    IonChip
  ]
})
export class CasesPage implements OnInit, OnDestroy {
  private crmService = inject(CrmService);
  private formBuilder = inject(FormBuilder);
  private alertController = inject(AlertController);
  private toastController = inject(ToastController);
  private modalController = inject(ModalController);
  private loadingController = inject(LoadingController);

  private destroy$ = new Subject<void>();

  // Estado de la página
  cases: CaseResponse[] = [];
  isLoading = false;
  isLoadingMore = false;
  searchText = '';
  selectedStatus: number | null = null;
  currentPage = 1;
  totalCount = 0;
  pageSize = 25;
  hasNextPage = false;

  // Modales
  isCreateModalOpen = false;
  isEditModalOpen = false;
  isViewModalOpen = false;
  selectedCase: CaseResponse | null = null;

  // Formularios
  createForm: FormGroup;
  editForm: FormGroup;

  // Enums para templates
  CaseStatus = CaseStatus;
  CasePriority = CasePriority;
  CaseOrigin = CaseOrigin;

  constructor() {
    // Registrar iconos
    addIcons({
      add,
      createOutline,
      trashOutline,
      eyeOutline,
      refreshOutline,
      searchOutline,
      filterOutline,
      closeOutline,
      saveOutline
    });

    // Inicializar formularios
    this.createForm = this.formBuilder.group({
      title: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(160)]],
      description: [''],
      casetypecode: [null],
      customer_account_id: [''],
      customer_contact_id: [''],
      prioritycode: [CasePriority.Normal],
      caseorigincode: [CaseOrigin.Web]
    });

    this.editForm = this.formBuilder.group({
      title: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(160)]],
      description: [''],
      casetypecode: [null],
      statuscode: [null],
      prioritycode: [null]
    });
  }

  ngOnInit() {
    this.loadCases();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ===============================================
  // CARGA DE DATOS
  // ===============================================

  async loadCases(refresh = false) {
    if (!refresh) {
      this.isLoading = true;
    }

    try {
      const params: CRMListParams = {
        top: this.pageSize,
        skip: refresh ? 0 : (this.currentPage - 1) * this.pageSize,
        order_by: 'createdon desc'
      };

      // Aplicar filtros
      const filters: string[] = [];

      if (this.searchText.trim()) {
        filters.push(`contains(title,'${this.searchText.trim()}')`);
      }

      if (this.selectedStatus !== null) {
        filters.push(`statuscode eq ${this.selectedStatus}`);
      }

      if (filters.length > 0) {
        params.filter_query = filters.join(' and ');
      }

      const response: CasesListResponse = await this.crmService.getCases(params).toPromise() as CasesListResponse;

      if (refresh) {
        this.cases = response.cases;
        this.currentPage = 1;
      } else {
        this.cases = [...this.cases, ...response.cases];
      }

      this.totalCount = response.count;
      this.hasNextPage = !!response.next_link;

    } catch (error) {
      await this.showErrorToast(`Error cargando casos: ${error}`);
    } finally {
      this.isLoading = false;
      this.isLoadingMore = false;
    }
  }

  async onRefresh(event: any) {
    await this.loadCases(true);
    event.target.complete();
  }

  async onLoadMore(event: any) {
    if (!this.hasNextPage) {
      event.target.complete();
      return;
    }

    this.isLoadingMore = true;
    this.currentPage++;
    await this.loadCases();
    event.target.complete();
  }

  // ===============================================
  // FILTROS Y BÚSQUEDA
  // ===============================================

  async onSearch(event: any) {
    this.searchText = event.target.value;
    this.currentPage = 1;
    await this.loadCases(true);
  }

  async onStatusFilter(event: any) {
    this.selectedStatus = event.target.value;
    this.currentPage = 1;
    await this.loadCases(true);
  }

  async clearFilters() {
    this.searchText = '';
    this.selectedStatus = null;
    this.currentPage = 1;
    await this.loadCases(true);
  }

  // ===============================================
  // CRUD OPERATIONS
  // ===============================================

  openCreateModal() {
    this.createForm.reset();
    this.createForm.patchValue({
      prioritycode: CasePriority.Normal,
      caseorigincode: CaseOrigin.Web
    });
    this.isCreateModalOpen = true;
  }

  closeCreateModal() {
    this.isCreateModalOpen = false;
    this.createForm.reset();
  }

  async createCase() {
    if (this.createForm.valid) {
      const loading = await this.loadingController.create({
        message: 'Creando caso...'
      });
      await loading.present();

      try {
        const caseData: CaseCreateRequest = this.createForm.value;

        // Limpiar campos vacíos
        if (!caseData.customer_account_id?.trim()) {
          delete caseData.customer_account_id;
        }
        if (!caseData.customer_contact_id?.trim()) {
          delete caseData.customer_contact_id;
        }

        const response = await this.crmService.createCase(caseData).toPromise();

        if (response?.status === 'success') {
          await this.showSuccessToast('Caso creado exitosamente');
          this.closeCreateModal();
          await this.loadCases(true);
        } else {
          throw new Error(response?.message || 'Error desconocido');
        }

      } catch (error) {
        await this.showErrorToast(`Error creando caso: ${error}`);
      } finally {
        await loading.dismiss();
      }
    }
  }

  openViewModal(caseItem: CaseResponse) {
    this.selectedCase = caseItem;
    this.isViewModalOpen = true;
  }

  closeViewModal() {
    this.isViewModalOpen = false;
    this.selectedCase = null;
  }

  openEditModal(caseItem: CaseResponse) {
    this.selectedCase = caseItem;
    this.editForm.patchValue({
      title: caseItem.title,
      description: caseItem.description,
      casetypecode: caseItem.casetypecode,
      statuscode: caseItem.statuscode,
      prioritycode: caseItem.prioritycode
    });
    this.isEditModalOpen = true;
  }

  closeEditModal() {
    this.isEditModalOpen = false;
    this.selectedCase = null;
    this.editForm.reset();
  }

  async updateCase() {
    if (this.editForm.valid && this.selectedCase) {
      const loading = await this.loadingController.create({
        message: 'Actualizando caso...'
      });
      await loading.present();

      try {
        const caseData: CaseUpdateRequest = this.editForm.value;

        const response = await this.crmService.updateCase(this.selectedCase.incidentid, caseData).toPromise();

        if (response?.status === 'success') {
          await this.showSuccessToast('Caso actualizado exitosamente');
          this.closeEditModal();
          await this.loadCases(true);
        } else {
          throw new Error(response?.message || 'Error desconocido');
        }

      } catch (error) {
        await this.showErrorToast(`Error actualizando caso: ${error}`);
      } finally {
        await loading.dismiss();
      }
    }
  }

  async deleteCase(caseItem: CaseResponse) {
    const alert = await this.alertController.create({
      header: 'Confirmar Eliminación',
      message: `¿Está seguro de que desea eliminar el caso "${caseItem.title}"? Esta acción no se puede deshacer.`,
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Eliminar',
          role: 'destructive',
          handler: async () => {
            await this.performDelete(caseItem);
          }
        }
      ]
    });

    await alert.present();
  }

  private async performDelete(caseItem: CaseResponse) {
    const loading = await this.loadingController.create({
      message: 'Eliminando caso...'
    });
    await loading.present();

    try {
      const response = await this.crmService.deleteCase(caseItem.incidentid).toPromise();

      if (response?.status === 'success') {
        await this.showSuccessToast('Caso eliminado exitosamente');
        await this.loadCases(true);
      } else {
        throw new Error(response?.message || 'Error desconocido');
      }

    } catch (error) {
      await this.showErrorToast(`Error eliminando caso: ${error}`);
    } finally {
      await loading.dismiss();
    }
  }

  // ===============================================
  // UTILIDADES
  // ===============================================

  getStatusText(statuscode?: number): string {
    switch (statuscode) {
      case CaseStatus.Active: return 'Activo';
      case CaseStatus.Resolved: return 'Resuelto';
      case CaseStatus.Canceled: return 'Cancelado';
      case CaseStatus.Merged: return 'Fusionado';
      default: return 'Desconocido';
    }
  }

  getStatusColor(statuscode?: number): string {
    switch (statuscode) {
      case CaseStatus.Active: return 'primary';
      case CaseStatus.Resolved: return 'success';
      case CaseStatus.Canceled: return 'medium';
      case CaseStatus.Merged: return 'warning';
      default: return 'medium';
    }
  }

  getPriorityText(prioritycode?: number): string {
    switch (prioritycode) {
      case CasePriority.High: return 'Alta';
      case CasePriority.Normal: return 'Normal';
      case CasePriority.Low: return 'Baja';
      default: return 'Normal';
    }
  }

  getPriorityColor(prioritycode?: number): string {
    switch (prioritycode) {
      case CasePriority.High: return 'danger';
      case CasePriority.Normal: return 'medium';
      case CasePriority.Low: return 'success';
      default: return 'medium';
    }
  }

  formatDate(dateString?: string): string {
    if (!dateString) return 'No disponible';
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  private async showSuccessToast(message: string) {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      position: 'top',
      color: 'success',
      icon: 'checkmark-circle-outline'
    });
    await toast.present();
  }

  private async showErrorToast(message: string) {
    const toast = await this.toastController.create({
      message,
      duration: 5000,
      position: 'top',
      color: 'danger',
      icon: 'alert-circle-outline'
    });
    await toast.present();
  }
}
