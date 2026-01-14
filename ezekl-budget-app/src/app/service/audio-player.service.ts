import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

/**
 * Servicio para reproducir audio del bot con soporte para interrupción
 */
@Injectable({
  providedIn: 'root'
})
export class AudioPlayerService {
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
        console.log(`🎵 Intentando reproducir audio (${audioBase64.length} caracteres)`);
        
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
          console.log('✅ Audio cargado correctamente');
        };
        
        audio.onended = () => {
          console.log('✅ Audio terminó de reproducirse');
          URL.revokeObjectURL(url); // Limpiar el blob URL
          this.currentAudioSubject.next(null);
          this.isPlayingSubject.next(false);
          resolve();
        };
        
        audio.onerror = (error) => {
          console.error('❌ Error reproduciendo audio:', error);
          console.error('Audio element error event:', audio.error);
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
              console.log('▶️ Audio iniciado correctamente');
            })
            .catch(error => {
              console.error('❌ Error al iniciar reproducción:', error);
              console.error('Puede ser que se necesite interacción del usuario para reproducir audio');
              URL.revokeObjectURL(url);
              this.currentAudioSubject.next(null);
              this.isPlayingSubject.next(false);
              resolve();
            });
        }
      } catch (error) {
        console.error('❌ Error creando audio:', error);
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
      console.log('🛑 Deteniendo audio actual');
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
      console.log('⏸️ Pausando audio');
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
      console.log('▶️ Reanudando audio');
      audio.play()
        .then(() => {
          this.isPlayingSubject.next(true);
        })
        .catch(error => {
          console.error('❌ Error al reanudar audio:', error);
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
