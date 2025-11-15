/**
 * Servicio para gestionar compañías
 * Maneja la comunicación con la API de compañías con paginación, búsqueda y filtros
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

// Interfaces para el servicio
export interface Company {
  idCompany: number;
  codeCompany: string;
  nameCompany: string;
  descriptionCompany: string;
  active: boolean;
}

export interface CompanyCreateRequest {
  codeCompany: string;
  nameCompany: string;
  descriptionCompany: string;
}

export interface CompanyUpdateRequest {
  codeCompany?: string;
  nameCompany?: string;
  descriptionCompany?: string;
}

export interface CompanyCreateResponse {
  idCompany: number;
}

export interface CompanyResponse {
  total: number;
  data: Company[];
}

export interface CompanyParams {
  search?: string;
  sort?: 'idCompany_asc' | 'codeCompany_asc' | 'codeCompany_desc' | 'nameCompany_asc' | 'nameCompany_desc';
  page?: number;
  itemPerPage?: number;
  includeInactive?: boolean;
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
export class CompanyService {
  private readonly API_BASE = '/api/companies';

  // Estado de la lista actual
  private companies$ = new BehaviorSubject<Company[]>([]);
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
  get companies(): Observable<Company[]> {
    return this.companies$.asObservable();
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
   * Obtiene compañías paginadas
   */
  getCompanies(params: CompanyParams = {}): Observable<CompanyResponse> {
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

    return this.http.get<CompanyResponse>(this.API_BASE, { params: httpParams })
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
   * Obtiene una compañía específica por ID
   */
  getCompanyById(id: number): Observable<Company> {
    this.setLoading(true);
    this.setError(null);

    return this.http.get<Company>(`${this.API_BASE}/${id}`)
      .pipe(
        catchError(this.handleError.bind(this)),
        tap(() => this.setLoading(false))
      );
  }

  /**
   * Carga datos y actualiza el estado local (para uso con infinite scroll)
   */
  loadCompanies(params: CompanyParams = {}, append: boolean = false): Observable<Company[]> {
    return this.getCompanies(params).pipe(
      map(response => {
        if (append) {
          // Agregar a la lista existente (infinite scroll)
          const currentCompanies = this.companies$.value;
          const updatedCompanies = [...currentCompanies, ...response.data];
          this.companies$.next(updatedCompanies);
          return updatedCompanies;
        } else {
          // Reemplazar la lista (nueva búsqueda o refresh)
          this.companies$.next(response.data);
          return response.data;
        }
      })
    );
  }

  /**
   * Busca compañías por término
   */
  searchCompanies(searchTerm: string, resetPagination: boolean = true): Observable<Company[]> {
    const params: CompanyParams = {
      search: searchTerm,
      page: resetPagination ? 1 : this.pagination$.value.currentPage,
      itemPerPage: this.pagination$.value.itemsPerPage
    };

    return this.loadCompanies(params, !resetPagination);
  }

  /**
   * Carga la siguiente página (infinite scroll)
   */
  loadNextPage(): Observable<Company[]> {
    const currentPagination = this.pagination$.value;

    if (!currentPagination.hasNextPage) {
      return throwError(() => new Error('No hay más páginas disponibles'));
    }

    const params: CompanyParams = {
      page: currentPagination.currentPage + 1,
      itemPerPage: currentPagination.itemsPerPage
    };

    return this.loadCompanies(params, true);
  }

  /**
   * Refresca la lista actual (pull to refresh)
   */
  refreshCompanies(currentSearch?: string): Observable<Company[]> {
    const params: CompanyParams = {
      search: currentSearch,
      page: 1,
      itemPerPage: this.pagination$.value.itemsPerPage
    };

    return this.loadCompanies(params, false);
  }

  /**
   * Limpia el estado actual
   */
  clearState(): void {
    this.companies$.next([]);
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
   * Crea una nueva compañía
   */
  createCompany(companyData: CompanyCreateRequest): Observable<CompanyCreateResponse> {
    this.setLoading(true);
    this.setError(null);

    return this.http.post<CompanyCreateResponse>(this.API_BASE, companyData)
      .pipe(
        catchError(this.handleError.bind(this)),
        tap(() => this.setLoading(false))
      );
  }

  /**
   * Actualiza una compañía existente
   */
  updateCompany(id: number, companyData: CompanyUpdateRequest): Observable<void> {
    this.setLoading(true);
    this.setError(null);

    return this.http.put<void>(`${this.API_BASE}/${id}`, companyData)
      .pipe(
        catchError(this.handleError.bind(this)),
        tap(() => this.setLoading(false))
      );
  }

  /**
   * Elimina una compañía (soft delete)
   */
  deleteCompany(id: number): Observable<void> {
    this.setLoading(true);
    this.setError(null);

    return this.http.delete<void>(`${this.API_BASE}/${id}`)
      .pipe(
        catchError(this.handleError.bind(this)),
        tap(() => this.setLoading(false))
      );
  }

  /**
   * Actualiza el estado local después de crear una compañía
   * @param newCompany Los datos de la nueva compañía (incluyendo el ID del servidor)
   */
  addCompanyToLocalState(newCompany: Company): void {
    const currentCompanies = this.companies$.value;
    const updatedCompanies = [newCompany, ...currentCompanies];
    this.companies$.next(updatedCompanies);

    // Actualizar la paginación para reflejar el nuevo total
    const currentPagination = this.pagination$.value;
    this.pagination$.next({
      ...currentPagination,
      totalItems: currentPagination.totalItems + 1
    });
  }

  /**
   * Actualiza el estado local después de editar una compañía
   * @param updatedCompany Los datos actualizados de la compañía
   */
  updateCompanyInLocalState(updatedCompany: Company): void {
    const currentCompanies = this.companies$.value;
    const updatedCompanies = currentCompanies.map(company =>
      company.idCompany === updatedCompany.idCompany ? updatedCompany : company
    );
    this.companies$.next(updatedCompanies);
  }

  /**
   * Elimina una compañía del estado local
   * @param companyId ID de la compañía a eliminar
   */
  removeCompanyFromLocalState(companyId: number): void {
    const currentCompanies = this.companies$.value;
    const updatedCompanies = currentCompanies.filter(company => company.idCompany !== companyId);
    this.companies$.next(updatedCompanies);

    // Actualizar la paginación para reflejar el nuevo total
    const currentPagination = this.pagination$.value;
    this.pagination$.next({
      ...currentPagination,
      totalItems: currentPagination.totalItems - 1
    });
  }

  /**
   * Crea una compañía con actualización optimista
   * @param companyData Datos de la nueva compañía
   * @returns Observable con el resultado y función de rollback
   */
  createCompanyOptimistic(companyData: CompanyCreateRequest): Observable<{ success: boolean; company?: Company; error?: string }> {
    this.setLoading(true);
    this.setError(null);

    // Crear compañía temporal para mostrar inmediatamente
    const tempCompany: Company = {
      idCompany: Date.now(), // ID temporal hasta que llegue el real
      codeCompany: companyData.codeCompany,
      nameCompany: companyData.nameCompany,
      descriptionCompany: companyData.descriptionCompany,
      active: true
    };

    // Guardar estado actual para rollback
    const originalCompanies = [...this.companies$.value];
    const originalPagination = { ...this.pagination$.value };

    // Agregar optimistamente
    this.addCompanyToLocalState(tempCompany);

    return this.http.post<CompanyCreateResponse>(this.API_BASE, companyData)
      .pipe(
        map(response => {
          // Actualizar con el ID real del servidor
          const realCompany: Company = {
            ...tempCompany,
            idCompany: response.idCompany
          };

          // Reemplazar la compañía temporal con la real
          const currentCompanies = this.companies$.value;
          const updatedCompanies = currentCompanies.map(company =>
            company.idCompany === tempCompany.idCompany ? realCompany : company
          );
          this.companies$.next(updatedCompanies);

          this.setLoading(false);
          return { success: true, company: realCompany };
        }),
        catchError(error => {
          // Rollback en caso de error
          this.companies$.next(originalCompanies);
          this.pagination$.next(originalPagination);

          const errorMessage = this.extractErrorMessage(error);
          this.setError(errorMessage);
          this.setLoading(false);

          return throwError(() => ({ success: false, error: errorMessage }));
        })
      );
  }

  /**
   * Actualiza una compañía con actualización optimista
   * @param id ID de la compañía a actualizar
   * @param companyData Datos actualizados
   * @returns Observable con el resultado y función de rollback
   */
  updateCompanyOptimistic(id: number, companyData: CompanyUpdateRequest): Observable<{ success: boolean; company?: Company; error?: string }> {
    this.setLoading(true);
    this.setError(null);

    // Guardar estado original para rollback
    const originalCompanies = [...this.companies$.value];
    const originalCompany = originalCompanies.find(c => c.idCompany === id);

    if (!originalCompany) {
      return throwError(() => ({ success: false, error: 'Compañía no encontrada' }));
    }

    // Crear compañía actualizada para mostrar optimistamente
    const updatedCompany: Company = {
      ...originalCompany,
      codeCompany: companyData.codeCompany || originalCompany.codeCompany,
      nameCompany: companyData.nameCompany || originalCompany.nameCompany,
      descriptionCompany: companyData.descriptionCompany || originalCompany.descriptionCompany
    };

    // Actualizar optimistamente
    this.updateCompanyInLocalState(updatedCompany);

    return this.http.put<void>(`${this.API_BASE}/${id}`, companyData)
      .pipe(
        map(() => {
          this.setLoading(false);
          return { success: true, company: updatedCompany };
        }),
        catchError(error => {
          // Rollback en caso de error
          this.companies$.next(originalCompanies);

          const errorMessage = this.extractErrorMessage(error);
          this.setError(errorMessage);
          this.setLoading(false);

          return throwError(() => ({ success: false, error: errorMessage }));
        })
      );
  }

  /**
   * Elimina una compañía con actualización optimista
   * @param id ID de la compañía a eliminar
   * @returns Observable con el resultado y función de rollback
   */
  deleteCompanyOptimistic(id: number): Observable<{ success: boolean; error?: string }> {
    this.setLoading(true);
    this.setError(null);

    // Guardar estado original para rollback
    const originalCompanies = [...this.companies$.value];
    const originalPagination = { ...this.pagination$.value };

    // Eliminar optimistamente
    this.removeCompanyFromLocalState(id);

    return this.http.delete<void>(`${this.API_BASE}/${id}`)
      .pipe(
        map(() => {
          this.setLoading(false);
          return { success: true };
        }),
        catchError(error => {
          // Rollback en caso de error
          this.companies$.next(originalCompanies);
          this.pagination$.next(originalPagination);

          const errorMessage = this.extractErrorMessage(error);
          this.setError(errorMessage);
          this.setLoading(false);

          return throwError(() => ({ success: false, error: errorMessage }));
        })
      );
  }

  /**
   * Extrae un mensaje de error legible del error HTTP
   * @param error Error HTTP
   * @returns Mensaje de error legible
   */
  private extractErrorMessage(error: HttpErrorResponse): string {
    if (error.error instanceof ErrorEvent) {
      return `Error: ${error.error.message}`;
    } else {
      switch (error.status) {
        case 401:
          return 'No tiene autorización para acceder a este recurso';
        case 404:
          return 'Recurso no encontrado';
        case 409:
          return 'El código de la compañía ya existe';
        case 500:
          return 'Error interno del servidor';
        default:
          return `Error ${error.status}: ${error.error?.detail || error.message}`;
      }
    }
  }

  // Métodos privados para gestión de estado
  private updatePaginationState(response: CompanyResponse, params: CompanyParams): void {
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

    console.error('Error en CompanyService:', error);
    this.setError(errorMessage);
    this.setLoading(false);

    return throwError(() => new Error(errorMessage));
  }
}
