import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AppHeaderComponent } from '../../shared/components/app-header/app-header.component';
import { CrmService } from '../../services/crm.service';
import { AccountResponse, AccountsListResponse, AccountCreateRequest, AccountUpdateRequest, CRMOperationResponse } from '../../models/crm.models';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { addIcons } from 'ionicons';
import {
  businessOutline,
  addOutline,
  callOutline,
  mailOutline,
  globeOutline,
  locationOutline,
  eyeOutline,
  createOutline,
  trashOutline,
  closeOutline,
  checkmarkOutline,
  saveOutline,
  filterOutline
} from 'ionicons/icons';
import {
  IonContent,
  IonHeader,
  IonTitle,
  IonToolbar,
  IonGrid,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  IonButton,
  IonIcon,
  IonList,
  IonInput,
  IonSkeletonText,
  IonRefresher,
  IonRefresherContent,
  IonInfiniteScroll,
  IonInfiniteScrollContent,
  IonModal,
  IonButtons,
  IonFab,
  IonFabButton,
  IonNote,
  IonText,
  AlertController,
  ToastController,
  ModalController,
  LoadingController
} from '@ionic/angular/standalone';

@Component({
  selector: 'app-accounts',
  templateUrl: './accounts.page.html',
  styleUrls: ['./accounts.page.scss'],
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
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonItem,
    IonLabel,
    IonButton,
    IonIcon,
    IonList,
    IonInput,
    IonSkeletonText,
    IonRefresher,
    IonRefresherContent,
    IonInfiniteScroll,
    IonInfiniteScrollContent,
    IonModal,
    IonButtons,
    IonFab,
    IonFabButton,
    IonNote,
    IonText
  ]
})
export class AccountsPage implements OnInit, OnDestroy {
  private crmService = inject(CrmService);
  private formBuilder = inject(FormBuilder);
  private alertController = inject(AlertController);
  private toastController = inject(ToastController);
  private modalController = inject(ModalController);
  private loadingController = inject(LoadingController);

  private destroy$ = new Subject<void>();

  // Estado de la página
  accounts: AccountResponse[] = [];
  isLoading = false;
  isLoadingMore = false;
  searchText = '';
  currentPage = 1;
  totalCount = 0;
  pageSize = 25;
  hasNextPage = false;
  nextLink: string | undefined = undefined; // Para paginación con cookies de D365

  // Modales
  isCreateModalOpen = false;
  isEditModalOpen = false;
  isViewModalOpen = false;
  selectedAccount: AccountResponse | null = null;

  // Formularios
  createForm: FormGroup;
  editForm: FormGroup;

  constructor() {
    // Registrar iconos
    addIcons({
      'business-outline': businessOutline,
      'add-outline': addOutline,
      'call-outline': callOutline,
      'mail-outline': mailOutline,
      'globe-outline': globeOutline,
      'location-outline': locationOutline,
      'eye-outline': eyeOutline,
      'create-outline': createOutline,
      'trash-outline': trashOutline,
      'close': closeOutline,
      'checkmark-outline': checkmarkOutline,
      'save-outline': saveOutline,
      'filter-outline': filterOutline
    });

    // Inicializar formularios
    this.createForm = this.formBuilder.group({
      name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(160)]],
      accountnumber: [''],
      telephone1: [''],
      emailaddress1: ['', [Validators.email]],
      websiteurl: [''],
      address1_line1: [''],
      address1_city: [''],
      address1_postalcode: [''],
      address1_country: ['']
    });

    this.editForm = this.formBuilder.group({
      name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(160)]],
      accountnumber: [''],
      telephone1: [''],
      emailaddress1: ['', [Validators.email]],
      websiteurl: [''],
      address1_line1: [''],
      address1_city: [''],
      address1_postalcode: [''],
      address1_country: ['']
    });
  }

  ngOnInit() {
    this.loadAccounts();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ===============================================
  // CARGA DE DATOS
  // ===============================================

  loadAccounts(refresh = false): Promise<void> {
    return new Promise((resolve, reject) => {
      if (refresh) {
        this.currentPage = 1;
        this.accounts = [];
        this.nextLink = undefined; // Reset next link
      }

      this.isLoading = true;

      // Construir filtro de búsqueda
      let filterQuery = '';
      if (this.searchText) {
        filterQuery = `contains(name,'${this.searchText}')`;
      }

      const params = {
        top: this.pageSize, // 25 items por página
        skip: 0, // Siempre 0, no se usa skip en D365
        filter_query: filterQuery || undefined,
        order_by: 'accountid', // ✅ Ordenamiento determinístico por primary key
        select_fields: 'accountid,name,emailaddress1,telephone1,websiteurl,createdon'
      };

      this.crmService.getAccounts(params)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (response: AccountsListResponse) => {
            if (refresh) {
              this.accounts = response.accounts;
            } else {
              this.accounts.push(...response.accounts);
            }

            this.totalCount = response.count;
            this.nextLink = response.next_link;

            // Verificar si hay más páginas usando nextLink
            this.hasNextPage = !!this.nextLink;

            this.isLoading = false;
            this.isLoadingMore = false;
            resolve();
          },
          error: (error) => {
            console.error('❌ Error loading accounts:', error);
            this.showErrorToast('Error al cargar las cuentas');
            this.isLoading = false;
            this.isLoadingMore = false;
            reject(error);
          }
        });
    });
  }

  async onRefresh(event: any) {
    // Reset estado de paginación
    this.nextLink = undefined;
    this.hasNextPage = false;

    await this.loadAccounts(true);
    event.target.complete();
  }

  async onLoadMore(event: any) {
    // Validar que se puede cargar más
    if (!this.hasNextPage || this.isLoadingMore || !this.nextLink) {
      event.target.complete();
      return;
    }

    this.isLoadingMore = true;

    this.crmService.getAccountsByNextLink(this.nextLink)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: AccountsListResponse) => {
          // Agregar nuevos registros al array existente
          this.accounts = [...this.accounts, ...response.accounts];

          // Actualizar nextLink para siguiente página
          this.nextLink = response.next_link;
          this.hasNextPage = !!this.nextLink;

          this.isLoadingMore = false;
          event.target.complete();
        },
        error: (error) => {
          console.error('❌ Error loading more accounts:', error);
          this.showErrorToast('Error al cargar más cuentas');
          this.isLoadingMore = false;
          event.target.complete();
        }
      });
  }

  // ===============================================
  // FILTROS Y BÚSQUEDA
  // ===============================================

  /**
   * Búsqueda desde el header (única fuente de búsqueda)
   */
  async onHeaderSearch(searchText: string) {
    this.searchText = searchText;
    await this.loadAccounts(true);
  }

  /**
   * Toggle de búsqueda del header
   */
  onHeaderSearchToggle(isActive: boolean) {
    if (!isActive) {
      // Si se desactiva la búsqueda, limpiar el texto
      this.searchText = '';
      this.loadAccounts(true);
    }
  }

  async clearFilters() {
    this.searchText = '';
    await this.loadAccounts(true);
  }

  // ===============================================
  // CRUD OPERATIONS
  // ===============================================

  openCreateModal() {
    this.createForm.reset({
      name: '',
      accountnumber: '',
      telephone1: '',
      emailaddress1: '',
      websiteurl: '',
      address1_line1: '',
      address1_city: '',
      address1_postalcode: '',
      address1_country: '',
      description: ''
    });
    this.isCreateModalOpen = true;
  }

  closeCreateModal() {
    this.isCreateModalOpen = false;
    this.createForm.reset();
  }

  async createAccount() {
    if (this.createForm.invalid) {
      return;
    }

    const loading = await this.loadingController.create({
      message: 'Creando cuenta...'
    });
    await loading.present();

    // Construir request solo con campos no vacíos
    const request: AccountCreateRequest = {
      name: this.createForm.value.name
    };

    // Agregar campos opcionales solo si tienen valor
    if (this.createForm.value.accountnumber) request.accountnumber = this.createForm.value.accountnumber;
    if (this.createForm.value.telephone1) request.telephone1 = this.createForm.value.telephone1;
    if (this.createForm.value.emailaddress1) request.emailaddress1 = this.createForm.value.emailaddress1;
    if (this.createForm.value.websiteurl) request.websiteurl = this.createForm.value.websiteurl;
    if (this.createForm.value.address1_line1) request.address1_line1 = this.createForm.value.address1_line1;
    if (this.createForm.value.address1_city) request.address1_city = this.createForm.value.address1_city;
    if (this.createForm.value.address1_postalcode) request.address1_postalcode = this.createForm.value.address1_postalcode;
    if (this.createForm.value.address1_country) request.address1_country = this.createForm.value.address1_country;

    this.crmService.createAccount(request)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: CRMOperationResponse) => {
          loading.dismiss();
          this.showSuccessToast('Cuenta creada exitosamente');
          this.closeCreateModal();
          this.loadAccounts(true);
        },
        error: (error) => {
          loading.dismiss();
          console.error('Error creating account:', error);
          this.showErrorToast('Error al crear la cuenta');
        }
      });
  }

  openViewModal(account: AccountResponse) {
    this.selectedAccount = account;
    this.isViewModalOpen = true;
  }

  closeViewModal() {
    this.isViewModalOpen = false;
    this.selectedAccount = null;
  }

  openEditModal(account: AccountResponse) {
    this.selectedAccount = account;
    this.editForm.patchValue({
      name: account.name,
      accountnumber: account.accountnumber || '',
      telephone1: account.telephone1 || '',
      emailaddress1: account.emailaddress1 || '',
      websiteurl: account.websiteurl || '',
      address1_line1: account.address1_line1 || '',
      address1_city: account.address1_city || '',
      address1_postalcode: account.address1_postalcode || '',
      address1_country: account.address1_country || '',
      description: ''
    });
    this.isEditModalOpen = true;
  }

  closeEditModal() {
    this.isEditModalOpen = false;
    this.selectedAccount = null;
    this.editForm.reset();
  }

  async updateAccount() {
    if (this.editForm.invalid || !this.selectedAccount) {
      return;
    }

    const loading = await this.loadingController.create({
      message: 'Actualizando cuenta...'
    });
    await loading.present();

    // Construir request solo con campos modificados
    const request: AccountUpdateRequest = {};

    if (this.editForm.value.name !== this.selectedAccount.name) request.name = this.editForm.value.name;
    if (this.editForm.value.telephone1 !== this.selectedAccount.telephone1) request.telephone1 = this.editForm.value.telephone1;
    if (this.editForm.value.emailaddress1 !== this.selectedAccount.emailaddress1) request.emailaddress1 = this.editForm.value.emailaddress1;
    if (this.editForm.value.websiteurl !== this.selectedAccount.websiteurl) request.websiteurl = this.editForm.value.websiteurl;
    if (this.editForm.value.address1_line1 !== this.selectedAccount.address1_line1) request.address1_line1 = this.editForm.value.address1_line1;
    if (this.editForm.value.address1_city !== this.selectedAccount.address1_city) request.address1_city = this.editForm.value.address1_city;
    if (this.editForm.value.address1_postalcode !== this.selectedAccount.address1_postalcode) request.address1_postalcode = this.editForm.value.address1_postalcode;
    if (this.editForm.value.address1_country !== this.selectedAccount.address1_country) request.address1_country = this.editForm.value.address1_country;

    this.crmService.updateAccount(this.selectedAccount.accountid, request)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: CRMOperationResponse) => {
          loading.dismiss();
          this.showSuccessToast('Cuenta actualizada exitosamente');
          this.closeEditModal();
          this.loadAccounts(true);
        },
        error: (error) => {
          loading.dismiss();
          console.error('Error updating account:', error);
          this.showErrorToast('Error al actualizar la cuenta');
        }
      });
  }

  async deleteAccount(account: AccountResponse) {
    const alert = await this.alertController.create({
      header: '¿Eliminar cuenta?',
      message: `¿Estás seguro de que deseas eliminar la cuenta "${account.name}"? Esta acción no se puede deshacer.`,
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Eliminar',
          role: 'destructive',
          handler: () => {
            this.performDelete(account);
          }
        }
      ]
    });

    await alert.present();
  }

  private async performDelete(account: AccountResponse) {
    const loading = await this.loadingController.create({
      message: 'Eliminando cuenta...'
    });
    await loading.present();

    this.crmService.deleteAccount(account.accountid)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: CRMOperationResponse) => {
          loading.dismiss();
          this.showSuccessToast('Cuenta eliminada exitosamente');
          this.loadAccounts(true);
        },
        error: (error) => {
          loading.dismiss();
          console.error('Error deleting account:', error);
          this.showErrorToast('Error al eliminar la cuenta');
        }
      });
  }

  // ===============================================
  // UTILIDADES
  // ===============================================

  formatDate(dateString?: string): string {
    if (!dateString) return '(No especificado)';

    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
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
      color: 'success',
      position: 'bottom'
    });
    await toast.present();
  }

  private async showErrorToast(message: string) {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      color: 'danger',
      position: 'bottom'
    });
    await toast.present();
  }
}
