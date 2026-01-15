# Guía Completa de ngx-datatable

## Tabla de Contenidos
- [Introducción](#introducción)
- [Instalación y Configuración](#instalación-y-configuración)
- [Características Principales](#características-principales)
- [Implementación con API](#implementación-con-api)
- [Paginación del Lado del Servidor](#paginación-del-lado-del-servidor)
- [Filtrado y Búsqueda](#filtrado-y-búsqueda)
- [Ordenamiento](#ordenamiento)
- [Ejemplos Prácticos](#ejemplos-prácticos)
- [Optimización y Mejores Prácticas](#optimización-y-mejores-prácticas)

## Introducción

**ngx-datatable** es un componente Angular altamente flexible y eficiente para presentar grandes conjuntos de datos. Utiliza Virtual DOM para manejar grandes cantidades de información sin afectar el rendimiento.

### ¿Por qué usar ngx-datatable?

- ✅ **Ligero**: Sin dependencias externas
- ✅ **Alto rendimiento**: Maneja miles de filas con Virtual DOM
- ✅ **Flexible**: Permite paginación del lado del cliente o servidor
- ✅ **Personalizable**: Templates para headers, celdas y filas
- ✅ **Responsive**: Se adapta a diferentes tamaños de pantalla
- ✅ **Soporte AOT**: Compilación Ahead-of-Time
- ✅ **Universal**: Compatible con Angular Universal

## Instalación y Configuración

### 1. Instalación

```bash
npm install @swimlane/ngx-datatable --save
```

### 2. Importar el Módulo

```typescript
import { NgxDatatableModule } from '@swimlane/ngx-datatable';

@NgModule({
  imports: [
    NgxDatatableModule
  ]
})
export class AppModule { }
```

### 3. Importar Estilos

En `angular.json`:

```json
"styles": [
  "node_modules/@swimlane/ngx-datatable/index.css",
  "node_modules/@swimlane/ngx-datatable/themes/material.scss",
  "node_modules/@swimlane/ngx-datatable/themes/bootstrap.scss",
  "node_modules/@swimlane/ngx-datatable/assets/icons.css"
]
```

## Características Principales

### Características Destacadas

| Característica | Descripción |
|---------------|-------------|
| **Virtual DOM** | Renderiza solo las filas visibles, ideal para grandes datasets |
| **Paginación** | Cliente o servidor side con componente integrado |
| **Ordenamiento** | Columnas ordenables con soporte servidor/cliente |
| **Filtrado** | Sistema flexible de filtrado personalizable |
| **Selección** | Single, multi, checkbox, con teclado |
| **Scrolling** | Horizontal y vertical con lazy loading |
| **Responsive** | Diseño adaptable automático |
| **Templates** | Personalización completa de headers, celdas y footers |
| **Pinning** | Fijar columnas a izquierda/derecha |
| **Row Details** | Vista expandible de detalles por fila |
| **Reordering** | Reordenar columnas mediante drag & drop |

## Implementación con API

### Estructura Básica del Componente

```typescript
import { Component, OnInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DatatableComponent, ColumnMode } from '@swimlane/ngx-datatable';

@Component({
  selector: 'app-data-table',
  templateUrl: './data-table.component.html'
})
export class DataTableComponent implements OnInit {
  @ViewChild(DatatableComponent) table: DatatableComponent;

  // Configuración
  ColumnMode = ColumnMode;
  rows: any[] = [];
  temp: any[] = [];
  loadingIndicator = true;
  reorderable = true;

  // Definición de columnas
  columns = [
    { prop: 'id', name: 'ID', width: 80 },
    { prop: 'name', name: 'Nombre', flexGrow: 1 },
    { prop: 'email', name: 'Email', flexGrow: 1 },
    { prop: 'company', name: 'Empresa', flexGrow: 1 },
    { prop: 'status', name: 'Estado', width: 100 }
  ];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadData();
  }

  // Cargar datos desde API
  loadData() {
    this.loadingIndicator = true;
    
    this.http.get<any>('https://api.example.com/users').subscribe({
      next: (data) => {
        this.rows = data;
        this.temp = [...data]; // Copia para filtrado
        this.loadingIndicator = false;
      },
      error: (error) => {
        console.error('Error al cargar datos:', error);
        this.loadingIndicator = false;
      }
    });
  }
}
```

### Template HTML Básico

```html
<div class="card">
  <div class="card-header">
    <h3>Lista de Usuarios</h3>
    <div class="search-box">
      <input 
        type="text" 
        class="form-control" 
        placeholder="Buscar..." 
        (keyup)="updateFilter($event)"
      />
    </div>
  </div>

  <div class="card-body">
    <ngx-datatable
      #table
      class="bootstrap"
      [columns]="columns"
      [columnMode]="ColumnMode.force"
      [headerHeight]="50"
      [footerHeight]="50"
      [rowHeight]="'auto'"
      [rows]="rows"
      [loadingIndicator]="loadingIndicator"
      [reorderable]="reorderable"
      [limit]="10">
    </ngx-datatable>
  </div>
</div>
```

## Paginación del Lado del Servidor

### Implementación Completa

#### 1. Interface para Paginación

```typescript
export interface PageInfo {
  offset: number;
  pageSize: number;
  limit: number;
  count: number;
}

export interface ApiResponse {
  data: any[];
  total: number;
  page: number;
  pageSize: number;
}
```

#### 2. Componente con Paginación Server-Side

```typescript
import { Component, OnInit, ViewChild } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { DatatableComponent, ColumnMode } from '@swimlane/ngx-datatable';

@Component({
  selector: 'app-server-pagination',
  templateUrl: './server-pagination.component.html'
})
export class ServerPaginationComponent implements OnInit {
  @ViewChild(DatatableComponent) table: DatatableComponent;

  ColumnMode = ColumnMode;
  rows: any[] = [];
  loadingIndicator = true;
  
  // Configuración de paginación
  page = {
    totalElements: 0,
    pageNumber: 0,
    size: 10
  };

  // Ordenamiento
  sorts = [{ prop: 'id', dir: 'desc' }];

  // Filtros
  filters = {
    search: '',
    status: ''
  };

  columns = [
    { prop: 'id', name: 'ID', width: 80 },
    { prop: 'name', name: 'Nombre', sortable: true },
    { prop: 'email', name: 'Email', sortable: true },
    { prop: 'company', name: 'Empresa', sortable: true },
    { prop: 'status', name: 'Estado', sortable: true }
  ];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.setPage({ offset: 0 });
  }

  /**
   * Cargar página desde el servidor
   */
  setPage(pageInfo: any) {
    this.page.pageNumber = pageInfo.offset;
    this.loadData();
  }

  /**
   * Manejar cambio de ordenamiento
   */
  onSort(event: any) {
    this.sorts = event.sorts;
    this.page.pageNumber = 0; // Resetear a primera página
    this.loadData();
  }

  /**
   * Cargar datos desde API con parámetros
   */
  loadData() {
    this.loadingIndicator = true;

    // Construir parámetros de consulta
    let params = new HttpParams()
      .set('page', String(this.page.pageNumber))
      .set('size', String(this.page.size));

    // Agregar ordenamiento
    if (this.sorts.length > 0) {
      const sort = this.sorts[0];
      params = params.set('sortBy', sort.prop)
                     .set('sortDir', sort.dir);
    }

    // Agregar filtros
    if (this.filters.search) {
      params = params.set('search', this.filters.search);
    }
    if (this.filters.status) {
      params = params.set('status', this.filters.status);
    }

    // Realizar petición HTTP
    this.http.get<ApiResponse>('/api/users', { params }).subscribe({
      next: (response) => {
        this.rows = response.data;
        this.page.totalElements = response.total;
        this.loadingIndicator = false;
      },
      error: (error) => {
        console.error('Error al cargar datos:', error);
        this.loadingIndicator = false;
      }
    });
  }

  /**
   * Actualizar filtro de búsqueda
   */
  updateFilter(event: any) {
    const val = event.target.value.toLowerCase();
    this.filters.search = val;
    this.page.pageNumber = 0; // Resetear a primera página
    this.loadData();
  }

  /**
   * Actualizar filtro de estado
   */
  updateStatusFilter(status: string) {
    this.filters.status = status;
    this.page.pageNumber = 0;
    this.loadData();
  }
}
```

#### 3. Template HTML para Server-Side

```html
<div class="container-fluid">
  <!-- Filtros -->
  <div class="row mb-3">
    <div class="col-md-6">
      <input 
        type="text" 
        class="form-control" 
        placeholder="Buscar por nombre o email..." 
        (keyup)="updateFilter($event)"
      />
    </div>
    <div class="col-md-3">
      <select 
        class="form-control" 
        [(ngModel)]="filters.status" 
        (change)="updateStatusFilter($event.target.value)">
        <option value="">Todos los estados</option>
        <option value="active">Activo</option>
        <option value="inactive">Inactivo</option>
        <option value="pending">Pendiente</option>
      </select>
    </div>
    <div class="col-md-3 text-right">
      <button class="btn btn-primary" (click)="loadData()">
        <i class="fa fa-refresh"></i> Recargar
      </button>
    </div>
  </div>

  <!-- Tabla -->
  <ngx-datatable
    #table
    class="bootstrap"
    [columns]="columns"
    [columnMode]="ColumnMode.force"
    [headerHeight]="50"
    [footerHeight]="50"
    [rowHeight]="'auto'"
    [rows]="rows"
    [loadingIndicator]="loadingIndicator"
    [externalPaging]="true"
    [count]="page.totalElements"
    [offset]="page.pageNumber"
    [limit]="page.size"
    [externalSorting]="true"
    [sorts]="sorts"
    (page)="setPage($event)"
    (sort)="onSort($event)">
  </ngx-datatable>
</div>
```

### Propiedades Clave para Server-Side

| Propiedad | Descripción | Valor |
|-----------|-------------|-------|
| `[externalPaging]` | Habilita paginación externa | `true` |
| `[count]` | Total de registros en el servidor | `page.totalElements` |
| `[offset]` | Página actual (0-based) | `page.pageNumber` |
| `[limit]` | Registros por página | `page.size` |
| `[externalSorting]` | Habilita ordenamiento externo | `true` |
| `[sorts]` | Estado actual del ordenamiento | `sorts` array |
| `(page)` | Evento al cambiar página | `setPage($event)` |
| `(sort)` | Evento al cambiar ordenamiento | `onSort($event)` |

## Filtrado y Búsqueda

### Filtrado del Lado del Cliente

```typescript
/**
 * Filtrar datos localmente
 */
updateFilter(event: any) {
  const val = event.target.value.toLowerCase();

  // Filtrar los datos
  const temp = this.temp.filter((d: any) => {
    // Buscar en múltiples campos
    return (
      d.name.toLowerCase().indexOf(val) !== -1 ||
      d.email.toLowerCase().indexOf(val) !== -1 ||
      d.company.toLowerCase().indexOf(val) !== -1 ||
      !val
    );
  });

  // Actualizar filas
  this.rows = temp;
  
  // Volver a la primera página
  this.table.offset = 0;
}
```

### Filtrado Avanzado con Múltiples Criterios

```typescript
export interface FilterCriteria {
  search?: string;
  status?: string;
  dateFrom?: Date;
  dateTo?: Date;
}

applyFilters(criteria: FilterCriteria) {
  let filtered = [...this.temp];

  // Filtro de texto
  if (criteria.search) {
    const search = criteria.search.toLowerCase();
    filtered = filtered.filter(item =>
      Object.values(item).some(val =>
        String(val).toLowerCase().includes(search)
      )
    );
  }

  // Filtro de estado
  if (criteria.status) {
    filtered = filtered.filter(item => item.status === criteria.status);
  }

  // Filtro de fechas
  if (criteria.dateFrom) {
    filtered = filtered.filter(item =>
      new Date(item.date) >= criteria.dateFrom
    );
  }

  if (criteria.dateTo) {
    filtered = filtered.filter(item =>
      new Date(item.date) <= criteria.dateTo
    );
  }

  this.rows = filtered;
  this.table.offset = 0;
}
```

## Ordenamiento

### Ordenamiento del Lado del Cliente

```typescript
columns = [
  { 
    prop: 'name', 
    name: 'Nombre', 
    sortable: true 
  },
  { 
    prop: 'email', 
    name: 'Email', 
    sortable: true 
  },
  { 
    prop: 'date', 
    name: 'Fecha', 
    sortable: true,
    comparator: this.dateComparator.bind(this)
  }
];

/**
 * Comparador personalizado para fechas
 */
dateComparator(propA: any, propB: any) {
  const dateA = new Date(propA);
  const dateB = new Date(propB);
  return dateA.getTime() - dateB.getTime();
}
```

### Ordenamiento con Estado Inicial

```html
<ngx-datatable
  [rows]="rows"
  [sorts]="[{prop: 'name', dir: 'asc'}]">
</ngx-datatable>
```

## Ejemplos Prácticos

### Ejemplo 1: Tabla con Acciones

```typescript
columns = [
  { prop: 'id', name: 'ID', width: 80 },
  { prop: 'name', name: 'Nombre' },
  { prop: 'email', name: 'Email' },
  { 
    name: 'Acciones', 
    cellTemplate: 'actionsTemplate',
    width: 150,
    sortable: false
  }
];
```

```html
<ngx-datatable
  [rows]="rows"
  [columns]="columns">
  
  <!-- Template para acciones -->
  <ngx-datatable-column name="Acciones" [sortable]="false">
    <ng-template let-row="row" ngx-datatable-cell-template>
      <button 
        class="btn btn-sm btn-primary" 
        (click)="edit(row)">
        <i class="fa fa-edit"></i>
      </button>
      <button 
        class="btn btn-sm btn-danger" 
        (click)="delete(row)">
        <i class="fa fa-trash"></i>
      </button>
    </ng-template>
  </ngx-datatable-column>
</ngx-datatable>
```

### Ejemplo 2: Selección de Filas

```typescript
selected: any[] = [];
SelectionType = SelectionType;

onSelect({ selected }: any) {
  console.log('Seleccionados:', selected);
  this.selected.splice(0, this.selected.length);
  this.selected.push(...selected);
}

onActivate(event: any) {
  console.log('Activar evento:', event);
}
```

```html
<ngx-datatable
  [rows]="rows"
  [selectionType]="SelectionType.checkbox"
  [selected]="selected"
  (select)="onSelect($event)"
  (activate)="onActivate($event)">
</ngx-datatable>
```

### Ejemplo 3: Detalles Expandibles

```typescript
toggleExpandRow(row: any) {
  this.table.rowDetail.toggleExpandRow(row);
}
```

```html
<ngx-datatable
  [rows]="rows">
  
  <!-- Template para detalles -->
  <ngx-datatable-row-detail [rowHeight]="200">
    <ng-template let-row="row" ngx-datatable-row-detail-template>
      <div class="row-detail">
        <h4>Detalles de {{ row.name }}</h4>
        <div>Email: {{ row.email }}</div>
        <div>Teléfono: {{ row.phone }}</div>
        <div>Dirección: {{ row.address }}</div>
      </div>
    </ng-template>
  </ngx-datatable-row-detail>
</ngx-datatable>
```

### Ejemplo 4: Templates Personalizados

```html
<ngx-datatable [rows]="rows">
  
  <!-- Columna con template personalizado -->
  <ngx-datatable-column name="Estado" prop="status">
    <ng-template let-value="value" ngx-datatable-cell-template>
      <span [class]="'badge badge-' + (value === 'active' ? 'success' : 'danger')">
        {{ value | uppercase }}
      </span>
    </ng-template>
  </ngx-datatable-column>

  <!-- Columna con imagen -->
  <ngx-datatable-column name="Avatar" prop="avatar">
    <ng-template let-value="value" ngx-datatable-cell-template>
      <img [src]="value" class="avatar-img" />
    </ng-template>
  </ngx-datatable-column>

  <!-- Columna con formato de moneda -->
  <ngx-datatable-column name="Precio" prop="price">
    <ng-template let-value="value" ngx-datatable-cell-template>
      {{ value | currency:'USD':'symbol':'1.2-2' }}
    </ng-template>
  </ngx-datatable-column>

</ngx-datatable>
```

## Optimización y Mejores Prácticas

### 1. Rendimiento

#### Virtual Scrolling
Para grandes datasets, usa scrolling virtual:

```html
<ngx-datatable
  [rows]="rows"
  [scrollbarV]="true"
  [scrollbarH]="true"
  [virtualization]="true"
  [rowHeight]="50">
</ngx-datatable>
```

#### Lazy Loading
Carga datos bajo demanda:

```typescript
onScroll(offsetY: number) {
  const viewHeight = this.el.nativeElement.getBoundingClientRect().height;
  
  // Si llegamos al final, cargar más
  if (offsetY + viewHeight >= this.rows.length * this.rowHeight) {
    this.loadMoreData();
  }
}

loadMoreData() {
  if (!this.loading && this.hasMore) {
    this.loading = true;
    this.page++;
    
    this.http.get(`/api/data?page=${this.page}`).subscribe(data => {
      this.rows = [...this.rows, ...data];
      this.loading = false;
    });
  }
}
```

### 2. Gestión de Estado

#### Usar RxJS para Datos Reactivos

```typescript
import { BehaviorSubject, Observable, combineLatest } from 'rxjs';
import { debounceTime, distinctUntilChanged, map } from 'rxjs/operators';

export class DataTableComponent implements OnInit {
  private dataSubject$ = new BehaviorSubject<any[]>([]);
  private filterSubject$ = new BehaviorSubject<string>('');
  private sortSubject$ = new BehaviorSubject<any>({});
  
  rows$: Observable<any[]>;

  ngOnInit() {
    // Combinar streams de datos, filtros y ordenamiento
    this.rows$ = combineLatest([
      this.dataSubject$,
      this.filterSubject$.pipe(debounceTime(300), distinctUntilChanged()),
      this.sortSubject$
    ]).pipe(
      map(([data, filter, sort]) => {
        let result = this.filterData(data, filter);
        result = this.sortData(result, sort);
        return result;
      })
    );

    // Suscribirse para actualizar la vista
    this.rows$.subscribe(rows => this.rows = rows);
  }

  updateFilter(value: string) {
    this.filterSubject$.next(value);
  }

  private filterData(data: any[], filter: string): any[] {
    if (!filter) return data;
    return data.filter(item => 
      JSON.stringify(item).toLowerCase().includes(filter.toLowerCase())
    );
  }

  private sortData(data: any[], sort: any): any[] {
    if (!sort.prop) return data;
    return [...data].sort((a, b) => {
      const valueA = a[sort.prop];
      const valueB = b[sort.prop];
      return sort.dir === 'asc' ? 
        (valueA > valueB ? 1 : -1) : 
        (valueA < valueB ? 1 : -1);
    });
  }
}
```

### 3. Manejo de Errores

```typescript
loadData() {
  this.loadingIndicator = true;
  this.errorMessage = null;

  this.http.get('/api/data').pipe(
    retry(3), // Reintentar 3 veces
    catchError(error => {
      this.errorMessage = 'Error al cargar datos. Por favor, intente nuevamente.';
      this.loadingIndicator = false;
      return of([]); // Retornar array vacío
    })
  ).subscribe(data => {
    this.rows = data;
    this.loadingIndicator = false;
  });
}
```

### 4. Caché de Datos

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { tap, shareReplay } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private cache = new Map<string, Observable<any>>();

  constructor(private http: HttpClient) {}

  getData(url: string, params?: any): Observable<any> {
    const key = `${url}_${JSON.stringify(params)}`;
    
    if (!this.cache.has(key)) {
      const request$ = this.http.get(url, { params }).pipe(
        shareReplay(1) // Compartir resultado entre suscriptores
      );
      this.cache.set(key, request$);
    }

    return this.cache.get(key)!;
  }

  clearCache(pattern?: string) {
    if (pattern) {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }
}
```

### 5. Configuración CSS Personalizada

```scss
// Personalizar estilos del datatable
.ngx-datatable {
  &.bootstrap {
    // Header
    .datatable-header {
      background: #f8f9fa;
      border-bottom: 2px solid #dee2e6;
      
      .datatable-header-cell {
        font-weight: 600;
        color: #495057;
        padding: 1rem;
      }
    }

    // Body
    .datatable-body {
      .datatable-body-row {
        border-bottom: 1px solid #dee2e6;
        
        &:hover {
          background-color: #f8f9fa;
        }

        &.active {
          background-color: #e9ecef;
        }
      }

      .datatable-body-cell {
        padding: 0.75rem 1rem;
      }
    }

    // Footer
    .datatable-footer {
      background: #f8f9fa;
      border-top: 2px solid #dee2e6;
      padding: 1rem;

      .datatable-pager {
        text-align: right;
      }
    }
  }

  // Loading indicator
  .datatable-body-loading {
    background: rgba(255, 255, 255, 0.9);
    
    .progress-bar {
      background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
    }
  }
}
```

### 6. Testing

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';

describe('DataTableComponent', () => {
  let component: DataTableComponent;
  let fixture: ComponentFixture<DataTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DataTableComponent ],
      imports: [ 
        NgxDatatableModule,
        HttpClientTestingModule 
      ]
    }).compileComponents();
  });

  it('should load data on init', () => {
    fixture = TestBed.createComponent(DataTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    
    expect(component.rows.length).toBeGreaterThan(0);
  });

  it('should filter data correctly', () => {
    component.temp = [
      { name: 'John', email: 'john@test.com' },
      { name: 'Jane', email: 'jane@test.com' }
    ];
    
    const event = { target: { value: 'john' } };
    component.updateFilter(event);
    
    expect(component.rows.length).toBe(1);
    expect(component.rows[0].name).toBe('John');
  });
});
```

## Recursos Adicionales

### Enlaces Útiles

- 📖 [Documentación Oficial](https://swimlane.gitbook.io/ngx-datatable/)
- 🎮 [Demos Interactivos](http://swimlane.github.io/ngx-datatable/)
- 💻 [GitHub Repository](https://github.com/swimlane/ngx-datatable)
- 💬 [Gitter Chat](https://gitter.im/swimlane/ngx-datatable)

### Ejemplos por Característica

| Ejemplo | URL Demo |
|---------|----------|
| Virtual Scroll (10K filas) | [Ver Demo](https://swimlane.github.io/ngx-datatable/#/virtual-scroll) |
| Paginación Cliente | [Ver Demo](https://swimlane.github.io/ngx-datatable/#/client-paging) |
| Paginación Servidor | [Ver Demo](https://swimlane.github.io/ngx-datatable/#/server-paging) |
| Filtrado | [Ver Demo](https://swimlane.github.io/ngx-datatable/#/filter) |
| Selección Checkbox | [Ver Demo](https://swimlane.github.io/ngx-datatable/#/chkbox-selection) |
| Row Details | [Ver Demo](https://swimlane.github.io/ngx-datatable/#/row-details) |
| Inline Editing | [Ver Demo](https://swimlane.github.io/ngx-datatable/#/inline-edit) |

### Tips de Rendimiento

1. **Usa `trackBy`** para listas grandes:
```typescript
trackByFn(index: number, item: any) {
  return item.id;
}
```

2. **Limita el número de columnas visibles** en móviles

3. **Implementa paginación server-side** para más de 1000 registros

4. **Usa `ChangeDetectionStrategy.OnPush`** cuando sea posible

5. **Evita operaciones costosas** en templates (usa pipes puros)

6. **Habilita virtual scrolling** para grandes datasets

7. **Implementa debouncing** en filtros de búsqueda

8. **Cachea resultados** de API cuando sea apropiado

---

**Última actualización:** 15 de enero de 2026  
**Versión de ngx-datatable:** 22.0.0  
**Compatibilidad Angular:** 19-20+
