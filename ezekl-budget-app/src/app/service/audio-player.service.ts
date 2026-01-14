import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { LoggerService } from './logger.service';

/**
 * Servicio para reproducir audio del bot con soporte para interrupción
 */
@Injectable({
  providedIn: 'root'
})
export class AudioPlayerService {
  private readonly logger = inject(LoggerService).getLogger('AudioPlayerService');
  private currentAudioSubject = new BehaviorSubject<HTMLAudioElement | null>(null);
  private isPlayingSubject = new BehaviorSubject<boolean>(false);

  currentAudio$: Observable<HTMLAudioElement | null> = this.currentAudioSubject.asObservable();
  isPlaying$: Observable<boolean> = this.isPlayingSubject.asObservable();

  get currentAudio(): HTMLAudioElement | null {
    return this.currentAudioSubject.value;
  }

  get isPlaying(): boolean {
    return this.isPlayingSubject.value;
  }

  /**
   * Reproduce audio desde base64
   * Optimizado para iOS/Safari con playsinline y blob URLs
   */
  async playAudio(audioBase64: string): Promise<void> {
    return new Promise((resolve) => {
      try {
        this.logger.debug(`Intentando reproducir audio (${audioBase64.length} caracteres)`);
        
        // Detener audio anterior si existe
        this.stopAudio();
        
        // Crear elemento de audio con configuración para iOS
        const audio = new Audio();
        
        // Configuración para iOS/Safari
        audio.setAttribute('playsinline', 'true');
        audio.preload = 'auto';
        
        // Convertir base64 a blob para mejor compatibilidad en iOS
        const byteCharacters = atob(audioBase64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'audio/mpeg' });
        const url = URL.createObjectURL(blob);
        
        audio.src = url;
        
        // Guardar referencia del audio actual
        this.currentAudioSubject.next(audio);
        this.isPlayingSubject.next(true);
        
        audio.onloadeddata = () => {
          this.logger.success('Audio cargado correctamente');
        };
        
        audio.onended = () => {
          this.logger.success('Audio terminó de reproducirse');
          URL.revokeObjectURL(url); // Limpiar el blob URL
          this.currentAudioSubject.next(null);
          this.isPlayingSubject.next(false);
          resolve();
        };
        
        audio.onerror = (error) => {
          this.logger.error('Error reproduciendo audio:', error);
          this.logger.error('Audio element error event:', audio.error);
          URL.revokeObjectURL(url); // Limpiar el blob URL
          this.currentAudioSubject.next(null);
          this.isPlayingSubject.next(false);
          resolve(); // Resolver de todas formas para continuar el flujo
        };
        
        // En iOS, la reproducción debe iniciar de inmediato
        const playPromise = audio.play();
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              this.logger.success('Audio iniciado correctamente');
            })
            .catch(error => {
              this.logger.error('Error al iniciar reproducción:', error);
              this.logger.warn('Puede ser que se necesite interacción del usuario para reproducir audio');
              URL.revokeObjectURL(url);
              this.currentAudioSubject.next(null);
              this.isPlayingSubject.next(false);
              resolve();
            });
        }
      } catch (error) {
        this.logger.error('Error creando audio:', error);
        this.currentAudioSubject.next(null);
        this.isPlayingSubject.next(false);
        resolve();
      }
    });
  }

  /**
   * Detiene la reproducción del audio actual
   */
  stopAudio(): void {
    const audio = this.currentAudioSubject.value;
    if (audio) {
      this.logger.debug('Deteniendo audio actual');
      audio.pause();
      audio.currentTime = 0;
      this.currentAudioSubject.next(null);
      this.isPlayingSubject.next(false);
    }
  }

  /**
   * Pausa el audio actual (sin reiniciar posición)
   */
  pauseAudio(): void {
    const audio = this.currentAudioSubject.value;
    if (audio && !audio.paused) {
      this.logger.debug('Pausando audio');
      audio.pause();
      this.isPlayingSubject.next(false);
    }
  }

  /**
   * Reanuda el audio pausado
   */
  resumeAudio(): void {
    const audio = this.currentAudioSubject.value;
    if (audio && audio.paused) {
      this.logger.debug('Reanudando audio');
      audio.play()
        .then(() => {
          this.isPlayingSubject.next(true);
        })
        .catch(error => {
          this.logger.error('Error al reanudar audio:', error);
        });
    }
  }

  /**
   * Limpia todos los recursos de audio
   */
  cleanup(): void {
    this.stopAudio();
  }
}
