import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, map, throwError } from 'rxjs';
import { LoggerService } from './logger.service';
import { environment } from '../../environments/environment';
import {
  MediaFile,
  MediaFileListResponse,
  MediaFileTotalResponse,
  MediaFileCreateResponse,
  MediaFileDeleteResponse,
  MediaFileListParams
} from '../shared/models';

/**
 * Servicio para gestión de archivos multimedia
 * Maneja la comunicación con el backend para operaciones CRUD de archivos
 */
@Injectable({
  providedIn: 'root'
})
export class MediaFileService {
  private readonly http = inject(HttpClient);
  private readonly logger = inject(LoggerService).getLogger('MediaFileService');
  
  private readonly baseUrl = `${environment.apiUrl}media-file`;

  /**
   * Obtiene la lista de archivos multimedia con paginación y filtros
   */
  getMediaFiles(params?: MediaFileListParams): Observable<MediaFileListResponse> {
    this.logger.debug('Obteniendo lista de archivos multimedia', params);
    
    let httpParams = new HttpParams();
    
    if (params) {
      if (params.search) httpParams = httpParams.set('search', params.search);
      if (params.sort) httpParams = httpParams.set('sort', params.sort);
      if (params.page) httpParams = httpParams.set('page', params.page.toString());
      if (params.itemPerPage) httpParams = httpParams.set('itemPerPage', params.itemPerPage.toString());
      if (params.mediaType) httpParams = httpParams.set('mediaType', params.mediaType);
    }
    
    return this.http.get<MediaFileListResponse>(`${this.baseUrl}.json`, { params: httpParams })
      .pipe(
        map(response => {
          this.logger.debug('Archivos obtenidos:', response);
          return response;
        }),
        catchError(error => {
          this.logger.error('Error al obtener archivos:', error);
          return throwError(() => error);
        })
      );
  }

  /**
   * Obtiene totales y estadísticas de archivos multimedia
   */
  getMediaFileTotals(): Observable<MediaFileTotalResponse> {
    this.logger.debug('Obteniendo totales de archivos multimedia');
    
    return this.http.get<MediaFileTotalResponse>(`${this.baseUrl}/total.json`)
      .pipe(
        map(response => {
          this.logger.debug('Totales obtenidos:', response);
          return response;
        }),
        catchError(error => {
          this.logger.error('Error al obtener totales:', error);
          return throwError(() => error);
        })
      );
  }

  /**
   * Sube un nuevo archivo multimedia
   */
  uploadMediaFile(file: File): Observable<MediaFileCreateResponse> {
    this.logger.debug('Subiendo archivo:', file.name);
    
    const formData = new FormData();
    formData.append('file', file);
    
    return this.http.post<MediaFileCreateResponse>(`${this.baseUrl}/`, formData)
      .pipe(
        map(response => {
          this.logger.success('Archivo subido exitosamente:', response);
          return response;
        }),
        catchError(error => {
          this.logger.error('Error al subir archivo:', error);
          return throwError(() => error);
        })
      );
  }

  /**
   * Obtiene la URL completa de un archivo multimedia
   */
  getMediaFileUrl(idMediaFile: number): string {
    return `${this.baseUrl}/${idMediaFile}`;
  }

  /**
   * Elimina un archivo multimedia
   */
  deleteMediaFile(idMediaFile: number): Observable<MediaFileDeleteResponse> {
    this.logger.debug('Eliminando archivo:', idMediaFile);
    
    return this.http.delete<MediaFileDeleteResponse>(`${this.baseUrl}/${idMediaFile}`)
      .pipe(
        map(response => {
          this.logger.success('Archivo eliminado exitosamente:', response);
          return response;
        }),
        catchError(error => {
          this.logger.error('Error al eliminar archivo:', error);
          return throwError(() => error);
        })
      );
  }

  /**
   * Formatea el tamaño del archivo a formato legible
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Obtiene el icono de Font Awesome según el tipo de archivo
   */
  getFileIcon(mediaType: string): string {
    const icons: { [key: string]: string } = {
      'image': 'fa-file-image',
      'video': 'fa-file-video',
      'audio': 'fa-file-audio',
      'document': 'fa-file-pdf'
    };
    return icons[mediaType] || 'fa-file';
  }

  /**
   * Obtiene el color según el tipo de archivo
   */
  getFileColor(mediaType: string): string {
    const colors: { [key: string]: string } = {
      'image': 'primary',
      'video': 'danger',
      'audio': 'success',
      'document': 'warning'
    };
    return colors[mediaType] || 'secondary';
  }
}
