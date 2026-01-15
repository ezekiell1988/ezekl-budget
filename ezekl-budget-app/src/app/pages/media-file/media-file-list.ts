import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { addIcons } from 'ionicons';
import { Subject, takeUntil } from 'rxjs';
import {
  cloudUploadOutline,
  searchOutline,
  trashOutline,
  eyeOutline,
  documentOutline,
  imageOutline,
  videocamOutline,
  musicalNoteOutline
} from 'ionicons/icons';
import {
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonList,
  IonItem,
  IonLabel,
  IonButton,
  IonIcon,
  IonBadge,
  IonSearchbar,
  IonSelect,
  IonSelectOption,
  IonGrid,
  IonRow,
  IonCol,
  IonChip,
  IonFab,
  IonFabButton,
  AlertController,
  ToastController
} from '@ionic/angular/standalone';
import { ResponsiveComponent } from '../../shared';
import { AppSettings, LoggerService, MediaFileService } from '../../service';
import { HeaderComponent, FooterComponent, PanelComponent } from '../../components';
import {
  MediaFile,
  MediaFileListResponse,
  MediaFileTotalResponse
} from '../../shared/models';

@Component({
  selector: '[media-file-list]',
  templateUrl: './media-file-list.html',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonList,
    IonItem,
    IonLabel,
    IonButton,
    IonIcon,
    IonBadge,
    IonSearchbar,
    IonSelect,
    IonSelectOption,
    IonGrid,
    IonRow,
    IonCol,
    IonChip,
    IonFab,
    IonFabButton,
    HeaderComponent,
    FooterComponent,
    PanelComponent
  ]
})
export class MediaFileListPage extends ResponsiveComponent implements OnInit, OnDestroy {
  readonly appSettings = inject(AppSettings);
  private readonly logger = inject(LoggerService).getLogger('MediaFileListPage');
  private readonly mediaFileService = inject(MediaFileService);
  private readonly router = inject(Router);
  private readonly alertController = inject(AlertController);
  private readonly toastController = inject(ToastController);
  private readonly destroy$ = new Subject<void>();

  // Estado de la aplicación
  mediaFiles: MediaFile[] = [];
  totals: MediaFileTotalResponse | null = null;
  loading = false;
  
  // Filtros y paginación
  searchText = '';
  selectedMediaType: string | null = null;
  currentPage = 1;
  itemsPerPage = 10;
  totalItems = 0;

  constructor() {
    super();
    addIcons({
      cloudUploadOutline,
      searchOutline,
      trashOutline,
      eyeOutline,
      documentOutline,
      imageOutline,
      videocamOutline,
      musicalNoteOutline
    });
  }

  getPageTitle(): string {
    return 'Archivos Multimedia';
  }

  ngOnInit() {
    this.logger.debug('Inicializando MediaFileListPage');
    this.loadData();
  }

  override ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Carga los datos de archivos y totales
   */
  loadData() {
    this.loading = true;
    this.loadMediaFiles();
    this.loadTotals();
  }

  /**
   * Carga la lista de archivos multimedia
   */
  loadMediaFiles() {
    this.mediaFileService.getMediaFiles({
      search: this.searchText || undefined,
      mediaType: this.selectedMediaType as any,
      page: this.currentPage,
      itemPerPage: this.itemsPerPage,
      sort: 'createAt_desc'
    })
    .pipe(takeUntil(this.destroy$))
    .subscribe({
      next: (response) => {
        this.mediaFiles = response.data;
        this.totalItems = response.total;
        this.loading = false;
        this.logger.debug('Archivos cargados:', response);
      },
      error: (error) => {
        this.logger.error('Error al cargar archivos:', error);
        this.loading = false;
        this.showToast('Error al cargar archivos', 'danger');
      }
    });
  }

  /**
   * Carga los totales de archivos
   */
  loadTotals() {
    this.mediaFileService.getMediaFileTotals()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.totals = response;
          this.logger.debug('Totales cargados:', response);
        },
        error: (error) => {
          this.logger.error('Error al cargar totales:', error);
        }
      });
  }

  /**
   * Busca archivos por texto
   */
  onSearch(event: any) {
    this.searchText = event.target?.value || event.detail?.value || '';
    this.currentPage = 1;
    this.loadMediaFiles();
  }

  /**
   * Filtra por tipo de medio
   */
  onMediaTypeChange(event: any) {
    this.selectedMediaType = event.target?.value || event.detail?.value || null;
    if (this.selectedMediaType === 'all') {
      this.selectedMediaType = null;
    }
    this.currentPage = 1;
    this.loadMediaFiles();
  }

  /**
   * Navega a la página de subida de archivos
   */
  goToUpload() {
    this.router.navigate(['/media-file/upload']);
  }

  /**
   * Visualiza un archivo
   */
  viewFile(file: MediaFile) {
    const url = this.mediaFileService.getMediaFileUrl(file.idMediaFile);
    window.open(url, '_blank');
  }

  /**
   * Elimina un archivo
   */
  async deleteFile(file: MediaFile) {
    const alert = await this.alertController.create({
      header: 'Confirmar eliminación',
      message: `¿Estás seguro de eliminar el archivo "${file.nameMediaFile}"?`,
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Eliminar',
          role: 'destructive',
          handler: () => {
            this.confirmDelete(file.idMediaFile);
          }
        }
      ]
    });

    await alert.present();
  }

  /**
   * Confirma la eliminación del archivo
   */
  private confirmDelete(idMediaFile: number) {
    this.mediaFileService.deleteMediaFile(idMediaFile)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.showToast('Archivo eliminado exitosamente', 'success');
          this.loadData();
        },
        error: (error) => {
          this.logger.error('Error al eliminar archivo:', error);
          this.showToast('Error al eliminar archivo', 'danger');
        }
      });
  }

  /**
   * Cambia de página
   */
  changePage(page: number) {
    this.currentPage = page;
    this.loadMediaFiles();
  }

  /**
   * Formatea el tamaño del archivo
   */
  formatSize(bytes: number): string {
    return this.mediaFileService.formatFileSize(bytes);
  }

  /**
   * Obtiene el icono del archivo
   */
  getFileIcon(mediaType: string): string {
    return this.mediaFileService.getFileIcon(mediaType);
  }

  /**
   * Obtiene el color del archivo
   */
  getFileColor(mediaType: string): string {
    return this.mediaFileService.getFileColor(mediaType);
  }

  /**
   * Calcula el número de páginas
   */
  get totalPages(): number {
    return Math.ceil(this.totalItems / this.itemsPerPage);
  }

  /**
   * Muestra un mensaje toast
   */
  private async showToast(message: string, color: string) {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      color,
      position: 'top'
    });
    await toast.present();
  }
}
