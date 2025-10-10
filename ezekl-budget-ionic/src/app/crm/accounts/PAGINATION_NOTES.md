# Notas sobre Paginación en Dynamics 365

## 🚨 Limitación Importante

**Dynamics 365 Web API NO soporta el parámetro `$skip` de OData** para paginación tradicional.

### Problema Encontrado

Cuando intentamos usar paginación estándar con `$skip`:

```typescript
GET /api/crm/accounts?$top=25&$skip=25  // ❌ Error 400
```

**Error retornado:**
```
400 Bad Request: Skip Clause is not supported in CRM
```

### Cómo Funciona D365

Dynamics 365 usa **paginación basada en cookies (stateful pagination)** en lugar de offset:

1. **Primera Request**: `GET /accounts?$top=25`
2. **Response incluye** `@odata.nextLink` con un token de paginación:
   ```json
   {
     "@odata.count": 5000,
     "@odata.nextLink": "/accounts?$top=25&$skiptoken=<cookie_token>",
     "value": [...]
   }
   ```
3. **Siguientes Requests**: Usar el `@odata.nextLink` completo

### Estado Actual

Por ahora, el **infinite scroll está deshabilitado** y solo cargamos la primera página de 25 cuentas.

### Implementación Futura

Para habilitar infinite scroll correctamente, necesitamos:

1. **Modificar el backend** para exponer el `next_link` completamente
2. **Modificar el servicio CRM** para aceptar URL completa de next_link
3. **Actualizar el componente** para usar next_link en lugar de calcular skip

#### Backend Changes Needed

```python
# app/api/crm/accounts.py
@router.get("", response_model=AccountsListResponse)
async def get_accounts(
    next_link: Optional[str] = None,  # Nueva opción
    top: Optional[int] = 25,
    # ...
):
    if next_link:
        # Usar next_link directamente
        result = await crm_service.get_accounts_from_url(next_link)
    else:
        # Primera carga
        result = await crm_service.get_accounts(top=top, ...)
```

#### Service Changes Needed

```typescript
// crm.service.ts
getAccountsFromNextLink(nextLink: string): Observable<AccountsListResponse> {
  // Parsear el next_link y hacer request
  return this.http.get<AccountsListResponse>(nextLink);
}
```

#### Component Changes Needed

```typescript
// accounts.page.ts
async onLoadMore(event: any) {
  if (this.hasNextPage && !this.isLoadingMore && this.nextLink) {
    this.isLoadingMore = true;
    
    // Usar next_link en lugar de calcular skip
    await this.loadAccountsFromNextLink(this.nextLink);
    
    event.target.complete();
  }
}
```

### Alternativas

1. **Aumentar $top** - Cargar más registros en la primera página (ej: 100 en lugar de 25)
2. **Virtual Scroll** - Mostrar solo los visibles y no cargar más
3. **Cursor-based Pagination** - Implementar paginación con next_link

### Referencias

- [OData V4: Server-Driven Paging](https://www.odata.org/documentation/odata-version-4-0-part-1-protocol/#ServerDrivenPaging)
- [Dynamics 365 Web API: Query Data](https://docs.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query-data-web-api)
- [Dynamics 365: Paging Results](https://docs.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query-data-web-api#page-results)

---

**Fecha**: 10 de octubre de 2025  
**Estado**: Infinite scroll deshabilitado temporalmente  
**Prioridad**: Media - Funcionalidad nice-to-have
