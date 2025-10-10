# 📚 Guía Completa de Paginación - Dynamics 365 Web API

## 📋 Resumen Ejecutivo

Dynamics 365 Web API usa **Server-Driven Paging** con `$skiptoken` y `@odata.nextLink`. **NO soporta** el parámetro OData estándar `$skip`.

---

## 🚫 El Problema: $skip No Funciona

### Error Común

```http
GET /api/data/v9.2/accounts?$top=25&$skip=25
Response: 400 Bad Request
Message: "Skip Clause is not supported in CRM"
```

### Documentación Oficial

Según [Microsoft Learn](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query-data-web-api):

> **"The Dataverse Web API doesn't support the following OData query options: $skip, $search, $format"**

⚠️ No podemos usar paginación offset-based tradicional (`$skip` + `$top`).

---

## ✅ La Solución: Server-Driven Paging

### Flujo Completo

#### 1️⃣ Primera Petición

```http
GET /api/data/v9.2/accounts?$select=name,accountid&$orderby=accountid
Prefer: odata.maxpagesize=25
```

O con query parameter:

```http
GET /api/data/v9.2/accounts?$select=name,accountid&$orderby=accountid&$top=25
```

#### 2️⃣ Respuesta con nextLink

```json
{
  "@odata.context": "[Organization URI]/api/data/v9.2/$metadata#accounts(name,accountid)",
  "@odata.count": 5000,
  "value": [
    {
      "accountid": "00000000-0000-0000-0000-000000000001",
      "name": "Contoso"
    },
    // ... 24 registros más
  ],
  "@odata.nextLink": "[Organization URI]/api/data/v9.2/accounts?$select=name,accountid&$orderby=accountid&$skiptoken=%3Ccookie%20pagenumber=%222%22%20pagingcookie=%22...%22%20/%3E"
}
```

#### 3️⃣ Siguientes Peticiones

**Usa el `@odata.nextLink` completo tal como viene:**

```http
GET [Organization URI]/api/data/v9.2/accounts?$select=name,accountid&$orderby=accountid&$skiptoken=%3Ccookie...
```

El servidor automáticamente incluye el `$skiptoken` correcto en el `nextLink`.

---

## ⚠️ Reglas Críticas

### 🚨 DO's and DON'Ts

#### ✅ DO (Hacer)

1. **Usar el nextLink completo** tal como viene en la respuesta
2. **Mantener el mismo `maxpagesize`** en todas las peticiones
3. **Incluir ordenamiento determinístico** (preferiblemente por primary key)
4. **Cachear los resultados** o el nextLink para navegación
5. **Continuar hasta que `@odata.nextLink` sea null**

#### ❌ DON'T (No Hacer)

1. ❌ **NO modificar** el nextLink
2. ❌ **NO agregar query params** adicionales al nextLink
3. ❌ **NO decodificar/recodificar** el `$skiptoken`
4. ❌ **NO combinar** `$top` con `Prefer: odata.maxpagesize` (se ignora `$top`)
5. ❌ **NO intentar calcular skip** manualmente

### 📝 Ejemplo de Qué NO Hacer

```typescript
// ❌ INCORRECTO: Modificar el nextLink
const modifiedLink = nextLink + '&$select=additionalfield';

// ❌ INCORRECTO: Extraer y modificar skiptoken
const token = extractToken(nextLink);
const newLink = `/accounts?$skiptoken=${token}&$filter=...`;

// ❌ INCORRECTO: Calcular offset
const offset = pageNumber * pageSize;
const url = `/accounts?$skip=${offset}&$top=${pageSize}`;
```

---

## 🎯 Ordenamiento Determinístico

### Por Qué Es Crítico

Sin ordenamiento determinístico:
- ❌ Los mismos registros aparecen en múltiples páginas
- ❌ Algunos registros se omiten completamente
- ❌ El orden cambia entre peticiones

### ✅ Buenos Ordenamientos

```typescript
// ✅ MEJOR: Primary Key (más eficiente en D365)
$orderby=accountid

// ✅ BUENO: Combinar con timestamp
$orderby=createdon desc,accountid

// ✅ BUENO: Campos con alta unicidad
$orderby=accountnumber,accountid

// ✅ BUENO: Múltiples campos para unicidad
$orderby=name,emailaddress1,accountid
```

### ❌ Malos Ordenamientos

```typescript
// ❌ MALO: Campo no único
$orderby=name
// Problema: Muchas cuentas con mismo nombre → orden no determinístico

// ❌ MALO: Status/State
$orderby=statecode
// Problema: Solo 2-3 valores posibles

// ❌ MALO: Campos calculados
$orderby=revenue
// Problema: No optimizado, puede duplicar registros

// ❌ MALO: Sin ordenamiento
// Problema: Puede retornar orden aleatorio entre páginas
```

### 💡 Recomendación de Microsoft

> "When possible, queries should order on the **primary key** for the table because Dataverse is optimized for ordering on the primary key by default."

---

## 🔧 Implementación: De Actual a Correcta

### ❌ Implementación Actual (Temporal)

#### Frontend: `accounts.page.ts`

```typescript
async loadAccounts() {
  const largePageSize = this.pageSize * 4; // 100 items
  const params: GetAccountsParams = {
    top: largePageSize,
    skip: 0,  // Siempre 0 para evitar error 400
    // ...
  };
  // ...
}

async onLoadMore(event: any) {
  // Infinite scroll deshabilitado
  event.target.complete();
}
```

**Limitaciones:**
- ⚠️ Solo accede a primeros 100 de 5000+ registros
- ⚠️ Infinite scroll no funciona
- ⚠️ No es escalable

---

### ✅ Implementación Correcta

#### 1️⃣ Backend: Nuevo método en `crm_service.py`

```python
async def get_accounts_by_nextlink(self, next_link: str) -> dict:
    """
    Obtener siguiente página usando nextLink completo de Dynamics 365
    
    Args:
        next_link: URL completa del @odata.nextLink retornado por D365
                  Ejemplo: "/api/data/v9.2/accounts?$select=...&$skiptoken=..."
        
    Returns:
        dict con accounts, count y next_link para siguiente página
    """
    # El nextLink viene como path relativo con query params
    # Ejemplo: "/api/data/v9.2/accounts?$select=accountid,name&$skiptoken=%3Ccookie..."
    
    # No agregar parámetros adicionales, usar URL tal como viene
    response = await self.http_request.get(
        endpoint=next_link,
        params={}  # NO agregar parámetros
    )
    
    accounts = response.get("value", [])
    
    return {
        "accounts": accounts,
        "count": response.get("@odata.count", len(accounts)),
        "next_link": response.get("@odata.nextLink")
    }
```

#### 2️⃣ Backend: Nuevo endpoint en `accounts.py`

```python
@router.get("/by-nextlink", response_model=AccountsListResponse)
async def get_accounts_by_nextlink(
    next_link: str,
    crm_service: CrmService = Depends(get_crm_service)
):
    """
    Obtener siguiente página de accounts usando nextLink de Dynamics 365
    
    Args:
        next_link: URL completa del @odata.nextLink
        
    Returns:
        Lista de accounts con información de paginación
    """
    result = await crm_service.get_accounts_by_nextlink(next_link)
    
    return AccountsListResponse(
        accounts=[AccountResponse(**account) for account in result["accounts"]],
        count=result["count"],
        next_link=result.get("next_link")
    )
```

#### 3️⃣ Frontend: Nuevo método en `crm.service.ts`

```typescript
/**
 * Obtener siguiente página de accounts usando nextLink
 * @param nextLink URL completa del @odata.nextLink retornado por backend
 * @returns Observable con lista de accounts y next_link
 */
getAccountsByNextLink(nextLink: string): Observable<AccountsListResponse> {
  // nextLink viene del backend como string completo
  // Ejemplo: "/api/data/v9.2/accounts?$select=...&$skiptoken=..."
  
  // URL encode para enviarlo como query parameter
  const encodedNextLink = encodeURIComponent(nextLink);
  
  return this.http.get<AccountsListResponse>(
    `${this.baseUrl}/crm/accounts/by-nextlink?next_link=${encodedNextLink}`
  );
}
```

#### 4️⃣ Frontend: Actualizar `accounts.page.ts`

```typescript
export class AccountsPage implements OnInit, OnDestroy {
  accounts: Account[] = [];
  nextLink: string | undefined;
  hasNextPage = true;
  isLoading = false;
  isLoadingMore = false;
  
  private pageSize = 25;
  
  async ngOnInit() {
    await this.loadAccounts();
  }
  
  /**
   * Cargar primera página de accounts
   */
  async loadAccounts() {
    this.isLoading = true;
    
    const params: GetAccountsParams = {
      top: this.pageSize,
      orderby: 'accountid',  // ✅ Ordenamiento determinístico por primary key
      select: 'accountid,name,emailaddress1,telephone1,websiteurl,createdon',
      count: 'true'
    };
    
    this.crmService.getAccounts(params)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          console.log('✅ Primera página cargada:', {
            itemsReceived: response.accounts.length,
            totalCount: response.count,
            hasNextLink: !!response.next_link
          });
          
          this.accounts = response.accounts;
          this.nextLink = response.next_link;
          this.hasNextPage = !!this.nextLink;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('❌ Error loading accounts:', error);
          this.presentToast('Error al cargar cuentas', 'danger');
          this.isLoading = false;
        }
      });
  }
  
  /**
   * Cargar más accounts cuando se hace scroll (infinite scroll)
   */
  async onLoadMore(event: any) {
    // Validar que se puede cargar más
    if (!this.hasNextPage || this.isLoadingMore || !this.nextLink) {
      console.log('⚠️ No se puede cargar más:', {
        hasNextPage: this.hasNextPage,
        isLoadingMore: this.isLoadingMore,
        hasNextLink: !!this.nextLink
      });
      event.target.complete();
      return;
    }
    
    console.log('🔄 Cargando más accounts...', {
      currentCount: this.accounts.length,
      nextLink: this.nextLink.substring(0, 100) + '...'
    });
    
    this.isLoadingMore = true;
    
    this.crmService.getAccountsByNextLink(this.nextLink)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          console.log('✅ Más accounts cargados:', {
            newItems: response.accounts.length,
            totalItems: this.accounts.length + response.accounts.length,
            hasMorePages: !!response.next_link
          });
          
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
          this.presentToast('Error al cargar más cuentas', 'danger');
          this.isLoadingMore = false;
          event.target.complete();
        }
      });
  }
  
  /**
   * Refrescar lista (pull to refresh)
   */
  async doRefresh(event: any) {
    console.log('🔄 Refrescando lista...');
    
    // Reset estado de paginación
    this.nextLink = undefined;
    this.hasNextPage = true;
    this.accounts = [];
    
    // Cargar primera página
    await this.loadAccounts();
    
    event.target.complete();
  }
}
```

---

## 📊 Límites y Consideraciones

### Límites por Defecto de Dynamics 365

| Tipo de Tabla | Límite por Request | Configurable |
|---------------|-------------------|--------------|
| **Standard Tables** | 5,000 registros | ✅ Sí con `$top` o `maxpagesize` |
| **Elastic Tables** | 500 registros | ✅ Sí con `$top` o `maxpagesize` |
| **Recomendado para UX** | 25-100 registros | - |

### ⚡ Optimización de Performance

```typescript
// ✅ CONFIGURACIÓN ÓPTIMA
const params = {
  top: 50,                        // Tamaño razonable (balance UX/performance)
  orderby: 'accountid',           // Primary key (más eficiente)
  select: 'accountid,name,email', // Solo campos necesarios
  count: 'true'                   // Incluir total count
};

// ❌ CONFIGURACIÓN SUBÓPTIMA
const params = {
  top: 5000,                      // Demasiados registros → timeout
  orderby: 'name',                // No único → duplicados
  // Sin select → trae TODOS los campos (lento)
  count: 'false'                  // No sabemos cuántos hay en total
};
```

### 🎯 Estrategias de Optimización

1. **Virtual Scrolling**: Renderizar solo items visibles en DOM
2. **Lazy Loading de Campos**: Cargar detalles solo cuando se abre el item
3. **Debouncing**: Evitar múltiples requests simultáneos
4. **Caching**: Guardar páginas cargadas para navegación rápida
5. **Search First**: Animar a filtrar antes de ver todos los items

---

## 🧪 Testing

### Casos de Prueba

```typescript
describe('Pagination with nextLink', () => {
  it('should load first page with 25 items', async () => {
    const response = await loadAccounts({ top: 25 });
    expect(response.accounts.length).toBe(25);
    expect(response.next_link).toBeDefined();
  });
  
  it('should load second page using nextLink', async () => {
    const page1 = await loadAccounts({ top: 25 });
    const page2 = await loadAccountsByNextLink(page1.next_link);
    
    expect(page2.accounts.length).toBeGreaterThan(0);
    expect(page2.accounts[0].accountid).not.toBe(page1.accounts[0].accountid);
  });
  
  it('should not duplicate items across pages', async () => {
    const page1 = await loadAccounts({ top: 25 });
    const page2 = await loadAccountsByNextLink(page1.next_link);
    
    const allIds = [
      ...page1.accounts.map(a => a.accountid),
      ...page2.accounts.map(a => a.accountid)
    ];
    
    const uniqueIds = new Set(allIds);
    expect(uniqueIds.size).toBe(allIds.length);
  });
  
  it('should reach end of data', async () => {
    let nextLink = undefined;
    let totalItems = 0;
    let iterations = 0;
    const maxIterations = 200; // Prevenir loop infinito
    
    // Primera página
    const firstPage = await loadAccounts({ top: 25 });
    totalItems += firstPage.accounts.length;
    nextLink = firstPage.next_link;
    
    // Cargar todas las páginas
    while (nextLink && iterations < maxIterations) {
      const page = await loadAccountsByNextLink(nextLink);
      totalItems += page.accounts.length;
      nextLink = page.next_link;
      iterations++;
    }
    
    expect(nextLink).toBeUndefined();
    expect(totalItems).toBe(firstPage.count); // Total debe coincidir
  });
});
```

---

## 🔗 Referencias Oficiales

### Documentación de Microsoft

1. **Query Data Web API**  
   https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query-data-web-api
   - OData options soportadas y no soportadas
   - Diferencias con OData estándar

2. **Page Results Using OData**  
   https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query/page-results
   - Server-driven paging
   - Ordenamiento determinístico
   - Mejores prácticas

3. **OData V4.0 Protocol**  
   https://www.odata.org/documentation/odata-version-4-0-part-1-protocol/#ServerDrivenPaging
   - Especificación OData de server-driven paging
   - Formato de nextLink

### Artículos Relacionados

- [Elastic Tables](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-elastic-tables)
- [Query Options](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query/overview)

---

## ✅ Checklist de Implementación

### Backend

- [ ] ✅ Crear método `get_accounts_by_nextlink()` en `crm_service.py`
- [ ] ✅ Crear endpoint `/by-nextlink` en `accounts.py`
- [ ] ⬜ Testing: Validar que nextLink se usa correctamente
- [ ] ⬜ Testing: Validar que no se modifican parámetros del nextLink

### Frontend Service

- [ ] ✅ Crear método `getAccountsByNextLink()` en `crm.service.ts`
- [ ] ⬜ Testing: Validar URL encoding del nextLink

### Frontend Component

- [ ] ✅ Actualizar `loadAccounts()` para incluir `orderby=accountid`
- [ ] ✅ Actualizar `onLoadMore()` para usar nextLink
- [ ] ✅ Agregar logging para debugging
- [ ] ⬜ Testing: Validar que no hay duplicados
- [ ] ⬜ Testing: Validar que refresh resetea paginación
- [ ] ⬜ Testing: Validar con dataset de 5000+ registros

### Aplicar a Otras Entidades

- [ ] ⬜ Aplicar solución a Cases
- [ ] ⬜ Aplicar solución a Contacts
- [ ] ⬜ Crear tests para todas las entidades

### Optimizaciones Futuras

- [ ] ⬜ Implementar virtual scrolling
- [ ] ⬜ Implementar caching de páginas
- [ ] ⬜ Implementar debouncing en scroll
- [ ] ⬜ Analizar performance con datasets grandes

---

## 📝 Notas Adicionales

### Comportamiento del Paging Cookie

El `$skiptoken` en realidad es un **paging cookie** que contiene:
- Número de página
- ID del primer registro de la página anterior
- ID del último registro de la página anterior
- Metadata de tracking

**No intentes decodificarlo o manipularlo** - es interno de Dynamics 365.

### Navegación Hacia Atrás

El server-driven paging está **optimizado para navegación forward** (hacia adelante). Si necesitas navegación backward:

1. **Cachear páginas previas** en memoria/localStorage
2. **Usar query parameters** diferentes para filtrar (`$filter`)
3. **Implementar bookmark system** con IDs específicos

### Compatibilidad con Búsqueda/Filtrado

Si agregas `$filter` a la petición inicial, el `nextLink` **incluirá automáticamente** ese filtro en todas las páginas siguientes.

```typescript
// ✅ CORRECTO: Filtro se mantiene en todas las páginas
const params = {
  top: 25,
  filter: "contains(name, 'Contoso')",
  orderby: 'accountid'
};

// nextLink será: /accounts?$filter=contains(name,'Contoso')&$skiptoken=...
```

---

**Fecha de Creación**: 10 de octubre de 2025  
**Estado**: Guía completa para implementación  
**Prioridad**: Alta - Requerido para escalar a 5000+ registros
