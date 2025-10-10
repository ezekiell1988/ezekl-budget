import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

import {
  // Modelos de casos
  CaseResponse,
  CaseCreateRequest,
  CaseUpdateRequest,
  CasesListResponse,

  // Modelos de cuentas
  AccountResponse,
  AccountCreateRequest,
  AccountUpdateRequest,
  AccountsListResponse,

  // Modelos de contactos
  ContactResponse,
  ContactCreateRequest,
  ContactUpdateRequest,
  ContactsListResponse,

  // Modelos de sistema
  CRMHealthResponse,
  CRMTokenResponse,
  CRMDiagnoseResponse,

  // Tipos comunes
  CRMOperationResponse,
  CRMListParams
} from '../models/crm.models';

@Injectable({
  providedIn: 'root'
})
export class CrmService {
  private http = inject(HttpClient);
  private readonly baseUrl = '/api/crm';

  constructor() {}

  // ===============================================
  // MÉTODOS AUXILIARES Y CONFIGURACIÓN
  // ===============================================

  /**
   * Obtiene headers HTTP con autorización
   */
  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  /**
   * Construye parámetros HTTP desde CRMListParams
   */
  private buildHttpParams(params?: CRMListParams): HttpParams {
    let httpParams = new HttpParams();

    if (params) {
      if (params.top !== undefined) {
        httpParams = httpParams.set('top', params.top.toString());
      }
      if (params.skip !== undefined) {
        httpParams = httpParams.set('skip', params.skip.toString());
      }
      if (params.filter_query) {
        httpParams = httpParams.set('filter_query', params.filter_query);
      }
      if (params.select_fields) {
        httpParams = httpParams.set('select_fields', params.select_fields);
      }
      if (params.order_by) {
        httpParams = httpParams.set('order_by', params.order_by);
      }
    }

    return httpParams;
  }

  /**
   * Manejo centralizado de errores HTTP
   */
  private handleError(error: any): Observable<never> {
    console.error('❌ Error en servicio CRM:', error);

    let errorMessage = 'Error desconocido en el servicio CRM';

    if (error.error?.detail) {
      errorMessage = error.error.detail;
    } else if (error.error?.message) {
      errorMessage = error.error.message;
    } else if (error.message) {
      errorMessage = error.message;
    }

    return throwError(() => new Error(errorMessage));
  }

  // ===============================================
  // ENDPOINTS DE CASOS (INCIDENTS)
  // ===============================================

  /**
   * Obtiene lista paginada de casos con filtros opcionales
   */
  getCases(params?: CRMListParams): Observable<CasesListResponse> {
    const httpParams = this.buildHttpParams(params);

    return this.http.get<CasesListResponse>(`${this.baseUrl}/cases`, {
      headers: this.getHeaders(),
      params: httpParams
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene un caso específico por ID
   */
  getCase(caseId: string): Observable<CaseResponse> {
    return this.http.get<CaseResponse>(`${this.baseUrl}/cases/${caseId}`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Crea un nuevo caso
   */
  createCase(caseData: CaseCreateRequest): Observable<CRMOperationResponse> {
    return this.http.post<CRMOperationResponse>(`${this.baseUrl}/cases`, caseData, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Actualiza un caso existente
   */
  updateCase(caseId: string, caseData: CaseUpdateRequest): Observable<CRMOperationResponse> {
    return this.http.patch<CRMOperationResponse>(`${this.baseUrl}/cases/${caseId}`, caseData, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Elimina un caso
   */
  deleteCase(caseId: string): Observable<CRMOperationResponse> {
    return this.http.delete<CRMOperationResponse>(`${this.baseUrl}/cases/${caseId}`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene la siguiente página de casos usando @odata.nextLink de Dynamics 365.
   *
   * **⚠️ Server-Driven Paging:**
   * Dynamics 365 usa paginación basada en cookies ($skiptoken), no offset ($skip).
   * El nextLink incluye automáticamente el $skiptoken correcto para la siguiente página.
   *
   * @param nextLink URL completa del @odata.nextLink retornado por el backend
   *                 Ejemplo: "/api/data/v9.2/incidents?$select=...&$skiptoken=..."
   * @returns Observable con la siguiente página de casos y el nextLink para más páginas
   *
   * **⚠️ Importante:**
   * - Dynamics 365 NO soporta $skip, usa $skiptoken
   * - NO modificar el nextLink
   * - Usar exactamente como viene en la respuesta
   *
   * @see D365_PAGINATION_GUIDE.md para más detalles
   */
  getCasesByNextLink(nextLink: string): Observable<CasesListResponse> {
    // URL encode del nextLink para enviarlo como query parameter
    const encodedNextLink = encodeURIComponent(nextLink);

    return this.http.get<CasesListResponse>(
      `${this.baseUrl}/cases/by-nextlink?next_link=${encodedNextLink}`,
      {
        headers: this.getHeaders()
      }
    ).pipe(
      catchError(this.handleError)
    );
  }

  // ===============================================
  // ENDPOINTS DE CUENTAS (ACCOUNTS)
  // ===============================================

  /**
   * Obtiene lista paginada de cuentas con filtros opcionales
   */
  getAccounts(params?: CRMListParams): Observable<AccountsListResponse> {
    const httpParams = this.buildHttpParams(params);

    return this.http.get<AccountsListResponse>(`${this.baseUrl}/accounts`, {
      headers: this.getHeaders(),
      params: httpParams
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene la siguiente página de cuentas usando nextLink de Dynamics 365
   *
   * Este método implementa server-driven paging correctamente según la
   * especificación OData v4.0 y las limitaciones de Dynamics 365 Web API.
   *
   * @param nextLink URL completa del @odata.nextLink retornado por el backend
   *                 Ejemplo: "/api/data/v9.2/accounts?$select=...&$skiptoken=..."
   * @returns Observable con la siguiente página de cuentas y el nextLink para más páginas
   *
   * **⚠️ Importante:**
   * - Dynamics 365 NO soporta $skip, usa $skiptoken
   * - NO modificar el nextLink
   * - Usar exactamente como viene en la respuesta
   *
   * @see D365_PAGINATION_GUIDE.md para más detalles
   */
  getAccountsByNextLink(nextLink: string): Observable<AccountsListResponse> {
    // URL encode del nextLink para enviarlo como query parameter
    const encodedNextLink = encodeURIComponent(nextLink);

    return this.http.get<AccountsListResponse>(
      `${this.baseUrl}/accounts/by-nextlink?next_link=${encodedNextLink}`,
      {
        headers: this.getHeaders()
      }
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene una cuenta específica por ID
   */
  getAccount(accountId: string): Observable<AccountResponse> {
    return this.http.get<AccountResponse>(`${this.baseUrl}/accounts/${accountId}`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Crea una nueva cuenta
   */
  createAccount(accountData: AccountCreateRequest): Observable<CRMOperationResponse> {
    return this.http.post<CRMOperationResponse>(`${this.baseUrl}/accounts`, accountData, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Actualiza una cuenta existente
   */
  updateAccount(accountId: string, accountData: AccountUpdateRequest): Observable<CRMOperationResponse> {
    return this.http.patch<CRMOperationResponse>(`${this.baseUrl}/accounts/${accountId}`, accountData, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Elimina una cuenta
   */
  deleteAccount(accountId: string): Observable<CRMOperationResponse> {
    return this.http.delete<CRMOperationResponse>(`${this.baseUrl}/accounts/${accountId}`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  // ===============================================
  // ENDPOINTS DE CONTACTOS (CONTACTS)
  // ===============================================

  /**
   * Obtiene lista paginada de contactos con filtros opcionales
   */
  getContacts(params?: CRMListParams): Observable<ContactsListResponse> {
    const httpParams = this.buildHttpParams(params);

    return this.http.get<ContactsListResponse>(`${this.baseUrl}/contacts`, {
      headers: this.getHeaders(),
      params: httpParams
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene un contacto específico por ID
   */
  getContact(contactId: string): Observable<ContactResponse> {
    return this.http.get<ContactResponse>(`${this.baseUrl}/contacts/${contactId}`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Crea un nuevo contacto
   */
  createContact(contactData: ContactCreateRequest): Observable<CRMOperationResponse> {
    return this.http.post<CRMOperationResponse>(`${this.baseUrl}/contacts`, contactData, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Actualiza un contacto existente
   */
  updateContact(contactId: string, contactData: ContactUpdateRequest): Observable<CRMOperationResponse> {
    return this.http.patch<CRMOperationResponse>(`${this.baseUrl}/contacts/${contactId}`, contactData, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Elimina un contacto
   */
  deleteContact(contactId: string): Observable<CRMOperationResponse> {
    return this.http.delete<CRMOperationResponse>(`${this.baseUrl}/contacts/${contactId}`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene la siguiente página de contactos usando @odata.nextLink de Dynamics 365.
   *
   * **⚠️ Server-Driven Paging:**
   * Dynamics 365 usa paginación basada en cookies ($skiptoken), no offset ($skip).
   * El nextLink incluye automáticamente el $skiptoken correcto para la siguiente página.
   *
   * @param nextLink URL completa del @odata.nextLink retornado por el backend
   *                 Ejemplo: "/api/data/v9.2/contacts?$select=...&$skiptoken=..."
   * @returns Observable con la siguiente página de contactos y el nextLink para más páginas
   *
   * **⚠️ Importante:**
   * - Dynamics 365 NO soporta $skip, usa $skiptoken
   * - NO modificar el nextLink
   * - Usar exactamente como viene en la respuesta
   *
   * @see D365_PAGINATION_GUIDE.md para más detalles
   */
  getContactsByNextLink(nextLink: string): Observable<ContactsListResponse> {
    // URL encode del nextLink para enviarlo como query parameter
    const encodedNextLink = encodeURIComponent(nextLink);

    return this.http.get<ContactsListResponse>(
      `${this.baseUrl}/contacts/by-nextlink?next_link=${encodedNextLink}`,
      {
        headers: this.getHeaders()
      }
    ).pipe(
      catchError(this.handleError)
    );
  }

  // ===============================================
  // ENDPOINTS DE SISTEMA Y DIAGNÓSTICOS
  // ===============================================

  /**
   * Health check básico del CRM
   */
  getHealthCheck(): Observable<CRMHealthResponse> {
    return this.http.get<CRMHealthResponse>(`${this.baseUrl}/system/health`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Diagnóstico completo del CRM
   */
  getDiagnosis(): Observable<CRMDiagnoseResponse> {
    return this.http.get<CRMDiagnoseResponse>(`${this.baseUrl}/system/diagnose`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Información del token actual
   */
  getTokenInfo(): Observable<CRMTokenResponse> {
    return this.http.get<CRMTokenResponse>(`${this.baseUrl}/system/token`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Limpiar caché de token
   */
  clearTokenCache(): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.baseUrl}/system/clear-cache`, {}, {
      headers: this.getHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  // ===============================================
  // MÉTODOS DE CONVENIENCIA Y UTILIDADES
  // ===============================================

  /**
   * Busca casos por título
   */
  searchCasesByTitle(searchText: string, limit: number = 25): Observable<CasesListResponse> {
    const params: CRMListParams = {
      filter_query: `contains(title,'${searchText}')`,
      top: limit
    };
    return this.getCases(params);
  }

  /**
   * Obtiene casos activos
   */
  getActiveCases(limit: number = 25): Observable<CasesListResponse> {
    const params: CRMListParams = {
      filter_query: 'statuscode eq 1',
      top: limit,
      order_by: 'createdon desc'
    };
    return this.getCases(params);
  }

  /**
   * Busca cuentas por nombre
   */
  searchAccountsByName(searchText: string, limit: number = 25): Observable<AccountsListResponse> {
    const params: CRMListParams = {
      filter_query: `contains(name,'${searchText}')`,
      top: limit
    };
    return this.getAccounts(params);
  }

  /**
   * Busca contactos por nombre
   */
  searchContactsByName(searchText: string, limit: number = 25): Observable<ContactsListResponse> {
    const params: CRMListParams = {
      filter_query: `contains(fullname,'${searchText}')`,
      top: limit
    };
    return this.getContacts(params);
  }

  /**
   * Obtiene métricas básicas del CRM
   */
  getCRMStats(): Observable<any> {
    // Obtener estadísticas combinando diferentes endpoints
    return this.getHealthCheck().pipe(
      map(health => ({
        health_status: health.status,
        d365_url: health.d365,
        api_version: health.api_version,
        timestamp: new Date().toISOString()
      }))
    );
  }

  /**
   * Valida si el servicio CRM está disponible
   */
  isServiceAvailable(): Observable<boolean> {
    return this.getHealthCheck().pipe(
      map(response => response.status === 'ok'),
      catchError(() => {
        return throwError(() => new Error('Servicio CRM no disponible'));
      })
    );
  }
}
