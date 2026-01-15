import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { addIcons } from 'ionicons';
import { Subject, takeUntil } from 'rxjs';
import {
  cloudUploadOutline,
  arrowBackOutline,
  checkmarkOutline
} from 'ionicons/icons';
import {
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonButton,
  IonIcon,
  IonList,
  IonItem,
  IonLabel,
  IonText,
  ToastController
} from '@ionic/angular/standalone';
import { ResponsiveComponent } from '../../shared';
import { AppSettings, LoggerService, MediaFileService } from '../../service';
import { HeaderComponent, FooterComponent, PanelComponent } from '../../components';

@Component({
  selector: '[media-file-upload]',
  templateUrl: './media-file-upload.html',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonButton,
    IonIcon,
    IonList,
    IonItem,
    IonLabel,
    IonText,
    HeaderComponent,
    FooterComponent,
    PanelComponent
  ]
})
export class MediaFileUploadPage extends ResponsiveComponent implements OnInit, OnDestroy {
  readonly appSettings = inject(AppSettings);
  private readonly logger = inject(LoggerService).getLogger('MediaFileUploadPage');
  private readonly mediaFileService = inject(MediaFileService);
  private readonly router = inject(Router);
  private readonly toastController = inject(ToastController);
  private readonly destroy$ = new Subject<void>();

  // Estado de la aplicación
  selectedFile: File | null = null;
  uploading = false;
  uploadProgress = 0;

  constructor() {
    super();
    addIcons({
      cloudUploadOutline,
      arrowBackOutline,
      checkmarkOutline
    });
  }

  getPageTitle(): string {
    return 'Subir Archivo';
  }

  ngOnInit() {
    this.logger.debug('Inicializando MediaFileUploadPage');
  }

  override ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Maneja la selección de archivo
   */
  onFileSelected(event: any) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      this.logger.debug('Archivo seleccionado:', this.selectedFile.name);
    }
  }

  /**
   * Obtiene información del archivo seleccionado
   */
  getFileInfo(): string {
    if (!this.selectedFile) return '';
    return `${this.selectedFile.name} (${this.mediaFileService.formatFileSize(this.selectedFile.size)})`;
  }

  /**
   * Sube el archivo al servidor
   */
  uploadFile() {
    if (!this.selectedFile) {
      this.showToast('Por favor selecciona un archivo', 'warning');
      return;
    }

    this.uploading = true;
    this.uploadProgress = 0;

    this.mediaFileService.uploadMediaFile(this.selectedFile)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.logger.success('Archivo subido exitosamente:', response);
          this.showToast('Archivo subido exitosamente', 'success');
          this.uploading = false;
          this.uploadProgress = 100;
          
          // Redirigir después de 1 segundo
          setTimeout(() => {
            this.goBack();
          }, 1000);
        },
        error: (error) => {
          this.logger.error('Error al subir archivo:', error);
          this.showToast('Error al subir archivo', 'danger');
          this.uploading = false;
          this.uploadProgress = 0;
        }
      });
  }

  /**
   * Vuelve a la lista de archivos
   */
  goBack() {
    this.router.navigate(['/media-file']);
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
