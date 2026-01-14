import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HeaderComponent } from '../../components/header';
import { FooterComponent } from '../../components/footer';
import { 
  IonContent,
  IonToolbar,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  IonInput,
  IonButton,
  IonIcon,
  IonBadge,
  IonProgressBar,
  IonText,
  IonModal,
  IonHeader,
  IonTitle} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { 
  micOutline, 
  micOffOutline,
  playOutline,
  stopOutline,
  pauseOutline,
  checkmarkCircleOutline,
  closeCircleOutline,
  wifiOutline, 
  personOutline, 
  chatbubbleOutline,
  analyticsOutline, closeOutline, trashOutline, callOutline } from 'ionicons/icons';
import { Subject, takeUntil } from 'rxjs';
import { ResponsiveComponent } from '../../shared';

import { 
  AuthService,
  AudioRecorderService,
  ShoppingWebSocketService,
  ConversationManagerService,
  AudioPlayerService,
  AudioProcessorService,
  LoggerService,
  type ConversationMessage
} from '../../service';
import { 
  WebSocketState, 
  ConversationState,
  WSResponse,
  WSShoppingResponse
} from '../../shared/models';

@Component({
  selector: 'voice-shopping',
  templateUrl: './voice-shopping.html',
  styleUrls: ['./voice-shopping.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HeaderComponent,
    FooterComponent,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonItem,
    IonLabel,
    IonInput,
    IonButton,
    IonIcon,
    IonBadge,
    IonProgressBar,
    IonText,
    IonModal,
    IonHeader,
    IonToolbar,
    IonTitle
]
})
export class VoiceShoppingPage extends ResponsiveComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('messagesContainer', { read: ElementRef }) private messagesContainer?: ElementRef;
  
  private destroy$ = new Subject<void>();
  private shouldScrollToBottom = false;
  
  // Estado de la UI
  phone = '';
  isInitialized = false;
  
  // Estados observables
  wsState: WebSocketState = WebSocketState.DISCONNECTED;
  conversationState: ConversationState = ConversationState.IDLE;
  audioLevel = 0;
  
  // Mensajes de la conversación (delegados al servicio)
  get messages(): ConversationMessage[] {
    return this.conversationManager.messages;
  }
  
  // Modal de detalles de ejecución
  showExecutionDetailsModal = false;
  selectedExecutionDetails: any[] = [];
  
  // Control de interrupción
  private pendingAudioBlob: Blob | null = null;
  private _isMuted = false;

  private readonly logger = inject(LoggerService).getLogger('VoiceShoppingPage');

  constructor(
    private authService: AuthService,
    private audioRecorder: AudioRecorderService,
    private websocket: ShoppingWebSocketService,
    private conversationManager: ConversationManagerService,
    private audioPlayer: AudioPlayerService,
    private audioProcessor: AudioProcessorService
  ) {
    super();
    addIcons({playOutline,personOutline,chatbubbleOutline,analyticsOutline,wifiOutline,trashOutline,callOutline,closeOutline,closeCircleOutline,stopOutline,pauseOutline,micOutline,micOffOutline,checkmarkCircleOutline});
  }

  ngOnInit(): void {
    this.loadUserPhone();
    this.subscribeToWebSocket();
    this.subscribeToAudioRecorder();
  }

  override ngOnDestroy(): void {
    this.cleanup();
    this.destroy$.next();
    this.destroy$.complete();
    super.ngOnDestroy();
  }

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  /**
   * Carga el número de teléfono del usuario autenticado
   */
  private loadUserPhone(): void {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser && currentUser.phoneLogin) {
      this.phone = currentUser.phoneLogin;
    }
  }

  /**
   * Suscribe a los eventos del WebSocket
   */
  private subscribeToWebSocket(): void {
    this.websocket.webSocketState
      .pipe(takeUntil(this.destroy$))
      .subscribe(state => {
        this.wsState = state;
      });

    this.websocket.conversationState
      .pipe(takeUntil(this.destroy$))
      .subscribe(state => {
        this.conversationState = state;
      });

    this.websocket.messages
      .pipe(takeUntil(this.destroy$))
      .subscribe(message => this.handleWebSocketMessage(message));

    this.websocket.errors
      .pipe(takeUntil(this.destroy$))
      .subscribe(error => this.handleError(error));
  }

  /**
   * Suscribe a los eventos del grabador de audio
   */
  private subscribeToAudioRecorder(): void {
    // Monitoreo continuo del nivel de audio para detección de VAD
    this.audioRecorder.audioLevel
      .pipe(takeUntil(this.destroy$))
      .subscribe(level => {
        this.audioLevel = level;
        
        // VAD: Si el bot está hablando y detectamos voz consistente del usuario, interrumpir automáticamente
        if (this.conversationState === ConversationState.SPEAKING && 
            this.audioRecorder.hasVoiceDetected) {
          this.logger.debug(`VAD: Voz detectada (nivel ${level}) mientras bot habla - Interrumpiendo...`);
          this.interruptBot();
        }
      });

    this.audioRecorder.isRecording
      .pipe(takeUntil(this.destroy$))
      .subscribe(isRecording => {
        if (isRecording) {
          this.checkForSilence();
        }
      });
  }

  /**
   * Interrumpe al bot cuando está hablando
   * Detiene la reproducción del audio y activa el micrófono
   */
  private interruptBot(): void {
    this.logger.debug('VAD: Usuario interrumpiendo al bot');
    
    // Evitar múltiples interrupciones
    if (this.conversationState !== ConversationState.SPEAKING) {
      return;
    }
    
    // Detener audio del bot usando el servicio
    this.audioPlayer.stopAudio();
    
    // Marcar que el bot ya no está hablando
    this.conversationManager.setBotSpeaking(false);
    
    // Desactivar mute si estaba activado
    this._isMuted = false;
    
    // Cambiar a estado de escucha
    this.conversationManager.setConversationState(ConversationState.LISTENING);
    this.conversationState = ConversationState.LISTENING;
    
    // Asegurarse que el micrófono esté grabando
    if (!this.audioRecorder.isInitialized || this.audioRecorder.recordingState !== 'recording') {
      this.startListening();
    }
    
    this.conversationManager.addSystemMessage('⚡ Has interrumpido al asistente. Habla ahora...', false);
    this.shouldScrollToBottom = true;
  }

  /**
   * Inicia la conversación
   */
  async startConversation(): Promise<void> {
    if (!this.phone || this.phone.trim().length === 0) {
      alert('Por favor ingresa un número de teléfono');
      return;
    }

    try {
      // Inicializar micrófono si no está inicializado
      if (!this.audioRecorder.isInitialized) {
        await this.audioRecorder.initialize();
      }

      // Iniciar VAD continuo para detectar interrupciones del usuario
      this.audioRecorder.startContinuousVAD();

      // Conectar WebSocket con audio habilitado
      this.websocket.connect(this.phone, undefined, true); // returnAudio = true para recibir audio
      
      // Esperar a que se conecte
      await this.waitForConnection();
      
      this.isInitialized = true;
      this.addSystemMessage('Conversación iniciada. Puedes empezar a hablar.');
      
      // Comenzar a grabar automáticamente
      this.startListening();
      
    } catch (error: any) {
      this.logger.error('Error iniciando conversación:', error);
      alert(error.message || 'Error al iniciar la conversación');
    }
  }

  /**
   * Espera a que el WebSocket se conecte
   */
  private waitForConnection(): Promise<void> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Timeout esperando conexión'));
      }, 10000);

      const subscription = this.websocket.webSocketState.subscribe(state => {
        if (state === WebSocketState.CONNECTED) {
          clearTimeout(timeout);
          subscription.unsubscribe();
          resolve();
        } else if (state === WebSocketState.ERROR) {
          clearTimeout(timeout);
          subscription.unsubscribe();
          reject(new Error('Error en la conexión'));
        }
      });
    });
  }

  /**
   * Inicia la escucha del micrófono
   */
  startListening(): void {
    if (!this.isInitialized) return;
    
    this.audioRecorder.startRecording();
    this.websocket.setConversationState(ConversationState.LISTENING);
  }

  /**
   * Toggle del modo mute - solo activo cuando el bot está hablando
   * Sirve para evitar que se reactive el micrófono automáticamente al terminar el bot
   */
  toggleMute(): void {
    // Solo se puede usar cuando el bot está hablando
    if (!this.conversationManager.isBotSpeaking) return;
    
    this._isMuted = !this._isMuted;
    
    if (this._isMuted) {
      this.addSystemMessage('Micrófono silenciado - No se reactivará automáticamente');
    } else {
      this.addSystemMessage('Micrófono se reactivará cuando el bot termine de hablar');
    }
  }

  /**
   * Detiene el micrófono y limpia el audio sin enviar nada al WebSocket
   * Disponible siempre durante la conversación
   */
  stopAndDiscard(): void {
    // Detener y limpiar grabación
    this.audioRecorder.discardRecording();
    this.pendingAudioBlob = null;
    
    // Volver a estado idle sin enviar nada
    this.websocket.setConversationState(ConversationState.IDLE);
    this.addSystemMessage('Audio descartado');
    
    // Si no está en mute, reiniciar escucha
    if (!this._isMuted && !this.conversationManager.isBotSpeaking) {
      setTimeout(() => this.startListening(), 100);
    }
  }

  /**
   * Finaliza la conversación completamente
   * - Detiene reproducción del bot si está hablando
   * - Libera audio pendiente de envío
   * - Desconecta WebSocket
   * - Regresa al estado inicial
   */
  stopConversation(): void {
    this.logger.info('Finalizando conversación');
    
    // Detener audio del bot usando el servicio
    this.audioPlayer.stopAudio();
    
    // Limpiar audio pendiente
    this.pendingAudioBlob = null;
    
    // Limpiar recursos
    this.cleanup();
    
    // Resetear estado
    this.isInitialized = false;
    this._isMuted = false;
    this.conversationState = ConversationState.IDLE;
    
    // Resetear el servicio de conversación
    this.conversationManager.reset();
    
    this.conversationManager.addSystemMessage('Conversación finalizada');
    this.shouldScrollToBottom = true;
  }

  /**
   * Verifica si hay silencio y envía el audio
   */
  private async checkForSilence(): Promise<void> {
    if (!this.audioRecorder.isInitialized) return;

    // Verificar cada 500ms si hay silencio
    const intervalId = setInterval(async () => {
      if (this.audioRecorder.recordingState !== 'recording') {
        clearInterval(intervalId);
        return;
      }

      if (this.audioRecorder.isSilent()) {
        clearInterval(intervalId);
        await this.processRecording();
      }
    }, 500);
  }

  /**
   * Procesa la grabación y la envía
   */
  private async processRecording(): Promise<void> {
    const audioBlob = await this.audioRecorder.stopRecording();
    
    if (!audioBlob || audioBlob.size === 0) {
      this.startListening(); // Reiniciar escucha
      return;
    }

    this.pendingAudioBlob = audioBlob;
    
    // Convertir audio a base64 usando el servicio
    const audioBase64 = await this.audioProcessor.convertBlobToBase64(audioBlob);
    
    if (audioBase64) {
      this.logger.debug(`Enviando audio (${audioBlob.size} bytes)`);
      // Enviar como mensaje de tipo 'audio'
      this.websocket.sendAudio(audioBase64, 'webm', 'es');
    } else {
      // Si no se pudo convertir, reiniciar escucha
      this.startListening();
    }
  }

  /**
   * Maneja mensajes del WebSocket
   */
  private handleWebSocketMessage(message: WSResponse): void {
    switch (message.type) {
      case 'conversation_started':
        this.logger.debug('Conversación iniciada:', message.conversation_id);
        break;

      case 'transcription':
        // Mostrar transcripción al usuario
        const transcription = (message as any).text;
        if (transcription && transcription.trim()) {
          this.conversationManager.addUserMessage(transcription);
          this.shouldScrollToBottom = true;
        }
        break;

      case 'shopping_response':
      case 'audio_response':
        this.handleShoppingResponse(message);
        break;

      case 'error':
        this.conversationManager.addSystemMessage(`Error: ${message.error}`, true);
        this.shouldScrollToBottom = true;
        break;
    }
  }

  /**
   * Maneja respuestas de shopping
   */
  private async handleShoppingResponse(response: WSShoppingResponse): Promise<void> {
    // Pasar execution_details si existen
    const executionDetails = response.shopping_response.execution_details;
    if (executionDetails && executionDetails.length > 0) {
      this.logger.debug('Detalles de ejecución:', executionDetails);
    }
    this.addBotMessage(response.shopping_response.response, executionDetails);
    
    // Simular que el bot está hablando
    this.conversationManager.setBotSpeaking(true);
    this.websocket.setConversationState(ConversationState.SPEAKING);
    this.conversationState = ConversationState.SPEAKING;
    
    // Reproducir audio si viene del backend
    // El audio puede venir en audio_response.audio_base64 o shopping_response.audio_base64
    const audioBase64 = response.audio_response?.audio_base64 || response.shopping_response.audio_base64;
    
    if (audioBase64) {
      this.logger.debug('Reproduciendo audio del backend...');
      await this.playAudio(audioBase64);
    } else {
      this.logger.warn('No se recibió audio del backend');
      this.logger.debug('Respuesta completa:', JSON.stringify(response, null, 2));
    }
    
    // Bot terminó de hablar, reiniciar escucha solo si no está en mute
    this.conversationManager.setBotSpeaking(false);
    if (!this._isMuted) {
      this.startListening();
    } else {
      this.logger.debug('Micrófono en mute - no se reactiva automáticamente');
      this.websocket.setConversationState(ConversationState.PAUSED);
      this.conversationState = ConversationState.PAUSED;
    }
  }

  /**
   * Reproduce audio desde base64 usando el servicio
   */
  private async playAudio(audioBase64: string): Promise<void> {
    await this.audioPlayer.playAudio(audioBase64);
  }

  /**
   * Maneja errores
   */
  private handleError(error: string): void {
    this.conversationManager.addSystemMessage(`Error: ${error}`, true);
    this.shouldScrollToBottom = true;
  }

  /**
   * Hace scroll al final del contenedor de mensajes
   */
  private scrollToBottom(): void {
    try {
      if (this.messagesContainer?.nativeElement) {
        const element = this.messagesContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    } catch (err) {
      this.logger.error('Error haciendo scroll:', err);
    }
  }

  /**
   * Agrega un mensaje del usuario
   */
  private addUserMessage(text: string): void {
    this.messages.push({
      type: 'user',
      text,
      timestamp: new Date()
    });
    this.shouldScrollToBottom = true;
  }

  /**
   * Agrega un mensaje del bot
   */
  private addBotMessage(text: string, executionDetails?: any[]): void {
    this.conversationManager.addBotMessage(text, executionDetails);
    this.shouldScrollToBottom = true;
  }

  /**
   * Agrega un mensaje del sistema
   */
  private addSystemMessage(text: string, isError = false): void {
    this.conversationManager.addSystemMessage(text, isError);
    this.shouldScrollToBottom = true;
  }

  /**
   * Abre el modal con los detalles de ejecución
   */
  openExecutionDetails(details: any[]): void {
    this.selectedExecutionDetails = details;
    this.showExecutionDetailsModal = true;
  }

  /**
   * Cierra el modal de detalles de ejecución
   */
  closeExecutionDetails(): void {
    this.showExecutionDetailsModal = false;
    this.selectedExecutionDetails = [];
  }

  /**
   * Formatea la duración en milisegundos (delegado al servicio)
   */
  formatDuration(ms: number): string {
    return this.conversationManager.formatDuration(ms);
  }

  /**
   * Verifica si un objeto tiene propiedades (delegado al servicio)
   */
  hasDetails(details: any): boolean {
    return this.conversationManager.hasDetails(details);
  }

  /**
   * Convierte objeto details a array de pares clave-valor (delegado al servicio)
   */
  getDetailsEntries(details: any): Array<{key: string, value: any}> {
    return this.conversationManager.getDetailsEntries(details);
  }

  /**
   * Formatea el valor para mostrar (delegado al servicio)
   */
  formatValue(value: any): string {
    return this.conversationManager.formatValue(value);
  }

  /**
   * Calcula el tiempo total de ejecución (delegado al servicio)
   */
  getTotalDuration(): number {
    if (!this.selectedExecutionDetails || this.selectedExecutionDetails.length === 0) {
      return 0;
    }
    return this.conversationManager.getTotalDuration(this.selectedExecutionDetails);
  }

  /**
   * Calcula el porcentaje de tiempo que tomó una operación respecto al total
   */
  getDurationPercentage(duration_ms: number): number {
    const total = this.getTotalDuration();
    if (total === 0) return 0;
    return this.conversationManager.getPercentage(duration_ms, total);
  }

  /**
   * Obtiene el color de la barra según el porcentaje
   */
  getProgressBarColor(percentage: number): string {
    if (percentage > 50) return 'danger';
    if (percentage > 25) return 'warning';
    return 'success';
  }

  /**
   * Limpia recursos
   */
  private cleanup(): void {
    this.audioRecorder.cleanup();
    this.audioPlayer.cleanup();
    this.websocket.disconnect();
    this.conversationManager.setBotSpeaking(false);
    this.pendingAudioBlob = null;
    this._isMuted = false;
  }

  // ============= Getters para la UI =============

  get canStart(): boolean {
    return !this.isInitialized && this.phone.trim().length > 0;
  }

  get isMuted(): boolean {
    return this._isMuted;
  }

  get canMute(): boolean {
    // El botón de mute solo está disponible cuando el bot está hablando
    return this.conversationManager.isBotSpeaking;
  }

  get canStop(): boolean {
    return this.isInitialized;
  }

  get isListening(): boolean {
    return this.conversationState === ConversationState.LISTENING;
  }

  get isProcessing(): boolean {
    return this.conversationState === ConversationState.PROCESSING;
  }

  get isSpeaking(): boolean {
    return this.conversationState === ConversationState.SPEAKING;
  }

  get isPaused(): boolean {
    return this.conversationState === ConversationState.PAUSED;
  }

  get statusText(): string {
    if (!this.isInitialized) return 'No conectado';
    
    if (this._isMuted) return 'Silenciado';
    
    switch (this.conversationState) {
      case ConversationState.IDLE: return 'Esperando...';
      case ConversationState.LISTENING: return 'Escuchando...';
      case ConversationState.PROCESSING: return 'Procesando...';
      case ConversationState.SPEAKING: return 'Bot hablando...';
      case ConversationState.PAUSED: return 'Pausado';
      default: return 'Desconocido';
    }
  }

  get statusColor(): string {
    if (!this.isInitialized) return 'medium';
    
    switch (this.conversationState) {
      case ConversationState.LISTENING: return 'success';
      case ConversationState.PROCESSING: return 'warning';
      case ConversationState.SPEAKING: return 'primary';
      case ConversationState.PAUSED: return 'medium';
      default: return 'medium';
    }
  }

  get wsStateText(): string {
    switch (this.wsState) {
      case WebSocketState.DISCONNECTED: return 'Desconectado';
      case WebSocketState.CONNECTING: return 'Conectando...';
      case WebSocketState.CONNECTED: return 'Conectado';
      case WebSocketState.ERROR: return 'Error';
      default: return 'Desconocido';
    }
  }

  get wsStateColor(): string {
    switch (this.wsState) {
      case WebSocketState.CONNECTED: return 'success';
      case WebSocketState.CONNECTING: return 'warning';
      case WebSocketState.ERROR: return 'danger';
      default: return 'medium';
    }
  }
}
