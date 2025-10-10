import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AppHeaderComponent } from '../../shared/components/app-header/app-header.component';
import { CrmService } from '../../shared/services/crm.service';
import { ContactResponse, ContactsListResponse, ContactCreateRequest, ContactUpdateRequest, CRMOperationResponse } from '../../shared/models/crm.models';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { addIcons } from 'ionicons';
import {
  peopleOutline,
  addOutline,
  callOutline,
  mailOutline,
  phonePortraitOutline,
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
  selector: 'app-contacts',
  templateUrl: './contacts.page.html',
  styleUrls: ['./contacts.page.scss'],
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
export class ContactsPage implements OnInit, OnDestroy {
  private crmService = inject(CrmService);
  private formBuilder = inject(FormBuilder);
  private alertController = inject(AlertController);
  private toastController = inject(ToastController);
  private modalController = inject(ModalController);
  private loadingController = inject(LoadingController);

  private destroy$ = new Subject<void>();

  // Estado de la página
  contacts: ContactResponse[] = [];
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
  selectedContact: ContactResponse | null = null;

  // Formularios
  createForm: FormGroup;
  editForm: FormGroup;

  constructor() {
    // Registrar iconos
    addIcons({
      'people-outline': peopleOutline,
      'add-outline': addOutline,
      'call-outline': callOutline,
      'mail-outline': mailOutline,
      'phone-portrait-outline': phonePortraitOutline,
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
      firstname: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(50)]],
      lastname: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(50)]],
      jobtitle: [''],
      telephone1: [''],
      mobilephone: [''],
      emailaddress1: ['', [Validators.email]],
      address1_line1: [''],
      address1_city: [''],
      address1_postalcode: [''],
      address1_country: ['']
    });

    this.editForm = this.formBuilder.group({
      firstname: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(50)]],
      lastname: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(50)]],
      jobtitle: [''],
      telephone1: [''],
      mobilephone: [''],
      emailaddress1: ['', [Validators.email]],
      address1_line1: [''],
      address1_city: [''],
      address1_postalcode: [''],
      address1_country: ['']
    });
  }

  ngOnInit() {
    this.loadContacts();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ===============================================
  // CARGA DE DATOS
  // ===============================================

  loadContacts(refresh = false): Promise<void> {
    return new Promise((resolve, reject) => {
      if (refresh) {
        this.currentPage = 1;
        this.contacts = [];
        this.nextLink = undefined; // Reset next link
      }

      this.isLoading = true;

      // Construir filtro de búsqueda
      let filterQuery = '';
      if (this.searchText) {
        filterQuery = `contains(fullname,'${this.searchText}')`;
      }

      const params = {
        top: this.pageSize, // 25 items por página
        skip: 0, // Siempre 0, no se usa skip en D365
        filter_query: filterQuery || undefined,
        order_by: 'contactid', // ✅ Ordenamiento determinístico por primary key
        select_fields: 'contactid,fullname,firstname,lastname,jobtitle,emailaddress1,telephone1,mobilephone,address1_city,address1_country,createdon'
      };

      this.crmService.getContacts(params)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (response: ContactsListResponse) => {
            if (refresh) {
              this.contacts = response.contacts;
            } else {
              this.contacts.push(...response.contacts);
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
            console.error('❌ Error loading contacts:', error);
            this.showErrorToast('Error al cargar los contactos');
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

    await this.loadContacts(true);
    event.target.complete();
  }

  async onLoadMore(event: any) {
    // Validar que se puede cargar más
    if (!this.hasNextPage || this.isLoadingMore || !this.nextLink) {
      event.target.complete();
      return;
    }

    this.isLoadingMore = true;

    this.crmService.getContactsByNextLink(this.nextLink)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: ContactsListResponse) => {
          // Agregar nuevos registros al array existente
          this.contacts = [...this.contacts, ...response.contacts];

          // Actualizar nextLink para siguiente página
          this.nextLink = response.next_link;
          this.hasNextPage = !!this.nextLink;

          this.isLoadingMore = false;
          event.target.complete();
        },
        error: (error) => {
          console.error('❌ Error loading more contacts:', error);
          this.showErrorToast('Error al cargar más contactos');
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
    await this.loadContacts(true);
  }

  /**
   * Toggle de búsqueda del header
   */
  onHeaderSearchToggle(isActive: boolean) {
    if (!isActive) {
      // Si se desactiva la búsqueda, limpiar el texto
      this.searchText = '';
      this.loadContacts(true);
    }
  }

  async clearFilters() {
    this.searchText = '';
    await this.loadContacts(true);
  }

  // ===============================================
  // CRUD OPERATIONS
  // ===============================================

  openCreateModal() {
    this.createForm.reset({
      firstname: '',
      lastname: '',
      jobtitle: '',
      telephone1: '',
      mobilephone: '',
      emailaddress1: '',
      address1_line1: '',
      address1_city: '',
      address1_postalcode: '',
      address1_country: ''
    });
    this.isCreateModalOpen = true;
  }

  closeCreateModal() {
    this.isCreateModalOpen = false;
    this.createForm.reset();
  }

  async createContact() {
    if (this.createForm.invalid) {
      return;
    }

    const loading = await this.loadingController.create({
      message: 'Creando contacto...'
    });
    await loading.present();

    // Construir request solo con campos no vacíos
    const request: ContactCreateRequest = {
      firstname: this.createForm.value.firstname,
      lastname: this.createForm.value.lastname
    };

    // Agregar campos opcionales solo si tienen valor
    if (this.createForm.value.jobtitle) request.jobtitle = this.createForm.value.jobtitle;
    if (this.createForm.value.telephone1) request.telephone1 = this.createForm.value.telephone1;
    if (this.createForm.value.mobilephone) request.mobilephone = this.createForm.value.mobilephone;
    if (this.createForm.value.emailaddress1) request.emailaddress1 = this.createForm.value.emailaddress1;
    if (this.createForm.value.address1_line1) request.address1_line1 = this.createForm.value.address1_line1;
    if (this.createForm.value.address1_city) request.address1_city = this.createForm.value.address1_city;
    if (this.createForm.value.address1_postalcode) request.address1_postalcode = this.createForm.value.address1_postalcode;
    if (this.createForm.value.address1_country) request.address1_country = this.createForm.value.address1_country;

    this.crmService.createContact(request)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: CRMOperationResponse) => {
          loading.dismiss();
          this.showSuccessToast('Contacto creado exitosamente');
          this.closeCreateModal();
          this.loadContacts(true);
        },
        error: (error) => {
          loading.dismiss();
          console.error('Error creating contact:', error);
          this.showErrorToast('Error al crear el contacto');
        }
      });
  }

  openViewModal(contact: ContactResponse) {
    this.selectedContact = contact;
    this.isViewModalOpen = true;
  }

  closeViewModal() {
    this.isViewModalOpen = false;
    this.selectedContact = null;
  }

  openEditModal(contact: ContactResponse) {
    this.selectedContact = contact;
    this.editForm.patchValue({
      firstname: contact.firstname || '',
      lastname: contact.lastname || '',
      jobtitle: contact.jobtitle || '',
      telephone1: contact.telephone1 || '',
      mobilephone: contact.mobilephone || '',
      emailaddress1: contact.emailaddress1 || '',
      address1_line1: contact.address1_line1 || '',
      address1_city: contact.address1_city || '',
      address1_postalcode: contact.address1_postalcode || '',
      address1_country: contact.address1_country || ''
    });
    this.isEditModalOpen = true;
  }

  closeEditModal() {
    this.isEditModalOpen = false;
    this.selectedContact = null;
    this.editForm.reset();
  }

  async updateContact() {
    if (this.editForm.invalid || !this.selectedContact) {
      return;
    }

    const loading = await this.loadingController.create({
      message: 'Actualizando contacto...'
    });
    await loading.present();

    // Construir request solo con campos modificados
    const request: ContactUpdateRequest = {};

    if (this.editForm.value.firstname !== this.selectedContact.firstname) request.firstname = this.editForm.value.firstname;
    if (this.editForm.value.lastname !== this.selectedContact.lastname) request.lastname = this.editForm.value.lastname;
    if (this.editForm.value.jobtitle !== this.selectedContact.jobtitle) request.jobtitle = this.editForm.value.jobtitle;
    if (this.editForm.value.telephone1 !== this.selectedContact.telephone1) request.telephone1 = this.editForm.value.telephone1;
    if (this.editForm.value.mobilephone !== this.selectedContact.mobilephone) request.mobilephone = this.editForm.value.mobilephone;
    if (this.editForm.value.emailaddress1 !== this.selectedContact.emailaddress1) request.emailaddress1 = this.editForm.value.emailaddress1;
    if (this.editForm.value.address1_line1 !== this.selectedContact.address1_line1) request.address1_line1 = this.editForm.value.address1_line1;
    if (this.editForm.value.address1_city !== this.selectedContact.address1_city) request.address1_city = this.editForm.value.address1_city;
    if (this.editForm.value.address1_postalcode !== this.selectedContact.address1_postalcode) request.address1_postalcode = this.editForm.value.address1_postalcode;
    if (this.editForm.value.address1_country !== this.selectedContact.address1_country) request.address1_country = this.editForm.value.address1_country;

    this.crmService.updateContact(this.selectedContact.contactid, request)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: CRMOperationResponse) => {
          loading.dismiss();
          this.showSuccessToast('Contacto actualizado exitosamente');
          this.closeEditModal();
          this.loadContacts(true);
        },
        error: (error) => {
          loading.dismiss();
          console.error('Error updating contact:', error);
          this.showErrorToast('Error al actualizar el contacto');
        }
      });
  }

  async deleteContact(contact: ContactResponse) {
    const alert = await this.alertController.create({
      header: '¿Eliminar contacto?',
      message: `¿Estás seguro de que deseas eliminar el contacto "${contact.fullname}"? Esta acción no se puede deshacer.`,
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Eliminar',
          role: 'destructive',
          handler: () => {
            this.performDelete(contact);
          }
        }
      ]
    });

    await alert.present();
  }

  private async performDelete(contact: ContactResponse) {
    const loading = await this.loadingController.create({
      message: 'Eliminando contacto...'
    });
    await loading.present();

    this.crmService.deleteContact(contact.contactid)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: CRMOperationResponse) => {
          loading.dismiss();
          this.showSuccessToast('Contacto eliminado exitosamente');
          this.loadContacts(true);
        },
        error: (error) => {
          loading.dismiss();
          console.error('Error deleting contact:', error);
          this.showErrorToast('Error al eliminar el contacto');
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
