import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonGrid,
  IonRow,
  IonCol,
  IonIcon,
  IonButton,
  IonButtons,
  IonInput,
  IonCard,
  IonCardContent,
  IonChip,
  IonLabel,
  IonText,
  IonNote,
  IonSpinner,
  IonItem,
  IonBadge,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  wifi,
  cloudOffline,
  refresh,
  mic,
  micOutline,
  send,
  chatbubblesOutline,
  volumeHigh,
  playOutline,
  play,
  flash,
  micOff,
  stop,
  stopCircle,
} from 'ionicons/icons';
import { AppHeaderComponent } from '../shared/components/app-header/app-header.component';

interface RealtimeCredentials {
  azure_openai_endpoint: string;
  azure_openai_api_key: string;
  azure_openai_deployment_name: string;
  server_os?: string;
  message: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  type: 'text' | 'audio';
  content: string;
  timestamp: string;
  audioBlob?: Blob; // Para reproducir el audio
  transcription?: string; // Transcripción del audio
  tokens?: number; // Tokens utilizados
  isTranscribing?: boolean; // Si está transcribiendo actualmente
}

/**
 * Configuración centralizada para Azure OpenAI Realtime API
 * Facilita el mantenimiento y modificación de parámetros en el futuro
 */
interface RealtimeConfig {
  // Configuración de API
  apiVersion: string;

  // Configuración de sesión
  modalities: ('text' | 'audio')[];
  instructions: string;
  voiceType: 'alloy' | 'echo' | 'shimmer';
  inputAudioFormat: 'pcm16' | 'g711_ulaw' | 'g711_alaw';
  outputAudioFormat: 'pcm16' | 'g711_ulaw' | 'g711_alaw';
  inputAudioTranscription: {
    model: string;
  };
  turnDetection: {
    type: 'server_vad';
    threshold: number;
    prefix_padding_ms: number;
    silence_duration_ms: number;
  };

  // Configuración de temperatura
  temperature: number;
  max_response_output_tokens: number;

  // Configuración de WebSocket y ping-pong
  pingIntervalMs: number;
  pongTimeoutMs: number;
  maxReconnectAttempts: number;

  // Configuración de audio local
  audioSampleRate: number;
  audioChannels: number;
}

@Component({
  selector: 'app-demo-realtime',
  templateUrl: './demo-realtime.page.html',
  styleUrls: ['./demo-realtime.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonGrid,
    IonRow,
    IonCol,
    IonIcon,
    IonButton,
    IonButtons,
    IonInput,
    IonCard,
    IonCardContent,
    IonChip,
    IonLabel,
    IonText,
    IonNote,
    IonSpinner,
    IonItem,
    IonBadge,
    AppHeaderComponent,
  ],
})
export class DemoRealtimePage implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('chatContainer') chatContainer!: ElementRef;

  // ==================== CONFIGURACIÓN CENTRALIZADA ====================

  /**
   * Configuración centralizada de Azure OpenAI Realtime API
   * Modificar estos valores según necesidades del proyecto
   */
  private readonly realtimeConfig: RealtimeConfig = {
    // API Version - Usar versión preview disponible para Realtime API
    // Nota: La API de Realtime aún está en preview, no hay versión GA
    apiVersion: '2024-10-01-preview',

    // Modalidades soportadas
    modalities: ['text', 'audio'],

    // Instrucciones del sistema para el asistente
    instructions: 'Eres un asistente útil y amigable. Responde de forma concisa y clara.',

    // Tipo de voz para respuestas de audio
    voiceType: 'alloy', // Opciones: 'alloy', 'echo', 'shimmer'

    // Formato de audio de entrada (micrófono del usuario)
    inputAudioFormat: 'pcm16',

    // Formato de audio de salida (respuestas del asistente)
    outputAudioFormat: 'pcm16',

    // Transcripción automática del audio de entrada
    inputAudioTranscription: {
      model: 'whisper-1'
    },

    // Detección de actividad de voz (VAD) en el servidor
    turnDetection: {
      type: 'server_vad',
      threshold: 0.5,           // Sensibilidad de detección (0.0 - 1.0)
      prefix_padding_ms: 300,   // Audio antes de que se detecte habla
      silence_duration_ms: 500  // Silencio para considerar fin de turno
    },

    // Temperatura para generación de respuestas (0.0 - 2.0)
    temperature: 0.8,

    // Máximo de tokens en respuestas
    max_response_output_tokens: 4096,

    // Configuración de ping-pong para mantener conexión activa
    pingIntervalMs: 25000,      // Ping cada 25 segundos
    pongTimeoutMs: 10000,       // Esperar pong máximo 10 segundos
    maxReconnectAttempts: 5,    // Máximo 5 intentos de reconexión

    // Configuración de audio local (Web Audio API)
    audioSampleRate: 24000,     // Hz - debe coincidir con el formato PCM16
    audioChannels: 1            // Mono
  };

  // Estado de conexión
  isConnected = false;
  isConnecting = false;
  connectionStatusText = 'Desconectado';

  // WebSocket
  private ws: WebSocket | null = null;
  private wsUrl = '';

  // Mensajes
  messages: ChatMessage[] = [];
  messageText = '';
  isAssistantThinking = false;

  // Audio y grabación
  isRecording = false;
  isMuted = false;
  isListeningMode = false; // Modo de escucha continua activado
  recordingDuration = 0;
  private recordingInterval: any = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private audioContext: AudioContext | null = null;
  private audioStream: MediaStream | null = null;
  private audioWorkletNode: AudioWorkletNode | null = null;
  private hasAudioBeenSent = false; // Flag para rastrear si se envió audio

  // VAD (Voice Activity Detection)
  vadActive = false;
  private vadAnalyser: AnalyserNode | null = null;
  private vadCheckInterval: any = null;
  private vadThreshold = -50; // dB threshold para detectar voz

  // Control de reproducción y flujo
  isAssistantSpeaking = false;
  isPlayingAudio = false;
  currentPlayingMessageId: string | null = null; // ID del mensaje que se está reproduciendo
  private playbackQueue: Blob[] = [];
  private currentAudioSource: AudioBufferSourceNode | null = null;

  // Mapa de audio buffers y datos por mensaje
  private audioBuffersByMessage: Map<string, string[]> = new Map();
  private currentResponseId: string | null = null;
  private currentAssistantMessageId: string | null = null;
  private currentUserMessageId: string | null = null;

  // Sistema de Ping-Pong para mantener conexión activa
  private pingInterval: any = null;
  private pongTimeout: any = null;
  private reconnectAttempts = 0;
  private isReconnecting = false;
  connectionLatency: number | null = null; // Latencia en ms
  private lastPingTime: number = 0;

  constructor(
    private http: HttpClient,
    private cdr: ChangeDetectorRef
  ) {
    addIcons({
      mic,
      playOutline,
      flash,
      chatbubblesOutline,
      send,
      volumeHigh,
      wifi,
      cloudOffline,
      refresh,
      micOutline,
      play,
      micOff,
      stop,
      stopCircle,
    });
  }

  async ngOnInit() {
    await this.connectToRealtime();
  }

  ngAfterViewInit() {
    // Scroll automático al final cuando se agregan mensajes
    setTimeout(() => this.scrollToBottom(), 0);
  }

  ngOnDestroy() {
    this.stopPingPong();
    this.disconnect();
    this.stopListening();
    if (this.audioStream) {
      this.audioStream.getTracks().forEach(track => track.stop());
    }
  }

  private async connectToRealtime(): Promise<void> {
    try {
      this.isConnecting = true;
      this.connectionStatusText = 'Conectando...';

      // Obtener credenciales del backend
      const credentials = await firstValueFrom(
        this.http.get<RealtimeCredentials>('/api/credentials/realtime')
      );

      // Credenciales obtenidas correctamente

      // Construir URL de WebSocket para Azure OpenAI Realtime API
      // Formato: wss://<endpoint>/openai/realtime?api-version=<version>&deployment=<deployment>&api-key=<key>
      const endpointUrl = new URL(credentials.azure_openai_endpoint);
      const wsProtocol = 'wss:';
      const wsHost = endpointUrl.hostname;

      this.wsUrl = `${wsProtocol}//${wsHost}/openai/realtime?api-version=${this.realtimeConfig.apiVersion}&deployment=${credentials.azure_openai_deployment_name}&api-key=${credentials.azure_openai_api_key}`;

      console.log(`🔌 Conectando con API version: ${this.realtimeConfig.apiVersion}`);

      // Crear conexión WebSocket
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        console.log('✅ Conectado a Azure OpenAI Realtime API');
        this.isConnected = true;
        this.isConnecting = false;
        this.reconnectAttempts = 0; // Resetear intentos de reconexión
        this.isReconnecting = false;
        this.connectionStatusText = 'Conectado';

        // Enviar configuración inicial de sesión
        this.sendSessionConfig();

        // Iniciar sistema de ping-pong
        this.startPingPong();
      };

      this.ws.onmessage = (event) => {
        this.handleRealtimeMessage(event.data);
      };

      this.ws.onerror = (error) => {
        console.error('❌ Error WebSocket:', error);
        this.connectionStatusText = 'Error de conexión';
        this.isConnecting = false;
        this.isConnected = false;
      };

      this.ws.onclose = (event) => {
        console.log('🔌 Desconectado de Azure OpenAI Realtime API', event);
        this.stopPingPong();
        this.isConnected = false;
        this.isConnecting = false;
        this.connectionStatusText = 'Desconectado';
        this.connectionLatency = null;

        // Intentar reconexión automática si no fue cierre intencional
        if (!event.wasClean && !this.isReconnecting && this.reconnectAttempts < this.realtimeConfig.maxReconnectAttempts) {
          this.attemptReconnection();
        }
      };

    } catch (error) {
      console.error('❌ Error conectando:', error);
      this.connectionStatusText = 'Error al conectar';
      this.isConnecting = false;
      this.isConnected = false;
    }
  }

  private sendSessionConfig(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;

    // Configurar la sesión del Realtime API usando la configuración centralizada
    const config = {
      type: 'session.update',
      session: {
        modalities: this.realtimeConfig.modalities,
        instructions: this.realtimeConfig.instructions,
        voice: this.realtimeConfig.voiceType,
        input_audio_format: this.realtimeConfig.inputAudioFormat,
        output_audio_format: this.realtimeConfig.outputAudioFormat,
        input_audio_transcription: this.realtimeConfig.inputAudioTranscription,
        turn_detection: this.realtimeConfig.turnDetection,
        temperature: this.realtimeConfig.temperature,
        max_response_output_tokens: this.realtimeConfig.max_response_output_tokens
      }
    };

    this.ws.send(JSON.stringify(config));
    console.log('⚙️ Configuración de sesión enviada:', config);
  }

  private handleRealtimeMessage(data: string): void {
    try {
      const message = JSON.parse(data);

      switch (message.type) {
        case 'session.created':
          // Sesión creada
          break;

        case 'session.updated':
          // Sesión actualizada
          break;

        case 'response.created':
          // Nueva respuesta iniciada - capturar el response_id
          this.currentResponseId = message.response?.id;
          // Response creado
          break;

        case 'response.output_item.added':
          // Nuevo item de salida - crear mensaje de audio del asistente
          if (message.item?.role === 'assistant') {
            this.createAssistantAudioMessage(message.item.id);
          }
          break;

        case 'conversation.item.created':
          // Nuevo item en la conversación
          if (message.item?.role === 'assistant') {
            this.isAssistantThinking = true;
          } else if (message.item?.role === 'user') {
            // Crear mensaje del usuario cuando el servidor lo confirma
            const userMessageId = message.item.id;
            this.createUserAudioMessage(userMessageId);
          }
          break;

        case 'conversation.item.input_audio_transcription.completed':
          // Transcripción del audio del usuario completada
          if (message.item_id && message.transcript) {
            this.updateUserTranscription(message.item_id, message.transcript);
          }
          break;

        case 'response.audio_transcript.delta':
          // Transcripción parcial del audio de respuesta
          // Transcripción en progreso
          this.updateAssistantTranscription(message.delta);
          break;

        case 'response.audio_transcript.done':
          // Transcripción completa del audio
          // Transcripción completada
          this.finalizeAssistantTranscription();
          break;

        case 'response.text.delta':
          // Texto parcial de respuesta
          this.appendAssistantMessage(message.delta);
          break;

        case 'response.text.done':
          // Respuesta de texto completa
          this.addAssistantMessage(message.text);
          this.isAssistantThinking = false;
          break;

        case 'response.audio.delta':
          // Audio parcial de respuesta - almacenar para reproducción
          this.storeAudioDelta(message.delta);
          break;

        case 'response.audio.done':
          // Audio completo
          this.finalizeAudioMessage();
          this.isAssistantThinking = false;
          break;

        case 'response.done':
          // Respuesta completa - capturar tokens
          console.log('📦 response.done completo:', message);
          if (message.response?.usage) {
            this.updateMessageTokens(message.response.usage);
          }
          this.currentResponseId = null;
          // NO resetear currentAssistantMessageId aquí para poder actualizar tokens después
          setTimeout(() => {
            this.currentAssistantMessageId = null;
          }, 100);
          break;

        case 'input_audio_buffer.speech_started':
          // Inicio de habla detectado (VAD)
          this.vadActive = true;
          break;

        case 'input_audio_buffer.speech_stopped':
          // Fin de habla detectado (VAD)
          this.vadActive = false;
          break;

        case 'pong':
          // Respuesta pong recibida
          this.handlePong();
          break;

        case 'error':
          console.error('❌ Error del servidor:', message.error);
          this.isAssistantThinking = false;
          break;
      }
    } catch (error) {
      console.error('❌ Error procesando mensaje:', error);
    }
  }

  async sendTextMessage(): Promise<void> {
    if (!this.messageText.trim() || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return;
    }

    const text = this.messageText.trim();

    // Agregar mensaje del usuario a la UI
    this.addUserMessage(text, 'text');

    // Enviar al Realtime API
    const event = {
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [
          {
            type: 'input_text',
            text: text
          }
        ]
      }
    };

    this.ws.send(JSON.stringify(event));

    // Solicitar respuesta
    this.ws.send(JSON.stringify({ type: 'response.create' }));

    this.messageText = '';
    this.isAssistantThinking = true;
  }

  async startListening(): Promise<void> {
    if (!this.isConnected || this.isListeningMode || this.isAssistantSpeaking) return;

    try {
      // Solicitar acceso al micrófono
      this.audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: this.realtimeConfig.audioSampleRate,
          channelCount: this.realtimeConfig.audioChannels
        }
      });

      // Crear AudioContext para procesar audio
      this.audioContext = new AudioContext({ sampleRate: this.realtimeConfig.audioSampleRate });
      const source = this.audioContext.createMediaStreamSource(this.audioStream);

      // Crear procesador de audio para streaming en tiempo real
      await this.audioContext.audioWorklet.addModule(
        URL.createObjectURL(new Blob([this.getAudioWorkletProcessorCode()], { type: 'application/javascript' }))
      );

      this.audioWorkletNode = new AudioWorkletNode(this.audioContext, 'audio-processor');

      // Recibir chunks de audio y enviarlos al servidor
      this.audioWorkletNode.port.onmessage = (event) => {
        if (!this.isMuted && !this.isAssistantSpeaking && this.ws && this.ws.readyState === WebSocket.OPEN) {
          // Convertir Float32Array a PCM16 y enviar
          const pcm16 = this.floatToPCM16(event.data);
          const base64Audio = this.arrayBufferToBase64(pcm16.buffer);

          this.ws.send(JSON.stringify({
            type: 'input_audio_buffer.append',
            audio: base64Audio
          }));

          // Marcar que se ha enviado audio
          if (!this.hasAudioBeenSent) {
            this.hasAudioBeenSent = true;
          }
        }
      };

      source.connect(this.audioWorkletNode);
      this.audioWorkletNode.connect(this.audioContext.destination);

      this.isListeningMode = true;
      this.isMuted = false;
      this.recordingDuration = 0;
      this.hasAudioBeenSent = false; // Resetear el flag al iniciar

      // Contador de duración
      this.recordingInterval = setInterval(() => {
        this.recordingDuration++;
      }, 1000);

      // Modo de escucha continua activado

    } catch (error) {
      console.error('❌ Error accediendo al micrófono:', error);
      alert('No se pudo acceder al micrófono. Verifica los permisos.');
    }
  }

  toggleMute(): void {
    this.isMuted = !this.isMuted;
  }

  stopListening(): void {
    if (!this.isListeningMode) return;

    // Detener primero el streaming de audio antes de cualquier otra cosa
    this.isMuted = true; // Silenciar inmediatamente para prevenir envío de audio

    // Desconectar AudioWorklet primero para detener el procesamiento
    if (this.audioWorkletNode) {
      this.audioWorkletNode.disconnect();
      this.audioWorkletNode = null;
    }

    // Detener el stream del micrófono
    if (this.audioStream) {
      this.audioStream.getTracks().forEach(track => track.stop());
      this.audioStream = null;
    }

    // Cerrar el AudioContext
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    // Detener el contador
    if (this.recordingInterval) {
      clearInterval(this.recordingInterval);
    }

    // Resetear estados
    this.isListeningMode = false;
    this.isMuted = false;
    this.recordingDuration = 0;

    // NO detener la reproducción de audio del asistente
    // El stop es solo para detener la escucha del micrófono, no la reproducción

    // Verificar estado del buffer antes de commit
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      // Solo hacer commit si realmente se envió audio Y el VAD detectó habla
      if (this.hasAudioBeenSent && this.vadActive) {
        // Si se envió audio y el VAD está activo, hacer commit y solicitar respuesta
        this.ws.send(JSON.stringify({ type: 'input_audio_buffer.commit' }));
        this.ws.send(JSON.stringify({ type: 'response.create' }));
      } else {
        // Si NO se cumple alguna condición, solo limpiar el buffer sin commit
        this.ws.send(JSON.stringify({ type: 'input_audio_buffer.clear' }));
      }
      this.hasAudioBeenSent = false;
    }
  }

  private getAudioWorkletProcessorCode(): string {
    return `
      class AudioProcessor extends AudioWorkletProcessor {
        constructor() {
          super();
          this.bufferSize = 4800; // 200ms a 24kHz
          this.buffer = new Float32Array(this.bufferSize);
          this.bufferIndex = 0;
        }

        process(inputs, outputs, parameters) {
          const input = inputs[0];
          if (input.length > 0) {
            const channelData = input[0];

            for (let i = 0; i < channelData.length; i++) {
              this.buffer[this.bufferIndex++] = channelData[i];

              if (this.bufferIndex >= this.bufferSize) {
                this.port.postMessage(this.buffer.slice(0));
                this.bufferIndex = 0;
              }
            }
          }

          return true;
        }
      }

      registerProcessor('audio-processor', AudioProcessor);
    `;
  }

  private floatToPCM16(float32Array: Float32Array): Int16Array {
    const pcm16 = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return pcm16;
  }

  private arrayBufferToBase64(buffer: ArrayBufferLike): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  private addUserMessage(content: string, type: 'text' | 'audio'): void {
    const message: ChatMessage = {
      id: Date.now().toString() + Math.random(),
      role: 'user',
      type,
      content,
      timestamp: new Date().toISOString()
    };

    this.messages.push(message);
    setTimeout(() => this.scrollToBottom(), 100);
  }

  private createUserAudioMessage(itemId: string): void {
    // Buscar si ya existe un mensaje temporal del usuario
    const tempMessage = this.messages.find(m => m.role === 'user' && !m.id.startsWith('item_'));

    if (tempMessage) {
      // Actualizar el ID temporal con el ID real del servidor
      tempMessage.id = itemId;
      tempMessage.isTranscribing = true;
      this.currentUserMessageId = itemId;
    } else {
      // Crear nuevo mensaje si no existe
      const message: ChatMessage = {
        id: itemId,
        role: 'user',
        type: 'audio',
        content: '🎤 Mensaje de voz',
        timestamp: new Date().toISOString(),
        isTranscribing: true,
        transcription: ''
      };
      this.messages.push(message);
      this.currentUserMessageId = itemId;
      setTimeout(() => this.scrollToBottom(), 100);
    }
  }

  private updateUserTranscription(itemId: string, transcript: string): void {
    const message = this.messages.find(m => m.id === itemId);
    if (message) {
      message.transcription = transcript;
      message.content = transcript;
      message.isTranscribing = false;
      // Transcripción del usuario completada
    }
  }

  private addAssistantMessage(content: string): void {
    const message: ChatMessage = {
      id: Date.now().toString() + Math.random(),
      role: 'assistant',
      type: 'text',
      content,
      timestamp: new Date().toISOString()
    };

    this.messages.push(message);
    setTimeout(() => this.scrollToBottom(), 100);
  }

  private appendAssistantMessage(delta: string): void {
    const lastMessage = this.messages[this.messages.length - 1];

    if (lastMessage && lastMessage.role === 'assistant') {
      lastMessage.content += delta;
    } else {
      this.addAssistantMessage(delta);
    }

    setTimeout(() => this.scrollToBottom(), 100);
  }

  private createAssistantAudioMessage(itemId: string): void {
    // Crear mensaje de audio del asistente inmediatamente
    const message: ChatMessage = {
      id: itemId,
      role: 'assistant',
      type: 'audio',
      content: '🎵 Audio recibido',
      timestamp: new Date().toISOString(),
      isTranscribing: true,
      transcription: ''
    };

    this.messages.push(message);
    this.currentAssistantMessageId = itemId;
    this.audioBuffersByMessage.set(itemId, []);
    setTimeout(() => this.scrollToBottom(), 100);
  }

  private updateAssistantTranscription(delta: string): void {
    if (!this.currentAssistantMessageId) return;

    const message = this.messages.find(m => m.id === this.currentAssistantMessageId);
    if (message) {
      if (!message.transcription) {
        message.transcription = '';
      }
      message.transcription += delta;
    }
  }

  private finalizeAssistantTranscription(): void {
    if (!this.currentAssistantMessageId) return;

    const message = this.messages.find(m => m.id === this.currentAssistantMessageId);
    if (message) {
      message.isTranscribing = false;
      // Reemplazar el contenido con la transcripción completa
      if (message.transcription) {
        message.content = message.transcription;
      }
    }
  }

  private storeAudioDelta(audioBase64: string): void {
    if (!this.currentAssistantMessageId) return;

    // Marcar que el asistente está hablando (pausar escucha)
    this.isAssistantSpeaking = true;

    const buffers = this.audioBuffersByMessage.get(this.currentAssistantMessageId);
    if (buffers) {
      buffers.push(audioBase64);
    }
  }

  private finalizeAudioMessage(): void {
    if (!this.currentAssistantMessageId) return;

    const message = this.messages.find(m => m.id === this.currentAssistantMessageId);
    const buffers = this.audioBuffersByMessage.get(this.currentAssistantMessageId);

    if (message && buffers && buffers.length > 0) {
      // Convertir todos los buffers base64 a un Blob
      const audioBlob = this.base64ArrayToBlob(buffers);
      message.audioBlob = audioBlob;
      // Audio finalizado, reproducir automáticamente

      // Reproducir automáticamente el audio del asistente
      setTimeout(() => {
        this.playAudio(message);
      }, 100);
    } else {
      // Si no hay audio, reactivar escucha inmediatamente
      setTimeout(() => {
        this.isAssistantSpeaking = false;
      }, 500);
    }
  }

  private updateMessageTokens(usage: any): void {
    if (!usage) return;

    const inputTokens = usage.input_tokens || 0;
    const outputTokens = usage.output_tokens || 0;
    const totalTokens = usage.total_tokens || (inputTokens + outputTokens);

    // Actualizar tokens del mensaje del USUARIO (input_tokens)
    if (this.currentUserMessageId && inputTokens > 0) {
      const userMessageIndex = this.messages.findIndex(m => m.id === this.currentUserMessageId);
      if (userMessageIndex !== -1) {
        this.messages[userMessageIndex].tokens = inputTokens;
      }
    }

    // Actualizar tokens del mensaje del ASISTENTE (output_tokens)
    if (this.currentAssistantMessageId && outputTokens > 0) {
      const assistantMessageIndex = this.messages.findIndex(m => m.id === this.currentAssistantMessageId);
      if (assistantMessageIndex !== -1) {
        this.messages[assistantMessageIndex].tokens = outputTokens;
      }
    }

    // Crear una nueva referencia del array para que Angular detecte el cambio
    this.messages = [...this.messages];

    // Forzar múltiples ciclos de detección de cambios
    this.cdr.markForCheck();
    this.cdr.detectChanges();

    // Forzar otro ciclo en el siguiente tick
    setTimeout(() => {
      this.cdr.markForCheck();
      this.cdr.detectChanges();
    }, 0);

    setTimeout(() => {
      this.cdr.markForCheck();
      this.cdr.detectChanges();
    }, 100);
  }

  private base64ArrayToBlob(base64Array: string[]): Blob {
    // Convertir array de base64 a Blob de audio
    const binaryStrings = base64Array.map(b64 => atob(b64));
    const lengths = binaryStrings.map(s => s.length);
    const totalLength = lengths.reduce((a, b) => a + b, 0);

    const uint8Array = new Uint8Array(totalLength);
    let offset = 0;

    for (const binaryString of binaryStrings) {
      for (let i = 0; i < binaryString.length; i++) {
        uint8Array[offset++] = binaryString.charCodeAt(i);
      }
    }

    // PCM16 audio blob
    return new Blob([uint8Array], { type: 'audio/pcm' });
  }

  playAudio(message: ChatMessage): void {
    if (!message.audioBlob || this.isPlayingAudio) return;

    // Marcar que estamos reproduciendo este mensaje específico
    this.isPlayingAudio = true;
    this.isAssistantSpeaking = true;
    this.currentPlayingMessageId = message.id;

    // Crear AudioContext para reproducir PCM16
    const audioContext = new AudioContext({ sampleRate: this.realtimeConfig.audioSampleRate });
    const reader = new FileReader();

    reader.onload = async (e) => {
      try {
        const arrayBuffer = e.target?.result as ArrayBuffer;

        // Convertir PCM16 a AudioBuffer
        const audioBuffer = this.pcm16ToAudioBuffer(arrayBuffer, audioContext);

        // Reproducir
        this.currentAudioSource = audioContext.createBufferSource();
        this.currentAudioSource.buffer = audioBuffer;
        this.currentAudioSource.connect(audioContext.destination);

        // Cuando termine la reproducción
        this.currentAudioSource.onended = () => {
          this.currentAudioSource = null;

          // Esperar 500ms antes de reactivar la escucha para evitar bucles
          setTimeout(() => {
            this.isPlayingAudio = false;
            this.isAssistantSpeaking = false;
            this.currentPlayingMessageId = null;
            this.vadActive = false; // Resetear VAD
            // Resetear el flag de audio para evitar commits vacíos
            this.hasAudioBeenSent = false;
          }, 500);
        };

        this.currentAudioSource.start(0);
      } catch (error) {
        console.error('❌ Error reproduciendo audio:', error);
        this.isPlayingAudio = false;
        this.isAssistantSpeaking = false;
        this.currentPlayingMessageId = null;
        this.currentAudioSource = null;
      }
    };

    reader.readAsArrayBuffer(message.audioBlob);
  }

  stopAudio(): void {
    if (this.currentAudioSource) {
      try {
        this.currentAudioSource.stop();
        this.currentAudioSource = null;
      } catch (error) {
        console.error('❌ Error deteniendo audio:', error);
      }
    }

    // Esperar 500ms antes de reactivar para evitar bucle
    setTimeout(() => {
      this.isPlayingAudio = false;
      this.isAssistantSpeaking = false;
      this.currentPlayingMessageId = null;
      this.vadActive = false; // Resetear VAD también aquí
      // Resetear el flag de audio para evitar commits vacíos
      this.hasAudioBeenSent = false;
    }, 500);
  }

  private pcm16ToAudioBuffer(arrayBuffer: ArrayBuffer, audioContext: AudioContext): AudioBuffer {
    // Convertir PCM16 a AudioBuffer
    const int16Array = new Int16Array(arrayBuffer);
    const float32Array = new Float32Array(int16Array.length);

    // Normalizar de int16 a float32 [-1, 1]
    for (let i = 0; i < int16Array.length; i++) {
      float32Array[i] = int16Array[i] / 32768.0;
    }

    // Crear AudioBuffer
    const audioBuffer = audioContext.createBuffer(1, float32Array.length, 24000);
    audioBuffer.getChannelData(0).set(float32Array);

    return audioBuffer;
  }

  private playAudioDelta(audioBase64: string): void {
    // Este método ya no se usa, la lógica está en storeAudioDelta
    console.log('🔊 Audio delta recibido');
  }

  private scrollToBottom(): void {
    if (this.chatContainer?.nativeElement) {
      const element = this.chatContainer.nativeElement;
      element.scrollTop = element.scrollHeight;
    }
  }

  private disconnect(): void {
    this.stopPingPong();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connectionLatency = null;
  }

  // ==================== SISTEMA DE PING-PONG ====================

  private startPingPong(): void {
    // Detener cualquier ping-pong anterior
    this.stopPingPong();

    // Enviar ping periódicamente
    this.pingInterval = setInterval(() => {
      this.sendPing();
    }, this.realtimeConfig.pingIntervalMs);

    console.log('🏓 Sistema de ping-pong iniciado');
  }

  private stopPingPong(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }

    if (this.pongTimeout) {
      clearTimeout(this.pongTimeout);
      this.pongTimeout = null;
    }

    console.log('🏓 Sistema de ping-pong detenido');
  }

  private sendPing(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ No se puede enviar ping: WebSocket no está abierto');
      return;
    }

    // No enviar ping durante actividad activa (streaming de audio o reproducción)
    if (this.isListeningMode || this.isPlayingAudio) {
      console.log('🏓 Ping omitido: actividad en curso');
      return;
    }

    try {
      this.lastPingTime = Date.now();
      this.ws.send(JSON.stringify({ type: 'ping' }));
      console.log('🏓 Ping enviado');

      // Configurar timeout para esperar pong
      this.pongTimeout = setTimeout(() => {
        console.error('❌ No se recibió pong - conexión perdida');
        this.handlePongTimeout();
      }, this.realtimeConfig.pongTimeoutMs);

    } catch (error) {
      console.error('❌ Error enviando ping:', error);
      this.handlePongTimeout();
    }
  }

  private handlePong(): void {
    // Calcular latencia
    if (this.lastPingTime > 0) {
      this.connectionLatency = Date.now() - this.lastPingTime;
      console.log(`🏓 Pong recibido - Latencia: ${this.connectionLatency}ms`);
    }

    // Cancelar timeout de pong
    if (this.pongTimeout) {
      clearTimeout(this.pongTimeout);
      this.pongTimeout = null;
    }

    // Actualizar UI con latencia
    this.cdr.detectChanges();
  }

  private handlePongTimeout(): void {
    console.error('❌ Timeout esperando pong - conexión inactiva');

    // Limpiar timeout
    if (this.pongTimeout) {
      clearTimeout(this.pongTimeout);
      this.pongTimeout = null;
    }

    // Desconectar y reconectar
    this.disconnect();
    this.attemptReconnection();
  }

  private async attemptReconnection(): Promise<void> {
    if (this.isReconnecting || this.reconnectAttempts >= this.realtimeConfig.maxReconnectAttempts) {
      console.error('❌ Máximo de intentos de reconexión alcanzado');
      this.connectionStatusText = 'Reconexión fallida';
      return;
    }

    this.isReconnecting = true;
    this.reconnectAttempts++;

    // Backoff exponencial: 2^attempts segundos
    const delayMs = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

    this.connectionStatusText = `Reconectando (${this.reconnectAttempts}/${this.realtimeConfig.maxReconnectAttempts})...`;
    console.log(`🔄 Intento de reconexión ${this.reconnectAttempts}/${this.realtimeConfig.maxReconnectAttempts} en ${delayMs}ms`);

    await new Promise(resolve => setTimeout(resolve, delayMs));

    try {
      await this.connectToRealtime();
    } catch (error) {
      console.error('❌ Error en reconexión:', error);
      this.isReconnecting = false;

      // Intentar de nuevo si no se alcanzó el máximo
      if (this.reconnectAttempts < this.realtimeConfig.maxReconnectAttempts) {
        this.attemptReconnection();
      }
    }
  }

  formatTime(isoString: string): string {
    return new Date(isoString).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}
