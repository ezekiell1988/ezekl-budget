import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonContent,
  IonGrid,
  IonList,
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
  IonLabel,
  IonIcon,
  IonButton,
  IonButtons,
  IonAccordion,
  IonAccordionGroup,
  IonItem,
  IonFab,
  IonFabButton,
  IonToggle,
  RefresherCustomEvent,
  InfiniteScrollCustomEvent,
  ModalController,
  AlertController,
  ToastController
} from '@ionic/angular/standalone';

import { addIcons } from 'ionicons';
import {
  calculatorOutline,
  filterOutline,
  chevronDown,
  folderOutline,
  listOutline,
  createOutline,
  trashOutline,
  gitBranchOutline,
  chevronForwardOutline,
  checkmarkCircle,
  closeCircle,
  folder,
  documentOutline,
  add,
  chevronForward
} from 'ionicons/icons';

import { AppHeaderComponent } from '../shared/components/app-header/app-header.component';
import { AccountingAccount, AccountingAccountService, PaginationState } from '../services/accounting-account';
import { AccountFormModalComponent } from './account-form-modal/account-form-modal.component';
import { Subject } from 'rxjs';
import { takeUntil, debounceTime, distinctUntilChanged } from 'rxjs/operators';

@Component({
  selector: 'app-accounting-accounts',
  templateUrl: './accounting-accounts.page.html',
  styleUrls: ['./accounting-accounts.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    AppHeaderComponent,
    IonContent,
    IonGrid,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonList,
    IonSkeletonText,
    IonRefresher,
    IonRefresherContent,
    IonInfiniteScroll,
    IonInfiniteScrollContent,
    IonChip,
    IonLabel,
    IonIcon,
    IonButton,
    IonButtons,
    IonAccordion,
    IonAccordionGroup,
    IonItem,
    IonFab,
    IonFabButton,
    IonToggle
  ]
})
export class AccountingAccountsPage implements OnInit, OnDestroy {
  // Servicios
  private accountService = inject(AccountingAccountService);
  private modalCtrl = inject(ModalController);
  private alertController = inject(AlertController);
  private toastController = inject(ToastController);
  private destroy$ = new Subject<void>();

  // Estado de datos
  accounts: AccountingAccount[] = [];
  pagination: PaginationState | null = null;
  isLoading = false;
  searchTerm = '';
  includeInactive = true; // Por defecto incluir inactivas

  // Ordenamiento
  currentSort: 'idAccountingAccount_asc' | 'idAccountingAccountFather_asc' | 'idAccountingAccountFather_desc' | 'codeAccountingAccount_asc' | 'codeAccountingAccount_desc' | 'nameAccountingAccount_asc' | 'nameAccountingAccount_desc' = 'nameAccountingAccount_asc';
  sortOptions = [
    { value: 'nameAccountingAccount_asc', label: 'Nombre (A-Z)' },
    { value: 'nameAccountingAccount_desc', label: 'Nombre (Z-A)' },
    { value: 'codeAccountingAccount_asc', label: 'Código (A-Z)' },
    { value: 'codeAccountingAccount_desc', label: 'Código (Z-A)' },
    { value: 'idAccountingAccount_asc', label: 'ID (Menor a Mayor)' },
    { value: 'idAccountingAccountFather_asc', label: 'Padre ID (Menor a Mayor)' },
    { value: 'idAccountingAccountFather_desc', label: 'Padre ID (Mayor a Menor)' }
  ];

  // Subject para búsqueda con debounce
  private searchSubject = new Subject<string>();

  constructor() {
    // Registrar iconos
    addIcons({
      folder,
      listOutline,
      createOutline,
      trashOutline,
      gitBranchOutline,
      chevronForwardOutline,
      calculatorOutline,
      filterOutline,
      chevronDown,
      folderOutline,
      checkmarkCircle,
      closeCircle,
      documentOutline,
      add,
      chevronForward
    });
  }

  ngOnInit() {
    this.setupSearch();
    this.subscribeToService();
    this.loadInitialData();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Determina si una cuenta tiene hijos
   */
  hasChildren(account: AccountingAccount): boolean {
    return !!(account.children && account.children.length > 0);
  }

  /**
   * Obtiene indicadores visuales para mostrar el nivel de jerarquía
   */
  getHierarchyIndicators(level: number): number[] {
    return Array.from({length: level}, (_, i) => i);
  }

  /**
   * Obtiene el valor único del acordeón para una cuenta
   */
  getAccordionValue(account: AccountingAccount): string {
    return `account-${account.idAccountingAccount}`;
  }

  /**
   * Maneja la expansión/colapso de acordeones
   */
  onAccordionChange(event: any): void {
    // Aquí se puede agregar lógica adicional si es necesaria
    // como cargar datos dinámicamente al expandir
  }

  /**
   * Configura el debounce para las búsquedas
   */
  private setupSearch(): void {
    this.searchSubject
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        takeUntil(this.destroy$)
      )
      .subscribe(searchTerm => {
        this.performSearch(searchTerm);
      });
  }

  /**
   * Se suscribe al estado del servicio
   */
  private subscribeToService(): void {
    this.accountService.accounts
      .pipe(takeUntil(this.destroy$))
      .subscribe(accounts => {
        this.accounts = accounts;
      });

    this.accountService.pagination
      .pipe(takeUntil(this.destroy$))
      .subscribe(pagination => {
        this.pagination = pagination;
      });

    this.accountService.loading
      .pipe(takeUntil(this.destroy$))
      .subscribe(loading => {
        this.isLoading = loading;
      });
  }

  /**
   * Carga los datos iniciales
   */
  private loadInitialData(): void {
    this.accountService.loadAccountingAccounts({
      page: 1,
      itemPerPage: 20,
      sort: this.currentSort,
      includeInactive: this.includeInactive
    }).pipe(takeUntil(this.destroy$)).subscribe();
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
    // Implementar si es necesario
  }

  /**
   * Maneja el cambio de ordenamiento desde el header
   */
  onSortChange(sortValue: string): void {
    this.currentSort = sortValue as any;
    this.accountService.loadAccountingAccounts({
      page: 1,
      itemPerPage: 20,
      sort: this.currentSort,
      search: this.searchTerm,
      includeInactive: this.includeInactive
    }).pipe(takeUntil(this.destroy$)).subscribe();
  }

  /**
   * Realiza la búsqueda con el término especificado
   */
  private performSearch(searchTerm: string): void {
    this.accountService.loadAccountingAccounts({
      page: 1,
      itemPerPage: 20,
      search: searchTerm,
      sort: this.currentSort,
      includeInactive: this.includeInactive
    }).pipe(takeUntil(this.destroy$)).subscribe();
  }

  /**
   * Maneja el pull-to-refresh
   */
  handleRefresh(event: RefresherCustomEvent): void {
    this.accountService.refreshAccounts(this.searchTerm, this.includeInactive)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          event.target.complete();
        },
        error: () => {
          event.target.complete();
        }
      });
  }

  /**
   * Carga más datos para infinite scroll
   */
  loadMoreData(event: InfiniteScrollCustomEvent): void {
    this.accountService.loadNextPage()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          event.target.complete();
        },
        error: () => {
          event.target.complete();
        }
      });
  }

  /**
   * Reintenta la carga de datos
   */
  retryLoad(): void {
    this.searchTerm = '';
    this.accountService.loadAccountingAccounts({
      page: 1,
      itemPerPage: 20,
      sort: this.currentSort,
      includeInactive: this.includeInactive
    }).pipe(takeUntil(this.destroy$)).subscribe();
  }

  /**
   * Maneja la gestión de subcuentas
   */
  onManageChildren(account: AccountingAccount, event: Event): void {
    event.stopPropagation(); // Prevenir la propagación del evento
    // TODO: Implementar la navegación a la gestión de subcuentas
    console.log('Gestionar subcuentas de:', account);
  }

  /**
   * Maneja la creación de una nueva cuenta contable
   */
  async onCreateAccount(): Promise<void> {
    const modal = await this.modalCtrl.create({
      component: AccountFormModalComponent,
      componentProps: {
        availableParentAccounts: this.getFlattenedAccounts()
      }
    });

    modal.onDidDismiss().then((result) => {
      if (result.data && result.data.action === 'created') {
        // Recargar datos para reflejar la nueva cuenta
        this.loadInitialData();
      }
    });

    await modal.present();
  }

  /**
   * Maneja la edición de una cuenta contable
   */
  async onEditAccount(account: AccountingAccount, event: Event): Promise<void> {
    event.stopPropagation(); // Prevenir la propagación del evento

    const modal = await this.modalCtrl.create({
      component: AccountFormModalComponent,
      componentProps: {
        account: account,
        availableParentAccounts: this.getFlattenedAccounts().filter(acc => acc.idAccountingAccount !== account.idAccountingAccount)
      }
    });

    modal.onDidDismiss().then((result) => {
      if (result.data && result.data.action === 'updated') {
        // Recargar datos para reflejar los cambios
        this.loadInitialData();
      }
    });

    await modal.present();
  }

  /**
   * Maneja la eliminación de una cuenta contable
   */
  async onDeleteAccount(account: AccountingAccount, event: Event): Promise<void> {
    event.stopPropagation(); // Prevenir la propagación del evento

    const hasChildren = account.children && account.children.length > 0;

    const alert = await this.alertController.create({
      header: 'Confirmar Eliminación',
      message: hasChildren
        ? `¿Está seguro que desea eliminar la cuenta "${account.nameAccountingAccount}"? Esta cuenta tiene ${account.children!.length} subcuenta(s) dependiente(s) que también serán afectadas.`
        : `¿Está seguro que desea eliminar la cuenta "${account.nameAccountingAccount}"? Esta acción no se puede deshacer.`,
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

  /**
   * Ejecuta la eliminación de la cuenta contable
   */
  private async performDelete(account: AccountingAccount): Promise<void> {
    try {
      const result = await this.accountService.deleteAccountingAccountOptimistic(account.idAccountingAccount).toPromise();

      if (result && result.success) {
        const toast = await this.toastController.create({
          message: `Cuenta contable "${account.nameAccountingAccount}" eliminada exitosamente`,
          duration: 3000,
          color: 'success',
          position: 'top'
        });
        await toast.present();

        // No necesitamos recargar porque el servicio ya actualizó el estado optimísticamente
      }

    } catch (error: any) {
      console.error('Error eliminando cuenta contable:', error);

      let errorMessage = 'Error al eliminar la cuenta contable';
      if (error.message) {
        errorMessage = error.message;
      }

      const toast = await this.toastController.create({
        message: errorMessage,
        duration: 5000,
        color: 'danger',
        position: 'top'
      });
      await toast.present();

      // El rollback ya se hizo automáticamente en el servicio
    }
  }

  /**
   * Obtiene una lista plana de todas las cuentas contables para usar como opciones padre
   */
  private getFlattenedAccounts(): AccountingAccount[] {
    const flattenAccounts = (accounts: AccountingAccount[]): AccountingAccount[] => {
      let result: AccountingAccount[] = [];

      accounts.forEach(account => {
        result.push(account);
        if (account.children && account.children.length > 0) {
          result = result.concat(flattenAccounts(account.children));
        }
      });

      return result;
    };

    return flattenAccounts(this.accounts);
  }

  /**
   * Maneja el cambio en el toggle de incluir inactivas
   */
  onIncludeInactiveChange(event: any): void {
    this.includeInactive = event.detail.checked;
    // Recargar datos con el nuevo filtro
    this.accountService.loadAccountingAccounts({
      page: 1,
      itemPerPage: 20,
      sort: this.currentSort,
      search: this.searchTerm,
      includeInactive: this.includeInactive
    }).pipe(takeUntil(this.destroy$)).subscribe();
  }
}
