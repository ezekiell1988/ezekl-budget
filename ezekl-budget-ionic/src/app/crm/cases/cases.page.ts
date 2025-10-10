import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AppHeaderComponent } from '../../shared/components/app-header/app-header.component';
import { CrmSearchComponent, CRMSearchResult } from '../../shared/components/crm-search/crm-search.component';
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
  IonSkeletonText,
  IonFab,
  IonFabButton,
  IonNote,
  IonText,
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
  searchOutline,
  filterOutline,
  closeOutline,
  saveOutline,
  businessOutline,
  personOutline,
  closeCircle,
  informationCircleOutline
} from 'ionicons/icons';

import { Subject } from 'rxjs';
import { takeUntil, debounceTime, distinctUntilChanged } from 'rxjs/operators';

import { CrmService } from '../../services/crm.service';
import {
  CaseResponse,
  CaseCreateRequest,
  CaseUpdateRequest,
  CasesListResponse,
  CRMListParams,
  CaseStatus,
  CasePriority,
  CaseOrigin
} from '../../models/crm.models';

@Component({
  selector: 'app-crm-cases',
  templateUrl: './cases.page.html',
  styleUrls: ['./cases.page.scss'],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    AppHeaderComponent,
    CrmSearchComponent,
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
    IonSelect,
    IonSelectOption,
    IonInput,
    IonTextarea,
    IonSkeletonText,
    IonRefresher,
    IonRefresherContent,
    IonInfiniteScroll,
    IonInfiniteScrollContent,
    IonModal,
    IonButtons,
    IonChip,
    IonFab,
    IonFabButton,
    IonNote,
    IonText
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
  pageSize = 5; // 🔧 Cambiado a 5 para testing de paginación
  hasNextPage = false;
  nextLink: string | undefined = undefined; // Para paginación con cookies de D365

  // Modales
  isCreateModalOpen = false;
  isEditModalOpen = false;
  isViewModalOpen = false;
  selectedCase: CaseResponse | null = null;

  // Modales de búsqueda
  isAccountSearchOpen = false;
  isContactSearchOpen = false;
  selectedAccount: CRMSearchResult | null = null;
  selectedContact: CRMSearchResult | null = null;

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
      searchOutline,
      filterOutline,
      closeOutline,
      saveOutline,
      businessOutline,
      personOutline,
      closeCircle,
      informationCircleOutline
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
        order_by: 'incidentid' // Usar primary key para ordenamiento determinístico
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
        this.nextLink = response.next_link;
      } else {
        this.cases = [...this.cases, ...response.cases];
      }

      this.totalCount = response.count;
      this.hasNextPage = !!response.next_link;
      this.nextLink = response.next_link;

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
    if (!this.hasNextPage || !this.nextLink) {
      event.target.complete();
      return;
    }

    this.isLoadingMore = true;
    this.currentPage++;

    try {
      // Usar nextLink para paginación server-driven (D365)
      const response: CasesListResponse = await this.crmService.getCasesByNextLink(this.nextLink).toPromise() as CasesListResponse;

      this.cases = [...this.cases, ...response.cases];
      this.totalCount = response.count;
      this.hasNextPage = !!response.next_link;
      this.nextLink = response.next_link;

    } catch (error) {
      await this.showErrorToast(`Error cargando más casos: ${error}`);
    } finally {
      this.isLoadingMore = false;
      event.target.complete();
    }
  }

  // ===============================================
  // FILTROS Y BÚSQUEDA
  // ===============================================

  /**
   * Búsqueda desde el header (única fuente de búsqueda)
   */
  async onHeaderSearch(searchText: string) {
    this.searchText = searchText;
    this.currentPage = 1;
    await this.loadCases(true);
  }

  /**
   * Toggle de búsqueda del header
   */
  onHeaderSearchToggle(isActive: boolean) {
    // Si se cierra la búsqueda del header, limpiar el texto
    if (!isActive && this.searchText) {
      this.searchText = '';
      this.currentPage = 1;
      this.loadCases(true);
    }
  }

  /**
   * Filtro de estado
   */
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
    this.selectedAccount = null;
    this.selectedContact = null;
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
      position: 'bottom',
      color: 'success',
      icon: 'checkmark-circle-outline'
    });
    await toast.present();
  }

  private async showErrorToast(message: string) {
    const toast = await this.toastController.create({
      message,
      duration: 5000,
      position: 'bottom',
      color: 'danger',
      icon: 'alert-circle-outline'
    });
    await toast.present();
  }

  // ===============================================
  // BÚSQUEDA DE CUENTAS Y CONTACTOS
  // ===============================================

  openAccountSearch() {
    // Si ya hay un contacto seleccionado, no permitir seleccionar cuenta
    if (this.selectedContact) {
      this.showErrorToast('Ya has seleccionado un contacto. Solo puedes asociar una cuenta O un contacto.');
      return;
    }
    this.isAccountSearchOpen = true;
  }

  closeAccountSearch() {
    this.isAccountSearchOpen = false;
  }

  onAccountSelected(result: CRMSearchResult) {
    this.selectedAccount = result;
    this.createForm.patchValue({
      customer_account_id: result.id
    });
    this.closeAccountSearch();
  }

  clearAccount(event: Event) {
    event.stopPropagation();
    this.selectedAccount = null;
    this.createForm.patchValue({
      customer_account_id: ''
    });
  }

  openContactSearch() {
    // Si ya hay una cuenta seleccionada, no permitir seleccionar contacto
    if (this.selectedAccount) {
      this.showErrorToast('Ya has seleccionado una cuenta. Solo puedes asociar una cuenta O un contacto.');
      return;
    }
    this.isContactSearchOpen = true;
  }

  closeContactSearch() {
    this.isContactSearchOpen = false;
  }

  onContactSelected(result: CRMSearchResult) {
    this.selectedContact = result;
    this.createForm.patchValue({
      customer_contact_id: result.id
    });
    this.closeContactSearch();
  }

  clearContact(event: Event) {
    event.stopPropagation();
    this.selectedContact = null;
    this.createForm.patchValue({
      customer_contact_id: ''
    });
  }
}
