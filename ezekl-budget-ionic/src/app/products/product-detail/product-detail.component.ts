import { Component, OnInit, OnDestroy, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  IonContent,
  IonHeader,
  IonTitle,
  IonToolbar,
  IonList,
  IonItem,
  IonLabel,
  IonSpinner,
  IonNote,
  IonIcon,
  IonButtons,
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonBadge,
  ToastController
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  closeOutline,
  informationCircleOutline,
  cashOutline,
  cartOutline,
  listOutline,
  alertCircleOutline
} from 'ionicons/icons';
import { Subject, takeUntil } from 'rxjs';
import { ProductService } from '../../services';
import { ProductDetail } from '../../models';

@Component({
  selector: 'app-product-detail',
  templateUrl: './product-detail.component.html',
  styleUrls: ['./product-detail.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    IonContent,
    IonHeader,
    IonTitle,
    IonToolbar,
    IonList,
    IonItem,
    IonLabel,
    IonSpinner,
    IonNote,
    IonIcon,
    IonButtons,
    IonButton,
    IonCard,
    IonCardContent,
    IonCardHeader,
    IonCardTitle,
    IonBadge
  ]
})
export class ProductDetailComponent implements OnInit, OnChanges, OnDestroy {
  @Input() productId!: number;
  @Input() showHeader = true;
  @Output() close = new EventEmitter<void>();

  product: ProductDetail | null = null;
  loading = false;
  error: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(
    private productService: ProductService,
    private toastController: ToastController
  ) {
    addIcons({
      closeOutline,
      alertCircleOutline,
      informationCircleOutline,
      cashOutline,
      cartOutline,
      listOutline
    });
  }

  ngOnInit() {
    // El productId viene como @Input
    if (this.productId) {
      this.loadProductDetail();
    } else {
      this.error = 'ID de producto no válido';
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    // Detectar cuando cambia el productId
    if (changes['productId'] && !changes['productId'].firstChange) {
      if (this.productId) {
        this.loadProductDetail();
      }
    }
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Cargar detalle del producto desde el servicio
   */
  loadProductDetail() {
    this.loading = true;
    this.error = null;

    this.productService.getProduct(this.productId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (product) => {
          this.product = product;
          this.loading = false;
        },
        error: (error) => {
          this.error = error.message || 'Error al cargar el producto';
          this.loading = false;
          if (this.error) {
            this.showErrorToast(this.error);
          }
        }
      });
  }

  /**
   * Obtener etiqueta del efecto contable
   */
  getEffectLabel(effect: number): string {
    return effect === 1 ? 'Incrementa' : 'Disminuye';
  }

  /**
   * Obtener color del efecto contable
   */
  getEffectColor(effect: number): string {
    return effect === 1 ? 'success' : 'danger';
  }

  /**
   * Formatear precio
   */
  formatPrice(price: number): string {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(price);
  }

  /**
   * Cerrar detalle
   */
  closeDetail() {
    this.close.emit();
  }

  /**
   * Refrescar detalle del producto
   */
  refresh(event?: any) {
    this.loadProductDetail();
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
