/**
 * Servicio para gestionar productos
 * Maneja la comunicación con la API de productos con estructura jerárquica
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { Product, ProductResponse, ProductDetail } from '../models';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private readonly API_BASE: string;

  // Estado de la lista actual
  private products$ = new BehaviorSubject<Product[]>([]);
  private loading$ = new BehaviorSubject<boolean>(false);
  private error$ = new BehaviorSubject<string | null>(null);

  constructor(private http: HttpClient) {
    // Usar ruta relativa si apiUrl está vacío (funciona con cualquier puerto)
    const baseUrl = environment.apiUrl || '';
    this.API_BASE = baseUrl ? `${baseUrl}/api/v1/products` : '/api/v1/products';
  }

  // Observables públicos para los componentes
  get products(): Observable<Product[]> {
    return this.products$.asObservable();
  }

  get loading(): Observable<boolean> {
    return this.loading$.asObservable();
  }

  get error(): Observable<string | null> {
    return this.error$.asObservable();
  }

  /**
   * Obtiene todos los productos con estructura jerárquica
   */
  getProducts(): Observable<Product[]> {
    this.setLoading(true);
    this.setError(null);

    return this.http.get<Product[]>(this.API_BASE).pipe(
      tap(products => {
        this.products$.next(products);
        this.setLoading(false);
      }),
      catchError(error => {
        const errorMessage = this.handleError(error);
        this.setError(errorMessage);
        this.setLoading(false);
        return throwError(() => new Error(errorMessage));
      })
    );
  }

  /**
   * Obtiene un producto específico por ID con detalle completo
   */
  getProduct(idProduct: number): Observable<ProductDetail> {
    this.setLoading(true);
    this.setError(null);

    return this.http.get<ProductDetail>(`${this.API_BASE}/${idProduct}`).pipe(
      tap(() => this.setLoading(false)),
      catchError(error => {
        const errorMessage = this.handleError(error);
        this.setError(errorMessage);
        this.setLoading(false);
        return throwError(() => new Error(errorMessage));
      })
    );
  }

  /**
   * Crear nuevo producto
   */
  createProduct(product: Partial<Product>): Observable<{ idProduct: number }> {
    this.setLoading(true);
    this.setError(null);

    return this.http.post<{ idProduct: number }>(this.API_BASE, product).pipe(
      tap(() => this.setLoading(false)),
      catchError(error => {
        const errorMessage = this.handleError(error);
        this.setError(errorMessage);
        this.setLoading(false);
        return throwError(() => new Error(errorMessage));
      })
    );
  }

  /**
   * Actualizar producto existente
   */
  updateProduct(idProduct: number, product: Partial<Product>): Observable<void> {
    this.setLoading(true);
    this.setError(null);

    return this.http.put<void>(`${this.API_BASE}/${idProduct}`, product).pipe(
      tap(() => this.setLoading(false)),
      catchError(error => {
        const errorMessage = this.handleError(error);
        this.setError(errorMessage);
        this.setLoading(false);
        return throwError(() => new Error(errorMessage));
      })
    );
  }

  /**
   * Eliminar producto
   */
  deleteProduct(idProduct: number): Observable<void> {
    this.setLoading(true);
    this.setError(null);

    return this.http.delete<void>(`${this.API_BASE}/${idProduct}`).pipe(
      tap(() => this.setLoading(false)),
      catchError(error => {
        const errorMessage = this.handleError(error);
        this.setError(errorMessage);
        this.setLoading(false);
        return throwError(() => new Error(errorMessage));
      })
    );
  }

  /**
   * Buscar productos por texto
   * @param searchText Texto a buscar en nombre y descripción
   * @returns Array de productos que coinciden (incluye búsqueda recursiva en hijos)
   */
  searchProducts(searchText: string): Product[] {
    const search = searchText.toLowerCase().trim();
    if (!search) {
      return this.products$.value;
    }

    const searchInProduct = (product: Product): Product | null => {
      const matches =
        product.nameProduct.toLowerCase().includes(search) ||
        product.descriptionProduct.toLowerCase().includes(search);

      let matchedChildren: Product[] = [];
      if (product.childrens) {
        matchedChildren = product.childrens
          .map(child => searchInProduct(child))
          .filter(child => child !== null) as Product[];
      }

      if (matches || matchedChildren.length > 0) {
        return {
          ...product,
          childrens: matchedChildren.length > 0 ? matchedChildren : product.childrens
        };
      }

      return null;
    };

    return this.products$.value
      .map(product => searchInProduct(product))
      .filter(product => product !== null) as Product[];
  }

  /**
   * Aplanar estructura jerárquica de productos para búsquedas más simples
   */
  flattenProducts(products?: Product[]): Product[] {
    const productsToFlatten = products || this.products$.value;
    const flattened: Product[] = [];

    const flatten = (product: Product) => {
      flattened.push(product);
      if (product.childrens) {
        product.childrens.forEach(child => flatten(child));
      }
    };

    productsToFlatten.forEach(product => flatten(product));
    return flattened;
  }

  // Métodos privados de utilidad
  private setLoading(loading: boolean): void {
    this.loading$.next(loading);
  }

  private setError(error: string | null): void {
    this.error$.next(error);
  }

  private handleError(error: HttpErrorResponse): string {
    let errorMessage = 'Ocurrió un error al comunicarse con el servidor';

    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Error del lado del servidor
      if (error.status === 401) {
        errorMessage = 'No autorizado. Por favor, inicie sesión nuevamente.';
      } else if (error.status === 403) {
        errorMessage = 'No tiene permisos para realizar esta acción.';
      } else if (error.status === 404) {
        errorMessage = 'Producto no encontrado.';
      } else if (error.status === 500) {
        errorMessage = 'Error interno del servidor. Por favor, intente más tarde.';
      } else if (error.error?.message) {
        errorMessage = error.error.message;
      }
    }

    console.error('Error en ProductService:', errorMessage, error);
    return errorMessage;
  }

  /**
   * Limpiar estado del servicio
   */
  clearState(): void {
    this.products$.next([]);
    this.setLoading(false);
    this.setError(null);
  }
}
