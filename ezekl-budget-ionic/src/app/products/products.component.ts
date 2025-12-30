import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonContent,
  IonHeader,
  IonTitle,
  IonToolbar,
  IonList,
  IonItem,
  IonLabel,
  IonSearchbar,
  IonSpinner,
  IonNote,
  IonIcon,
  IonButtons,
  IonButton,
  IonBackButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  ToastController,
  Platform
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  chevronForward,
  chevronDown,
  folderOutline,
  documentOutline,
  searchOutline,
  alertCircleOutline, arrowBack, informationCircleOutline } from 'ionicons/icons';
import { Subject, takeUntil } from 'rxjs';
import { ProductService } from '../services';
import { Product } from '../models';
import { ProductDetailComponent } from './product-detail/product-detail.component';

@Component({
  selector: 'app-products',
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonContent,
    IonHeader,
    IonTitle,
    IonToolbar,
    IonList,
    IonItem,
    IonLabel,
    IonSearchbar,
    IonSpinner,
    IonNote,
    IonIcon,
    IonButtons,
    IonButton,
    IonBackButton,
    IonCard,
    IonCardContent,
    IonCardHeader,
    IonCardTitle,
    ProductDetailComponent
  ]
})
export class ProductsComponent implements OnInit, OnDestroy {
  products: Product[] = [];
  filteredProducts: Product[] = [];
  searchText = '';
  loading = false;
  error: string | null = null;
  expandedItems: Set<number> = new Set();

  selectedProductId: number | null = null;
  isDesktop = false;

  private destroy$ = new Subject<void>();

  constructor(
    private productService: ProductService,
    private toastController: ToastController,
    private platform: Platform
  ) {
    addIcons({arrowBack,alertCircleOutline,documentOutline,folderOutline,informationCircleOutline,chevronForward,chevronDown,searchOutline});
  }

  ngOnInit() {
    this.checkScreenSize();
    this.loadProducts();

    // Escuchar cambios en el tamaño de la ventana
    this.platform.resize.pipe(takeUntil(this.destroy$)).subscribe(() => {
      this.checkScreenSize();
    });
  }

  /**
   * Verificar si es pantalla desktop (mayor a 768px)
   */
  checkScreenSize() {
    this.isDesktop = this.platform.width() >= 768;
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Cargar productos desde el servicio
   */
  loadProducts() {
    this.loading = true;
    this.error = null;

    this.productService.getProducts()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (products) => {
          this.products = products;
          this.filteredProducts = products;
          this.loading = false;
        },
        error: (error) => {
          this.error = error.message || 'Error al cargar los productos';
          this.loading = false;
          if (this.error) {
            this.showErrorToast(this.error);
          }
        }
      });
  }

  /**
   * Filtrar productos por texto de búsqueda
   */
  onSearch(event: any) {
    this.searchText = event.detail.value || '';

    if (!this.searchText.trim()) {
      this.filteredProducts = this.products;
      return;
    }

    this.filteredProducts = this.productService.searchProducts(this.searchText);
  }

  /**
   * Limpiar búsqueda
   */
  clearSearch() {
    this.searchText = '';
    this.filteredProducts = this.products;
  }

  /**
   * Toggle estado expandido de un producto
   */
  toggleExpand(productId: number) {
    if (this.expandedItems.has(productId)) {
      this.expandedItems.delete(productId);
    } else {
      this.expandedItems.add(productId);
    }
  }

  /**
   * Verificar si un producto está expandido
   */
  isExpanded(productId: number): boolean {
    return this.expandedItems.has(productId);
  }

  /**
   * Verificar si un producto tiene hijos
   */
  hasChildren(product: Product): boolean {
    return product.childrens !== null && product.childrens.length > 0;
  }

  /**
   * Obtener nivel de indentación para un producto
   */
  getIndentLevel(level: number): string {
    return `${level * 20}px`;
  }

  /**
   * Seleccionar un producto (mostrar detalle)
   */
  selectProduct(product: Product) {
    this.selectedProductId = product.idProduct;
  }

  /**
   * Volver al listado de productos
   */
  backToList() {
    this.selectedProductId = null;
  }

  /**
   * Refrescar lista de productos
   */
  refresh(event?: any) {
    this.loadProducts();
    if (event) {
      setTimeout(() => {
        event.target.complete();
      }, 1000);
    }
  }

  /**
   * Mostrar toast de error
   */
  private async showErrorToast(message: string) {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      position: 'bottom',
      color: 'danger',
      buttons: [
        {
          text: 'Cerrar',
          role: 'cancel'
        }
      ]
    });
    await toast.present();
  }
}
