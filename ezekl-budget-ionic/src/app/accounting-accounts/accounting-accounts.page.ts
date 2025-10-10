/**
 * Página de Cuentas Contables
 * Muestra una lista paginada de cuentas contables con funcionalidades de:
 * - Búsqueda en tiempo real
 * - Pull to refresh
 * - Infinite scroll
 * - Skeleton loading
 * - Manejo de errores
 */

import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonContent,
  IonHeader,
  IonTitle,
  IonToolbar,
  IonGrid,
  // IonRow, // No usado
  // IonCol, // No usado
  IonSearchbar,
  IonList,
  IonItem,
  IonLabel,
  IonIcon,
  IonText,
  IonButton,
  IonCard,
  IonCardContent,
  IonRefresher,
  IonRefresherContent,
  IonInfiniteScroll,
  IonInfiniteScrollContent,
  IonSkeletonText,
  RefresherCustomEvent,
  InfiniteScrollCustomEvent,
  SearchbarCustomEvent,
  ModalController
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  documentTextOutline,
  alertCircleOutline,
  refresh,
  chevronForward
} from 'ionicons/icons';
import { AppHeaderComponent } from '../shared/components/app-header/app-header.component';
import { AccountDetailModalComponent } from './account-detail-modal/account-detail-modal.component';
import { AccountingAccountService, AccountingAccount, PaginationState } from '../services/accounting-account';
import { Subject, takeUntil, debounceTime, distinctUntilChanged } from 'rxjs';

@Component({
  selector: 'app-accounting-accounts',
  templateUrl: './accounting-accounts.page.html',
  styleUrls: ['./accounting-accounts.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonContent,
    IonHeader,
    IonTitle,
    IonToolbar,
    IonGrid,
    // IonRow, // No usado en template
    // IonCol, // No usado en template
    IonSearchbar,
    IonList,
    IonItem,
    IonLabel,
    IonIcon,
    IonText,
    IonButton,
    IonCard,
    IonCardContent,
    IonRefresher,
    IonRefresherContent,
    IonInfiniteScroll,
    IonInfiniteScrollContent,
    IonSkeletonText,
    AppHeaderComponent
  ]
})
export class AccountingAccountsPage implements OnInit, OnDestroy {
  // Estado de datos
  accounts: AccountingAccount[] = [];
  pagination: PaginationState | null = null;
  isLoading = false;
  isInitialLoading = true;
  error: string | null = null;
  searchTerm = '';

  // Configuración de UI
  skeletonItems = Array(8).fill(null); // 8 skeleton items para loading

  // Subject para búsqueda con debounce
  private searchSubject = new Subject<string>();
  private destroy$ = new Subject<void>();

  constructor(
    private accountService: AccountingAccountService,
    private modalCtrl: ModalController
  ) {
    // Registrar iconos
    addIcons({
      documentTextOutline,
      alertCircleOutline,
      refresh,
      chevronForward
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
    this.accountService.clearState();
  }

  /**
   * Configura el debounce para las búsquedas
   */
  private setupSearchDebounce(): void {
    this.searchSubject
      .pipe(
        debounceTime(500),
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
  private subscribeToServiceState(): void {
    // Suscribirse a las cuentas
    this.accountService.accounts
      .pipe(takeUntil(this.destroy$))
      .subscribe(accounts => {
        this.accounts = accounts;
      });

    // Suscribirse a la paginación
    this.accountService.pagination
      .pipe(takeUntil(this.destroy$))
      .subscribe(pagination => {
        this.pagination = pagination;
      });

    // Suscribirse al estado de loading
    this.accountService.loading
      .pipe(takeUntil(this.destroy$))
      .subscribe(loading => {
        this.isLoading = loading;
      });

    // Suscribirse a errores
    this.accountService.error
      .pipe(takeUntil(this.destroy$))
      .subscribe(error => {
        this.error = error;
      });
  }

  /**
   * Carga los datos iniciales
   */
  private loadInitialData(): void {
    this.isInitialLoading = true;

    this.accountService.loadAccountingAccounts()
      .subscribe({
        next: () => {
          this.isInitialLoading = false;
        },
        error: (error) => {
          this.isInitialLoading = false;
          console.error('Error cargando datos iniciales:', error);
        }
      });
  }

  /**
   * Maneja el cambio en el campo de búsqueda
   */
  onSearchChange(event: SearchbarCustomEvent): void {
    const searchTerm = event.detail.value || '';
    this.searchTerm = searchTerm;
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
   * Realiza la búsqueda con el término especificado
   */
  private performSearch(searchTerm: string): void {
    this.accountService.searchAccounts(searchTerm, true)
      .subscribe({
        error: (error) => {
          console.error('Error en búsqueda:', error);
        }
      });
  }

  /**
   * Maneja el pull-to-refresh
   */
  handleRefresh(event: RefresherCustomEvent): void {
    this.accountService.refreshAccounts(this.searchTerm)
      .subscribe({
        next: () => {
          event.target.complete();
        },
        error: (error) => {
          console.error('Error en refresh:', error);
          event.target.complete();
        }
      });
  }

  /**
   * Carga más datos para infinite scroll
   */
  loadMoreData(event: InfiniteScrollCustomEvent): void {
    this.accountService.loadNextPage()
      .subscribe({
        next: () => {
          event.target.complete();
        },
        error: (error) => {
          console.error('Error cargando más datos:', error);
          event.target.complete();
        }
      });
  }

  /**
   * Maneja el click en una cuenta contable
   * Abre un modal con los detalles de la cuenta
   */
  async onAccountClick(account: AccountingAccount): Promise<void> {
    console.log('Cuenta seleccionada:', account);

    const modal = await this.modalCtrl.create({
      component: AccountDetailModalComponent,
      componentProps: {
        account: account
      },
      breakpoints: [0, 0.5, 0.75, 1],
      initialBreakpoint: 0.75
    });

    await modal.present();
  }

  /**
   * Reintenta la carga de datos
   */
  retryLoad(): void {
    this.error = null;
    if (this.searchTerm) {
      this.performSearch(this.searchTerm);
    } else {
      this.loadInitialData();
    }
  }
}
