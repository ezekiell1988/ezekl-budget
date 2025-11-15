import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonContent,
  IonHeader,
  IonTitle,
  IonToolbar,
  IonGrid,
  IonList,
  IonItem,
  IonLabel,
  IonIcon,
  IonButton,
  IonCard,
  IonCardContent,
  IonRefresher,
  IonRefresherContent,
  IonInfiniteScroll,
  IonInfiniteScrollContent,
  IonSkeletonText,
  IonFab,
  IonFabButton,
  IonToggle,
  IonChip,
  IonCardTitle,
  IonCardHeader,
  IonButtons,
  RefresherCustomEvent,
  InfiniteScrollCustomEvent,
  SearchbarCustomEvent,
  ToggleCustomEvent,
  ModalController,
  AlertController,
  ToastController,
} from '@ionic/angular/standalone';

// Iconos
import { addIcons } from 'ionicons';
import {
  businessOutline,
  alertCircleOutline,
  refresh,
  chevronForward,
  createOutline,
  trashOutline,
  addOutline,
  add,
  filterOutline,
  closeOutline,
  listOutline,
  chevronDown
} from 'ionicons/icons';

// Servicios y componentes
import { AppHeaderComponent } from '../shared/components/app-header/app-header.component';
import { CompanyFormModalComponent } from './company-form-modal/company-form-modal.component';
import { CompanyService, Company, PaginationState } from '../services/company';

// RxJS
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-companies',
  templateUrl: './companies.page.html',
  styleUrls: ['./companies.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonContent,
    IonGrid,
    IonList,
    IonItem,
    IonLabel,
    IonIcon,
    IonButton,
    IonCard,
    IonCardContent,
    IonCardTitle,
    IonCardHeader,
    IonRefresher,
    IonRefresherContent,
    IonInfiniteScroll,
    IonInfiniteScrollContent,
    IonSkeletonText,
    IonChip,
    IonFab,
    IonFabButton,
    IonToggle,
    IonButtons,
    AppHeaderComponent,
  ],
})
export class CompaniesPage implements OnInit, OnDestroy {
  // Estado de datos
  companies: Company[] = [];
  pagination: PaginationState | null = null;
  isLoading = false;
  isInitialLoading = true;
  error: string | null = null;
  searchTerm = '';
  includeInactive = true; // Por defecto incluir inactivas

  // Ordenamiento
  currentSort: 'nameCompany_asc' | 'nameCompany_desc' | 'codeCompany_asc' | 'codeCompany_desc' | 'idCompany_asc' = 'nameCompany_asc';
  sortOptions = [
    { value: 'nameCompany_asc', label: 'Nombre (A-Z)' },
    { value: 'nameCompany_desc', label: 'Nombre (Z-A)' },
    { value: 'codeCompany_asc', label: 'Código (A-Z)' },
    { value: 'codeCompany_desc', label: 'Código (Z-A)' },
    { value: 'idCompany_asc', label: 'ID (Menor a Mayor)' }
  ];

  // Configuración de UI
  skeletonItems = Array(8).fill(null); // 8 skeleton items para loading

  // Subject para búsqueda con debounce
  private searchSubject = new Subject<string>();
  private destroy$ = new Subject<void>();

  constructor(
    private companyService: CompanyService,
    private modalCtrl: ModalController,
    private alertController: AlertController,
    private toastController: ToastController
  ) {
    // Registrar iconos
    addIcons({
      businessOutline,
      createOutline,
      trashOutline,
      filterOutline,
      add,
      closeOutline,
      refresh,
      alertCircleOutline,
      addOutline,
      chevronForward,
      listOutline,
      chevronDown,
    });

    this.setupSearchDebounce();
  }

  ngOnInit() {
    this.subscribeToServiceState();
    this.loadInitialData();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    this.companyService.clearState();
  }

  /**
   * Configura el debounce para las búsquedas
   */
  private setupSearchDebounce(): void {
    this.searchSubject
      .pipe(debounceTime(500), distinctUntilChanged(), takeUntil(this.destroy$))
      .subscribe((searchTerm) => {
        this.performSearch(searchTerm);
      });
  }

  /**
   * Se suscribe al estado del servicio
   */
  private subscribeToServiceState(): void {
    // Suscribirse a las compañías
    this.companyService.companies
      .pipe(takeUntil(this.destroy$))
      .subscribe((companies) => {
        this.companies = companies;
      });

    // Suscribirse a la paginación
    this.companyService.pagination
      .pipe(takeUntil(this.destroy$))
      .subscribe((pagination) => {
        this.pagination = pagination;
      });

    // Suscribirse al estado de loading
    this.companyService.loading
      .pipe(takeUntil(this.destroy$))
      .subscribe((loading) => {
        this.isLoading = loading;
      });

    // Suscribirse a errores
    this.companyService.error
      .pipe(takeUntil(this.destroy$))
      .subscribe((error) => {
        this.error = error;
      });
  }

  /**
   * Carga los datos iniciales
   */
  private loadInitialData(): void {
    this.companyService
      .loadCompanies({
        page: 1,
        itemPerPage: 20,
        sort: this.currentSort,
        includeInactive: this.includeInactive, // Usar el valor actual del toggle
      })
      .subscribe({
        next: () => {
          this.isInitialLoading = false;
        },
        error: () => {
          this.isInitialLoading = false;
        },
      });
  }

  /**
   * Maneja el cambio en el campo de búsqueda del header
   */
  onHeaderSearch(searchTerm: string): void {
    this.searchTerm = searchTerm;
    this.searchSubject.next(searchTerm);
  }

  /**
   * Maneja el toggle del search en el header
   */
  onHeaderSearchToggle(event: any): void {
    // Implementación si es necesaria
  }

  /**
   * Maneja el cambio de ordenamiento desde el header
   */
  onSortChange(sortValue: string): void {
    const validSortValues = ['nameCompany_asc', 'nameCompany_desc', 'codeCompany_asc', 'codeCompany_desc', 'idCompany_asc'];
    if (validSortValues.includes(sortValue)) {
      this.currentSort = sortValue as 'nameCompany_asc' | 'nameCompany_desc' | 'codeCompany_asc' | 'codeCompany_desc' | 'idCompany_asc';
      this.performSearch(this.searchTerm);
    }
  }

  /**
   * Maneja el cambio en el campo de búsqueda
   */
  onSearchChange(event: SearchbarCustomEvent): void {
    const searchTerm = event.detail.value || '';
    this.searchSubject.next(searchTerm);
  }

  /**
   * Maneja la limpieza del campo de búsqueda
   */
  onSearchClear(): void {
    this.searchTerm = '';
    this.performSearch('');
  }

  /**
   * Maneja el cambio en el toggle de incluir inactivas
   */
  onIncludeInactiveChange(event: ToggleCustomEvent): void {
    this.includeInactive = event.detail.checked;

    // Recargar los datos con el nuevo filtro
    this.companyService
      .loadCompanies({
        page: 1,
        itemPerPage: 20,
        search: this.searchTerm,
        sort: this.currentSort,
        includeInactive: this.includeInactive,
      })
      .subscribe({
        next: () => {
          // Los datos se actualizan automáticamente via observables
        },
        error: (error) => {
          console.error('Error al filtrar compañías:', error);
        },
      });
  }

  /**
   * Realiza la búsqueda con el término especificado
   */
  private performSearch(searchTerm: string): void {
    this.companyService
      .loadCompanies({
        page: 1,
        itemPerPage: 20,
        search: searchTerm,
        sort: this.currentSort,
        includeInactive: this.includeInactive,
      })
      .subscribe({
        next: () => {
          // El estado se actualiza automáticamente via observables
        },
        error: (error) => {
          console.error('Error en búsqueda:', error);
        },
      });
  }

  /**
   * Maneja el pull-to-refresh
   */
  handleRefresh(event: RefresherCustomEvent): void {
    this.companyService
      .loadCompanies({
        page: 1,
        itemPerPage: 20,
        search: this.searchTerm,
        sort: this.currentSort,
        includeInactive: this.includeInactive,
      })
      .subscribe({
        next: () => {
          event.target.complete();
        },
        error: () => {
          event.target.complete();
        },
      });
  }

  /**
   * Carga más datos para infinite scroll
   */
  loadMoreData(event: InfiniteScrollCustomEvent): void {
    this.companyService.loadNextPage().subscribe({
      next: () => {
        event.target.complete();
      },
      error: () => {
        event.target.complete();
      },
    });
  }

  /**
   * Reintenta la carga de datos
   */
  retryLoad(): void {
    this.error = null;
    this.isInitialLoading = true;
    this.companyService.clearState();
    this.loadInitialData();
  }

  /**
   * Abre modal para crear nueva compañía
   */
  async onCreateCompany(): Promise<void> {
    const modal = await this.modalCtrl.create({
      component: CompanyFormModalComponent,
      componentProps: {},
      presentingElement: await this.modalCtrl.getTop(),
    });

    modal.onDidDismiss().then((result) => {
      if (result.data?.action === 'created') {
        // Ya no necesitamos hacer nada aquí porque la actualización optimista
        // se maneja directamente en el modal con el servicio
        console.log('Compañía creada:', result.data?.data);
      }
    });

    await modal.present();
  }

  /**
   * Edita una compañía
   */
  async onEditCompany(company: Company, event: Event): Promise<void> {
    event.stopPropagation();

    const modal = await this.modalCtrl.create({
      component: CompanyFormModalComponent,
      componentProps: {
        company: company,
      },
      presentingElement: await this.modalCtrl.getTop(),
    });

    modal.onDidDismiss().then((result) => {
      if (result.data?.action === 'updated') {
        // Ya no necesitamos hacer nada aquí porque la actualización optimista
        // se maneja directamente en el modal con el servicio
        console.log('Compañía actualizada:', result.data?.data);
      }
    });

    await modal.present();
  }

  /**
   * Elimina una compañía con confirmación
   */
  async onDeleteCompany(company: Company, event: Event): Promise<void> {
    event.stopPropagation();

    const alert = await this.alertController.create({
      header: 'Confirmar eliminación',
      message: `¿Está seguro de que desea eliminar la compañía "${company.nameCompany}"?`,
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel',
          cssClass: 'alert-button-cancel',
        },
        {
          text: 'Eliminar',
          cssClass: 'alert-button-danger',
          handler: async () => {
            await this.performDelete(company);
          },
        },
      ],
    });

    await alert.present();
  }

  /**
   * Ejecuta la eliminación de la compañía
   */
  private async performDelete(company: Company): Promise<void> {
    try {
      // Usar el método optimista que maneja rollback automáticamente
      const result = await this.companyService.deleteCompanyOptimistic(company.idCompany).toPromise();

      if (result && result.success) {
        const toast = await this.toastController.create({
          message: `Compañía "${company.nameCompany}" eliminada exitosamente`,
          duration: 3000,
          position: 'bottom',
          color: 'success',
          icon: 'checkmark-circle-outline',
        });
        await toast.present();
      }

    } catch (error: any) {
      console.error('Error eliminando compañía:', error);

      // El rollback ya se hizo automáticamente en el servicio
      let errorMessage = 'Error al eliminar la compañía';
      if (error.error) {
        errorMessage = error.error;
      }

      const toast = await this.toastController.create({
        message: errorMessage,
        duration: 3000,
        position: 'bottom',
        color: 'danger',
        icon: 'alert-circle-outline',
      });
      await toast.present();
    }
  }
}
