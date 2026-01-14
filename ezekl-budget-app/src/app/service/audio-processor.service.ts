import { Injectable, inject } from '@angular/core';
import { LoggerService } from './logger.service';

/**
 * Servicio para procesar y convertir audio
 */
@Injectable({
  providedIn: 'root'
})
export class AudioProcessorService {
  private readonly logger = inject(LoggerService).getLogger('AudioProcessorService');

  /**
   * Convierte un Blob de audio a formato Base64
   * Usado para enviar audio al backend via WebSocket
   */
  async convertBlobToBase64(audioBlob: Blob): Promise<string | null> {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onloadend = () => {
        const base64String = reader.result as string;
        // Remover el prefijo "data:audio/webm;base64," si existe
        const base64Data = base64String.split(',')[1] || base64String;
        resolve(base64Data);
      };
      
      reader.onerror = (error) => {
        this.logger.error('Error convirtiendo audio a base64:', error);
        reject(error);
      };
      
      reader.readAsDataURL(audioBlob);
    });
  }

  /**
   * Convierte base64 a Blob
   * Útil para crear URLs de audio para reproducción
   */
  base64ToBlob(base64: string, mimeType: string = 'audio/mpeg'): Blob {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  }

  /**
   * Crea una URL de objeto desde un Blob
   * Recordar revocar la URL con URL.revokeObjectURL() cuando ya no se necesite
   */
  createObjectURL(blob: Blob): string {
    return URL.createObjectURL(blob);
  }

  /**
   * Valida que un blob de audio sea válido
   */
  isValidAudioBlob(blob: Blob): boolean {
    if (!blob) return false;
    if (blob.size === 0) {
      this.logger.warn('Blob de audio está vacío');
      return false;
    }
    return true;
  }

  /**
   * Obtiene información del blob de audio
   */
  getAudioBlobInfo(blob: Blob): { size: number; type: string; sizeInKB: string } {
    const sizeInKB = (blob.size / 1024).toFixed(2);
    return {
      size: blob.size,
      type: blob.type,
      sizeInKB: `${sizeInKB} KB`
    };
  }

  /**
   * Valida formato de audio base64
   */
  isValidBase64Audio(base64: string): boolean {
    if (!base64 || base64.length === 0) {
      this.logger.warn('String base64 está vacío');
      return false;
    }
    
    // Verificar que sea base64 válido
    try {
      atob(base64);
      return true;
    } catch (e) {
      this.logger.error('String base64 inválido:', e);
      return false;
    }
  }
}
