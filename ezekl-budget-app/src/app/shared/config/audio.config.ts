/**
 * Configuración para grabación y reproducción de audio
 */

export const AUDIO_CONFIG = {
  // Configuración del micrófono
  microphone: {
    sampleRate: 16000,
    channelCount: 1,
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true
  },
  
  // Configuración de la grabación
  recording: {
    // Formato de audio
    mimeType: 'audio/webm;codecs=opus',
    
    // Tiempo mínimo de silencio para considerar fin de frase (ms)
    silenceThresholdMs: 1500,
    
    // Nivel de audio para considerar silencio (0-255)
    silenceLevel: 30,
    
    // Tamaño del chunk de audio (ms)
    chunkDurationMs: 100,
    
    // Tiempo máximo de grabación continua (ms)
    maxRecordingDurationMs: 60000
  },
  
  // Configuración de reproducción
  playback: {
    volume: 1.0,
    autoPlay: true
  },
  
  // Detección de voz (VAD - Voice Activity Detection)
  vad: {
    enabled: true,
    // Umbral de energía para considerar que hay voz
    energyThreshold: 40,
    // Número de frames consecutivos con voz para activar
    consecutiveFrames: 3
  }
} as const;

/**
 * Obtiene las constraints de MediaStream para el micrófono
 */
export function getMicrophoneConstraints(): MediaStreamConstraints {
  return {
    audio: {
      sampleRate: AUDIO_CONFIG.microphone.sampleRate,
      channelCount: AUDIO_CONFIG.microphone.channelCount,
      echoCancellation: AUDIO_CONFIG.microphone.echoCancellation,
      noiseSuppression: AUDIO_CONFIG.microphone.noiseSuppression,
      autoGainControl: AUDIO_CONFIG.microphone.autoGainControl
    },
    video: false
  };
}
