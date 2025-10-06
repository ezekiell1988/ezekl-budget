/**
 * Servicio para gestionar cuentas contables
 * Maneja la comunicación con la API de cuentas contables con paginación, búsqueda y filtros
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

// Interfaces para el servicio
export interface AccountingAccount {
  idAccountingAccount: number;
  codeAccountingAccount: string;
  nameAccountingAccount: string;
}

export interface AccountingAccountResponse {
  total: number;
  data: AccountingAccount[];
}

export interface AccountingAccountParams {
  search?: string;
  sort?: 'idAccountingAccount_asc' | 'codeAccountingAccount_asc' | 'codeAccountingAccount_desc' | 'nameAccountingAccount_asc' | 'nameAccountingAccount_desc';
  page?: number;
  itemPerPage?: number;
}

export interface PaginationState {
  currentPage: number;
  itemsPerPage: number;
  totalItems: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AccountingAccountService {
  private readonly API_BASE = '/api/accounting-accounts';

  // Estado de la lista actual
  private accounts$ = new BehaviorSubject<AccountingAccount[]>([]);
  private pagination$ = new BehaviorSubject<PaginationState>({
    currentPage: 1,
    itemsPerPage: 20,
    totalItems: 0,
    totalPages: 0,
    hasNextPage: false,
    hasPreviousPage: false
  });
  private loading$ = new BehaviorSubject<boolean>(false);
  private error$ = new BehaviorSubject<string | null>(null);

  constructor(private http: HttpClient) {}

  // Observables públicos para los componentes
  get accounts(): Observable<AccountingAccount[]> {
    return this.accounts$.asObservable();
  }

  get pagination(): Observable<PaginationState> {
    return this.pagination$.asObservable();
  }

  get loading(): Observable<boolean> {
    return this.loading$.asObservable();
  }

  get error(): Observable<string | null> {
    return this.error$.asObservable();
  }

  /**
   * Obtiene cuentas contables paginadas
   */
  getAccountingAccounts(params: AccountingAccountParams = {}): Observable<AccountingAccountResponse> {
    this.setLoading(true);
    this.setError(null);

    let httpParams = new HttpParams();

    if (params.search) {
      httpParams = httpParams.set('search', params.search);
    }
    if (params.sort) {
      httpParams = httpParams.set('sort', params.sort);
    }
    if (params.page) {
      httpParams = httpParams.set('page', params.page.toString());
    }
    if (params.itemPerPage) {
      httpParams = httpParams.set('itemPerPage', params.itemPerPage.toString());
    }

    return this.http.get<AccountingAccountResponse>(this.API_BASE, { params: httpParams })
      .pipe(
        tap(response => {
          // Actualizar estado interno
          this.updatePaginationState(response, params);
        }),
        catchError(this.handleError.bind(this)),
        tap(() => this.setLoading(false))
      );
  }

  /**
   * Obtiene una cuenta contable específica por ID
   */
  getAccountingAccountById(id: number): Observable<AccountingAccount> {
    this.setLoading(true);
    this.setError(null);

    return this.http.get<AccountingAccount>(`${this.API_BASE}/${id}`)
      .pipe(
        catchError(this.handleError.bind(this)),
        tap(() => this.setLoading(false))
      );
  }

  /**
   * Carga datos y actualiza el estado local (para uso con infinite scroll)
   */
  loadAccountingAccounts(params: AccountingAccountParams = {}, append: boolean = false): Observable<AccountingAccount[]> {
    return this.getAccountingAccounts(params).pipe(
      map(response => {
        if (append) {
          // Agregar a la lista existente (infinite scroll)
          const currentAccounts = this.accounts$.value;
          const updatedAccounts = [...currentAccounts, ...response.data];
          this.accounts$.next(updatedAccounts);
          return updatedAccounts;
        } else {
          // Reemplazar la lista (nueva búsqueda o refresh)
          this.accounts$.next(response.data);
          return response.data;
        }
      })
    );
  }

  /**
   * Busca cuentas contables por término
   */
  searchAccounts(searchTerm: string, resetPagination: boolean = true): Observable<AccountingAccount[]> {
    const params: AccountingAccountParams = {
      search: searchTerm,
      page: resetPagination ? 1 : this.pagination$.value.currentPage,
      itemPerPage: this.pagination$.value.itemsPerPage
    };

    return this.loadAccountingAccounts(params, !resetPagination);
  }

  /**
   * Carga la siguiente página (infinite scroll)
   */
  loadNextPage(): Observable<AccountingAccount[]> {
    const currentPagination = this.pagination$.value;

    if (!currentPagination.hasNextPage) {
      return throwError(() => new Error('No hay más páginas disponibles'));
    }

    const params: AccountingAccountParams = {
      page: currentPagination.currentPage + 1,
      itemPerPage: currentPagination.itemsPerPage
    };

    return this.loadAccountingAccounts(params, true);
  }

  /**
   * Refresca la lista actual (pull to refresh)
   */
  refreshAccounts(currentSearch?: string): Observable<AccountingAccount[]> {
    const params: AccountingAccountParams = {
      search: currentSearch,
      page: 1,
      itemPerPage: this.pagination$.value.itemsPerPage
    };

    return this.loadAccountingAccounts(params, false);
  }

  /**
   * Limpia el estado actual
   */
  clearState(): void {
    this.accounts$.next([]);
    this.pagination$.next({
      currentPage: 1,
      itemsPerPage: 20,
      totalItems: 0,
      totalPages: 0,
      hasNextPage: false,
      hasPreviousPage: false
    });
    this.setError(null);
    this.setLoading(false);
  }

  // Métodos privados para gestión de estado
  private updatePaginationState(response: AccountingAccountResponse, params: AccountingAccountParams): void {
    const currentPage = params.page || 1;
    const itemsPerPage = params.itemPerPage || 20;
    const totalPages = Math.ceil(response.total / itemsPerPage);

    this.pagination$.next({
      currentPage,
      itemsPerPage,
      totalItems: response.total,
      totalPages,
      hasNextPage: currentPage < totalPages,
      hasPreviousPage: currentPage > 1
    });
  }

  private setLoading(loading: boolean): void {
    this.loading$.next(loading);
  }

  private setError(error: string | null): void {
    this.error$.next(error);
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'Error desconocido';

    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Error del lado del servidor
      switch (error.status) {
        case 401:
          errorMessage = 'No tiene autorización para acceder a este recurso';
          break;
        case 404:
          errorMessage = 'Recurso no encontrado';
          break;
        case 500:
          errorMessage = 'Error interno del servidor';
          break;
        default:
          errorMessage = `Error ${error.status}: ${error.error?.detail || error.message}`;
      }
    }

    console.error('Error en AccountingAccountService:', error);
    this.setError(errorMessage);
    this.setLoading(false);

    return throwError(() => new Error(errorMessage));
  }
}
