/**
 * Modelos TypeScript para la integración con Dynamics 365 CRM
 * Estos interfaces coinciden con los modelos Pydantic del backend FastAPI
 */

// ===============================================
// MODELOS BASE Y RESPUESTAS COMUNES
// ===============================================

export interface CRMOperationResponse {
  status: string;
  entity_url?: string;
  entity_id?: string;
  message?: string;
}

// ===============================================
// MODELOS DE CASOS (INCIDENTS)
// ===============================================

export interface CaseResponse {
  incidentid: string;
  title: string;
  description?: string;
  statuscode?: number;
  statecode?: number;
  casetypecode?: number;
  createdon?: string;
  modifiedon?: string;
  customerid?: string;
  customer_name?: string;
  prioritycode?: number;
  caseorigincode?: number;
  escalated?: boolean;
}

export interface CaseCreateRequest {
  title: string;
  description?: string;
  casetypecode?: number;
  customer_account_id?: string;
  customer_contact_id?: string;
  prioritycode?: number;
  caseorigincode?: number;
}

export interface CaseUpdateRequest {
  title?: string;
  description?: string;
  casetypecode?: number;
  statuscode?: number;
  prioritycode?: number;
}

export interface CasesListResponse {
  count: number;
  cases: CaseResponse[];
  next_link?: string;
}

// ===============================================
// MODELOS DE CUENTAS (ACCOUNTS)
// ===============================================

export interface AccountResponse {
  accountid: string;
  name: string;
  accountnumber?: string;
  telephone1?: string;
  emailaddress1?: string;
  websiteurl?: string;
  address1_line1?: string;
  address1_city?: string;
  address1_stateorprovince?: string;
  address1_postalcode?: string;
  address1_country?: string;
  industrycode?: number;
  revenue?: number;
  numberofemployees?: number;
  createdon?: string;
  modifiedon?: string;
  statuscode?: number;
}

export interface AccountCreateRequest {
  name: string;
  accountnumber?: string;
  telephone1?: string;
  emailaddress1?: string;
  websiteurl?: string;
  address1_line1?: string;
  address1_city?: string;
  address1_stateorprovince?: string;
  address1_postalcode?: string;
  address1_country?: string;
  industrycode?: number;
  revenue?: number;
  numberofemployees?: number;
}

export interface AccountUpdateRequest {
  name?: string;
  telephone1?: string;
  emailaddress1?: string;
  websiteurl?: string;
  address1_line1?: string;
  address1_city?: string;
  address1_stateorprovince?: string;
  address1_postalcode?: string;
  address1_country?: string;
  industrycode?: number;
  revenue?: number;
  numberofemployees?: number;
}

export interface AccountsListResponse {
  count: number;
  accounts: AccountResponse[];
  next_link?: string;
}

// ===============================================
// MODELOS DE CONTACTOS (CONTACTS)
// ===============================================

export interface ContactResponse {
  contactid: string;
  firstname: string;
  lastname: string;
  fullname?: string;
  emailaddress1?: string;
  telephone1?: string;
  mobilephone?: string;
  jobtitle?: string;
  birthdate?: string;
  gendercode?: number;
  address1_line1?: string;
  address1_city?: string;
  address1_stateorprovince?: string;
  address1_postalcode?: string;
  address1_country?: string;
  parentcustomerid?: string;
  createdon?: string;
  modifiedon?: string;
  statuscode?: number;
}

export interface ContactCreateRequest {
  firstname: string;
  lastname: string;
  emailaddress1?: string;
  telephone1?: string;
  mobilephone?: string;
  jobtitle?: string;
  birthdate?: string;
  gendercode?: number;
  address1_line1?: string;
  address1_city?: string;
  address1_stateorprovince?: string;
  address1_postalcode?: string;
  address1_country?: string;
  parentcustomerid?: string;
}

export interface ContactUpdateRequest {
  firstname?: string;
  lastname?: string;
  emailaddress1?: string;
  telephone1?: string;
  mobilephone?: string;
  jobtitle?: string;
  birthdate?: string;
  gendercode?: number;
  address1_line1?: string;
  address1_city?: string;
  address1_stateorprovince?: string;
  address1_postalcode?: string;
  address1_country?: string;
}

export interface ContactsListResponse {
  count: number;
  contacts: ContactResponse[];
  next_link?: string;
}

// ===============================================
// MODELOS DE SISTEMA Y DIAGNÓSTICOS
// ===============================================

export interface CRMHealthResponse {
  status: 'ok' | 'error';
  d365: string;
  api_version: string;
  message?: string;
}

export interface CRMTokenResponse {
  token_preview: string;
  expires_at: number;
  is_valid: boolean;
  expires_in_seconds: number;
}

export interface CRMDiagnosticCheck {
  name: string;
  status: 'success' | 'warning' | 'error';
  message: string;
  details?: any;
}

export interface CRMDiagnoseResponse {
  overall_status: 'healthy' | 'warnings' | 'errors';
  checks: CRMDiagnosticCheck[];
  recommendations?: string[];
  user_info?: {
    user_id: string;
    business_unit_name: string;
    organization_name: string;
  };
}

// ===============================================
// PARÁMETROS DE CONSULTA Y FILTROS
// ===============================================

export interface CRMListParams {
  top?: number;                    // Número de resultados (paginación)
  skip?: number;                   // Offset para paginación
  filter_query?: string;          // Filtro OData
  select_fields?: string;         // Campos específicos a retornar
  order_by?: string;              // Ordenamiento
}

// ===============================================
// ENUMS Y CONSTANTES
// ===============================================

export enum CaseStatus {
  Active = 1,
  Resolved = 5,
  Canceled = 6,
  Merged = 2000
}

export enum CaseOrigin {
  Phone = 1,
  Email = 2,
  Web = 3,
  Facebook = 2483,
  Twitter = 3986
}

export enum CasePriority {
  High = 1,
  Normal = 2,
  Low = 3
}

export enum AccountIndustry {
  Accounting = 1,
  Agriculture = 2,
  Automotive = 3,
  Banking = 4,
  Biotechnology = 5,
  Consulting = 6,
  Education = 7,
  Financial = 8,
  Government = 9,
  Healthcare = 10,
  Technology = 11
}

export enum ContactGender {
  Male = 1,
  Female = 2
}

// ===============================================
// FILTROS PREDEFINIDOS PARA ODATA
// ===============================================

export class CRMFilters {
  // Filtros para casos
  static activeCases(): string {
    return 'statuscode eq 1';
  }

  static casesByTitle(searchText: string): string {
    return `contains(title,'${searchText}')`;
  }

  static casesCreatedAfter(date: string): string {
    return `createdon gt ${date}`;
  }

  // Filtros para cuentas
  static accountsByName(searchText: string): string {
    return `contains(name,'${searchText}')`;
  }

  static accountsByCity(city: string): string {
    return `contains(address1_city,'${city}')`;
  }

  static accountsWithRevenue(minRevenue: number): string {
    return `revenue gt ${minRevenue}`;
  }

  // Filtros para contactos
  static contactsByName(searchText: string): string {
    return `contains(fullname,'${searchText}')`;
  }

  static contactsByJobTitle(title: string): string {
    return `contains(jobtitle,'${title}')`;
  }

  static contactsByEmail(emailDomain: string): string {
    return `contains(emailaddress1,'${emailDomain}')`;
  }

  // Combinadores
  static combineFilters(filters: string[], operator: 'and' | 'or' = 'and'): string {
    return filters.join(` ${operator} `);
  }
}
