import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { AUDIO_CONFIG, getMicrophoneConstraints } from '../shared/config/audio.config';
import { LoggerService } from './logger.service';

/**
 * Servicio para manejar la grabación de audio del micrófono
 * Utiliza MediaRecorder API y detecta silencios
 */
@Injectable({
  providedIn: 'root'
})
export class AudioRecorderService {
  private readonly logger = inject(LoggerService).getLogger('AudioRecorderService');
  private mediaRecorder: MediaRecorder | null = null;
  private audioStream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  
  private isRecording$ = new BehaviorSubject<boolean>(false);
  private audioLevel$ = new BehaviorSubject<number>(0);
  private audioChunks: Blob[] = [];
  
  private silenceDetectionTimer: any = null;
  private lastSoundTime: number = 0;
  
  // VAD continuo - independiente del estado de grabación
  private vadAnimationFrame: number | null = null;
  private isVADActive = false;
  private consecutiveVoiceFrames = 0;

  constructor() {}

  /**
   * Inicializa el micrófono y prepara la grabación
   */
  async initialize(): Promise<void> {
    try {
      // Solicitar acceso al micrófono
      const constraints = getMicrophoneConstraints();
      this.audioStream = await navigator.mediaDevices.getUserMedia(constraints);
      
      // Crear contexto de audio para análisis
      this.audioContext = new AudioContext({ sampleRate: AUDIO_CONFIG.microphone.sampleRate });
      const source = this.audioContext.createMediaStreamSource(this.audioStream);
      
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      source.connect(this.analyser);
      
      // Crear MediaRecorder
      const mimeType = AUDIO_CONFIG.recording.mimeType;
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        throw new Error(`Formato de audio ${mimeType} no soportado`);
      }
      
      this.mediaRecorder = new MediaRecorder(this.audioStream, {
        mimeType,
        audioBitsPerSecond: 16000
      });
      
      this.setupMediaRecorderEvents();
      
      this.logger.success('Micrófono inicializado correctamente');
    } catch (error) {
      this.logger.error('Error inicializando micrófono:', error);
      throw new Error('No se pudo acceder al micrófono. Verifica los permisos.');
    }
  }

  /**
   * Configura los eventos del MediaRecorder
   */
  private setupMediaRecorderEvents(): void {
    if (!this.mediaRecorder) return;

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        this.audioChunks.push(event.data);
      }
    };

    this.mediaRecorder.onerror = (event: any) => {
      this.logger.error('Error en MediaRecorder:', event.error);
      this.stopRecording();
    };
  }

  /**
   * Inicia la grabación de audio
   */
  startRecording(): void {
    if (!this.mediaRecorder || this.mediaRecorder.state === 'recording') {
      this.logger.warn('MediaRecorder no disponible o ya está grabando');
      return;
    }

    this.audioChunks = [];
    this.lastSoundTime = Date.now();
    
    try {
      this.mediaRecorder.start(AUDIO_CONFIG.recording.chunkDurationMs);
      this.isRecording$.next(true);
      this.startAudioLevelMonitoring();
      
      this.logger.success('Grabación iniciada');
    } catch (error) {
      this.logger.error('Error al iniciar grabación:', error);
    }
  }

  /**
   * Detiene la grabación y retorna el audio grabado
   */
  async stopRecording(): Promise<Blob | null> {
    if (!this.mediaRecorder || this.mediaRecorder.state !== 'recording') {
      return null;
    }

    return new Promise((resolve) => {
      if (!this.mediaRecorder) {
        resolve(null);
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { 
          type: AUDIO_CONFIG.recording.mimeType 
        });
        
        this.audioChunks = [];
        this.isRecording$.next(false);
        this.stopAudioLevelMonitoring();
        
        this.logger.debug(`Grabación detenida. Tamaño: ${audioBlob.size} bytes`);
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Pausa la grabación (sin perder el audio grabado)
   */
  pauseRecording(): void {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.pause();
      this.isRecording$.next(false);
      this.stopAudioLevelMonitoring();
      this.logger.debug('Grabación pausada');
    }
  }

  /**
   * Reanuda la grabación pausada
   */
  resumeRecording(): void {
    if (this.mediaRecorder && this.mediaRecorder.state === 'paused') {
      this.mediaRecorder.resume();
      this.isRecording$.next(true);
      this.startAudioLevelMonitoring();
      this.logger.debug('Grabación reanudada');
    }
  }

  /**
   * Descarta el audio grabado sin enviarlo
   */
  discardRecording(): void {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
      this.audioChunks = [];
      this.isRecording$.next(false);
      this.stopAudioLevelMonitoring();
      this.logger.debug('Grabación descartada');
    }
  }

  /**
   * Inicia el monitoreo del nivel de audio
   */
  private startAudioLevelMonitoring(): void {
    if (!this.analyser) return;

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const checkAudioLevel = () => {
      if (!this.analyser || !this.isRecording$.value) return;

      this.analyser.getByteFrequencyData(dataArray);
      
      // Calcular nivel promedio de audio
      const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
      this.audioLevel$.next(Math.round(average));

      // Detectar si hay sonido o silencio
      if (average > AUDIO_CONFIG.recording.silenceLevel) {
        this.lastSoundTime = Date.now();
      }

      requestAnimationFrame(checkAudioLevel);
    };

    checkAudioLevel();
  }

  /**
   * Inicia VAD continuo - monitorea el micrófono siempre, incluso cuando no graba
   * Útil para detectar cuando el usuario interrumpe al bot
   */
  startContinuousVAD(): void {
    if (!this.analyser || this.isVADActive) return;

    this.isVADActive = true;
    this.consecutiveVoiceFrames = 0;
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const checkAudioLevel = () => {
      if (!this.analyser || !this.isVADActive) {
        this.vadAnimationFrame = null;
        return;
      }

      this.analyser.getByteFrequencyData(dataArray);
      
      // Calcular nivel promedio de audio
      const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
      this.audioLevel$.next(Math.round(average));

      // Actualizar último tiempo de sonido
      if (average > AUDIO_CONFIG.vad.energyThreshold) {
        this.lastSoundTime = Date.now();
        this.consecutiveVoiceFrames++;
      } else {
        this.consecutiveVoiceFrames = 0;
      }

      this.vadAnimationFrame = requestAnimationFrame(checkAudioLevel);
    };

    checkAudioLevel();
    this.logger.debug('VAD continuo activado (umbral: ' + AUDIO_CONFIG.vad.energyThreshold + ', frames: ' + AUDIO_CONFIG.vad.consecutiveFrames + ')');
  }

  /**
   * Detiene VAD continuo
   */
  stopContinuousVAD(): void {
    this.isVADActive = false;
    this.consecutiveVoiceFrames = 0;
    if (this.vadAnimationFrame) {
      cancelAnimationFrame(this.vadAnimationFrame);
      this.vadAnimationFrame = null;
    }
    this.audioLevel$.next(0);
    this.logger.debug('VAD continuo desactivado');
  }

  /**
   * Verifica si se detectó voz de forma consistente
   * Usa sistema de frames consecutivos para evitar falsos positivos
   */
  get hasVoiceDetected(): boolean {
    return this.consecutiveVoiceFrames >= AUDIO_CONFIG.vad.consecutiveFrames;
  }

  /**
   * Detiene el monitoreo del nivel de audio
   */
  private stopAudioLevelMonitoring(): void {
    this.audioLevel$.next(0);
  }

  /**
   * Verifica si hay silencio prolongado
   */
  isSilent(): boolean {
    const silenceDuration = Date.now() - this.lastSoundTime;
    return silenceDuration > AUDIO_CONFIG.recording.silenceThresholdMs;
  }

  /**
   * Libera recursos del micrófono
   */
  cleanup(): void {
    // Detener VAD continuo
    this.stopContinuousVAD();

    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    }

    if (this.audioStream) {
      this.audioStream.getTracks().forEach(track => track.stop());
      this.audioStream = null;
    }

    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.mediaRecorder = null;
    this.analyser = null;
    this.audioChunks = [];
    this.isRecording$.next(false);
    this.audioLevel$.next(0);

    this.logger.debug('Micrófono liberado');
  }

  // ============= Getters =============
  
  get isRecording(): Observable<boolean> {
    return this.isRecording$.asObservable();
  }

  get audioLevel(): Observable<number> {
    return this.audioLevel$.asObservable();
  }

  get isInitialized(): boolean {
    return this.mediaRecorder !== null;
  }

  get recordingState(): RecordingState {
    if (!this.mediaRecorder) return 'inactive';
    return this.mediaRecorder.state as RecordingState;
  }
}

type RecordingState = 'inactive' | 'recording' | 'paused';
