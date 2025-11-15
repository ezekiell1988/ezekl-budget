/**
 * Servicio para gestionar cuentas contables
 * Maneja la comunicación con la API de cuentas contables con paginación, búsqueda y filtros
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

// Interfaces para el servicio
export interface AccountingAccount {
  idAccountingAccount: number;
  idAccountingAccountFather?: number;
  codeAccountingAccount: string;
  nameAccountingAccount: string;
  active: boolean;
  children?: AccountingAccount[];
}

export interface AccountingAccountResponse {
  total: number;
  data: AccountingAccount[];
}

export interface AccountingAccountParams {
  search?: string;
  sort?: 'idAccountingAccount_asc' | 'idAccountingAccountFather_asc' | 'idAccountingAccountFather_desc' | 'codeAccountingAccount_asc' | 'codeAccountingAccount_desc' | 'nameAccountingAccount_asc' | 'nameAccountingAccount_desc';
  page?: number;
  itemPerPage?: number;
  includeInactive?: boolean;
}

export interface AccountingAccountCreateRequest {
  idAccountingAccountFather?: number;
  codeAccountingAccount: string;
  nameAccountingAccount: string;
}

export interface AccountingAccountUpdateRequest {
  idAccountingAccountFather?: number;
  codeAccountingAccount?: string;
  nameAccountingAccount?: string;
}

export interface AccountingAccountCreateResponse {
  idAccountingAccount: number;
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
  private readonly API_BASE: string;

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

  // Estado actual de filtros (para infinite scroll)
  private currentFilters: AccountingAccountParams = {};

  constructor(private http: HttpClient) {
    this.API_BASE = `${environment.apiUrl}/api/accounting-accounts`;
  }

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
    if (params.includeInactive !== undefined) {
      httpParams = httpParams.set('includeInactive', params.includeInactive.toString());
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
    // Guardar filtros actuales para infinite scroll
    if (!append) {
      this.currentFilters = { ...params };
    }

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
      ...this.currentFilters, // Usar los filtros actuales
      page: currentPagination.currentPage + 1,
      itemPerPage: currentPagination.itemsPerPage
    };

    return this.loadAccountingAccounts(params, true);
  }

  /**
   * Refresca la lista actual (pull to refresh)
   */
  refreshAccounts(currentSearch?: string, includeInactive: boolean = false): Observable<AccountingAccount[]> {
    const params: AccountingAccountParams = {
      search: currentSearch,
      page: 1,
      itemPerPage: this.pagination$.value.itemsPerPage,
      includeInactive: includeInactive
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

  /**
   * Crea una nueva cuenta contable
   */
  createAccountingAccount(accountData: AccountingAccountCreateRequest): Observable<AccountingAccountCreateResponse> {
    this.setLoading(true);
    this.setError(null);

    return this.http.post<AccountingAccountCreateResponse>(this.API_BASE, accountData)
      .pipe(
        catchError(this.handleError.bind(this)),
        tap(() => this.setLoading(false))
      );
  }

  /**
   * Actualiza una cuenta contable existente
   */
  updateAccountingAccount(id: number, accountData: AccountingAccountUpdateRequest): Observable<{ message: string }> {
    this.setLoading(true);
    this.setError(null);

    return this.http.put<{ message: string }>(`${this.API_BASE}/${id}`, accountData)
      .pipe(
        catchError(this.handleError.bind(this)),
        tap(() => this.setLoading(false))
      );
  }

  /**
   * Elimina una cuenta contable
   */
  deleteAccountingAccount(id: number): Observable<{ message: string }> {
    this.setLoading(true);
    this.setError(null);

    return this.http.delete<{ message: string }>(`${this.API_BASE}/${id}`)
      .pipe(
        catchError(this.handleError.bind(this)),
        tap(() => this.setLoading(false))
      );
  }

  /**
   * Crea una cuenta contable con actualización optimista del estado local
   */
  createAccountingAccountOptimistic(accountData: AccountingAccountCreateRequest): Observable<{
    success: boolean;
    account?: AccountingAccount;
    error?: string;
  }> {
    return this.createAccountingAccount(accountData).pipe(
      map(response => {
        // Crear el objeto de cuenta contable para el estado local
        const newAccount: AccountingAccount = {
          idAccountingAccount: response.idAccountingAccount,
          idAccountingAccountFather: accountData.idAccountingAccountFather,
          codeAccountingAccount: accountData.codeAccountingAccount,
          nameAccountingAccount: accountData.nameAccountingAccount,
          active: true,
          children: []
        };

        // Agregar al estado local
        const currentAccounts = this.accounts$.value;
        this.accounts$.next([...currentAccounts, newAccount]);

        // Actualizar el total en paginación
        const currentPagination = this.pagination$.value;
        this.pagination$.next({
          ...currentPagination,
          totalItems: currentPagination.totalItems + 1
        });

        return {
          success: true,
          account: newAccount
        };
      }),
      catchError(error => {
        // En caso de error, no modificar el estado local
        return throwError(() => ({
          success: false,
          error: error.message
        }));
      })
    );
  }

  /**
   * Actualiza una cuenta contable con actualización optimista del estado local
   */
  updateAccountingAccountOptimistic(id: number, accountData: AccountingAccountUpdateRequest): Observable<{
    success: boolean;
    account?: AccountingAccount;
    error?: string;
  }> {
    // Guardar estado anterior para rollback
    const currentAccounts = this.accounts$.value;

    // Función para buscar y actualizar recursivamente
    const findAndUpdateRecursive = (accounts: AccountingAccount[], targetId: number): { found: boolean; updated?: AccountingAccount } => {
      for (let i = 0; i < accounts.length; i++) {
        if (accounts[i].idAccountingAccount === targetId) {
          const originalAccount = { ...accounts[i] };
          const updatedAccount: AccountingAccount = {
            ...originalAccount,
            ...(accountData.idAccountingAccountFather !== undefined && { idAccountingAccountFather: accountData.idAccountingAccountFather }),
            ...(accountData.codeAccountingAccount && { codeAccountingAccount: accountData.codeAccountingAccount }),
            ...(accountData.nameAccountingAccount && { nameAccountingAccount: accountData.nameAccountingAccount })
          };
          accounts[i] = updatedAccount;
          return { found: true, updated: updatedAccount };
        }

        if (accounts[i].children && accounts[i].children && accounts[i].children!.length > 0) {
          const result = findAndUpdateRecursive(accounts[i].children!, targetId);
          if (result.found) {
            return result;
          }
        }
      }
      return { found: false };
    };

    // Crear copia profunda para actualización optimista
    const optimisticAccounts = JSON.parse(JSON.stringify(currentAccounts));
    const updateResult = findAndUpdateRecursive(optimisticAccounts, id);

    if (!updateResult.found) {
      // Si no se encuentra en el estado local, intentar llamar al API directamente
      return this.updateAccountingAccount(id, accountData).pipe(
        map(() => ({
          success: true,
          account: undefined // No tenemos la cuenta actualizada localmente
        })),
        catchError(error => {
          return throwError(() => ({
            success: false,
            error: error.message
          }));
        })
      );
    }

    // Actualizar optimísticamente
    this.accounts$.next(optimisticAccounts);

    return this.updateAccountingAccount(id, accountData).pipe(
      map(() => ({
        success: true,
        account: updateResult.updated
      })),
      catchError(error => {
        // Rollback en caso de error
        this.accounts$.next(currentAccounts);

        return throwError(() => ({
          success: false,
          error: error.message
        }));
      })
    );
  }  /**
   * Elimina una cuenta contable con actualización optimista del estado local
   */
  deleteAccountingAccountOptimistic(id: number): Observable<{
    success: boolean;
    error?: string;
  }> {
    // Guardar estado anterior para rollback
    const currentAccounts = this.accounts$.value;

    // Buscar la cuenta recursivamente en la estructura jerárquica
    const findAccountRecursive = (accounts: AccountingAccount[], targetId: number): { found: boolean; account?: AccountingAccount } => {
      for (const account of accounts) {
        if (account.idAccountingAccount === targetId) {
          return { found: true, account };
        }
        if (account.children && account.children.length > 0) {
          const result = findAccountRecursive(account.children, targetId);
          if (result.found) {
            return result;
          }
        }
      }
      return { found: false };
    };

    const searchResult = findAccountRecursive(currentAccounts, id);

    if (!searchResult.found) {
      // Si no se encuentra en el estado local, intentar llamar al API directamente
      return this.deleteAccountingAccount(id).pipe(
        map(() => ({
          success: true
        })),
        catchError(error => {
          return throwError(() => ({
            success: false,
            error: error.message
          }));
        })
      );
    }

    // Función para eliminar recursivamente de la estructura jerárquica
    const removeAccountRecursive = (accounts: AccountingAccount[], targetId: number): AccountingAccount[] => {
      return accounts.filter(account => {
        if (account.idAccountingAccount === targetId) {
          return false; // Eliminar esta cuenta
        }
        if (account.children && account.children.length > 0) {
          account.children = removeAccountRecursive(account.children, targetId);
        }
        return true;
      });
    };

    // Eliminar optimísticamente
    const optimisticAccounts = removeAccountRecursive([...currentAccounts], id);
    this.accounts$.next(optimisticAccounts);

    // Actualizar el total en paginación
    const currentPagination = this.pagination$.value;
    this.pagination$.next({
      ...currentPagination,
      totalItems: Math.max(0, currentPagination.totalItems - 1)
    });

    return this.deleteAccountingAccount(id).pipe(
      map(() => ({
        success: true
      })),
      catchError(error => {
        // Rollback en caso de error
        this.accounts$.next(currentAccounts);
        this.pagination$.next(currentPagination);

        return throwError(() => ({
          success: false,
          error: error.message
        }));
      })
    );
  }  // Métodos privados para gestión de estado
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
