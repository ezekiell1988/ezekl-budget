import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { 
  WebSocketState, 
  ConversationState,
  WSResponse,
  WSMessageRequest,
  ConversationMetadata,
  WSShoppingResponse
} from '../shared/models/websocket.models';
import { buildWebSocketUrl, WEBSOCKET_CONFIG } from '../shared/config/websocket.config';
import { LoggerService } from './logger.service';

/**
 * Servicio para manejar la conexión WebSocket con el backend de shopping
 */
@Injectable({
  providedIn: 'root'
})
export class ShoppingWebSocketService {
  private readonly logger = inject(LoggerService).getLogger('ShoppingWebSocketService');
  private ws: WebSocket | null = null;
  private reconnectAttempt = 0;
  private pingIntervalId: any = null;
  
  // Observables de estado
  private wsState$ = new BehaviorSubject<WebSocketState>(WebSocketState.DISCONNECTED);
  private conversationState$ = new BehaviorSubject<ConversationState>(ConversationState.IDLE);
  private messages$ = new Subject<WSResponse>();
  private errors$ = new Subject<string>();
  
  // Metadata de la conversación
  private metadata: ConversationMetadata = {
    phone: '',
    messageCount: 0
  };

  constructor() {}

  /**
   * Conecta al WebSocket
   */
  connect(phone: string, merchantId?: number, returnAudio: boolean = true): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.logger.warn('WebSocket ya está conectado');
      return;
    }

    this.metadata.phone = phone;
    this.metadata.messageCount = 0;
    this.metadata.startTime = Date.now();
    
    const url = buildWebSocketUrl(phone, merchantId, returnAudio);
    
    try {
      this.wsState$.next(WebSocketState.CONNECTING);
      this.ws = new WebSocket(url);
      
      this.setupWebSocketHandlers();
      
      this.logger.debug(`Conectando WebSocket: ${url}`);
    } catch (error) {
      this.logger.error('Error creando WebSocket:', error);
      this.handleError('Error al crear conexión WebSocket');
    }
  }

  /**
   * Configura los event handlers del WebSocket
   */
  private setupWebSocketHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.logger.success('WebSocket conectado');
      this.wsState$.next(WebSocketState.CONNECTED);
      this.reconnectAttempt = 0;
      this.startPingInterval();
    };

    this.ws.onmessage = (event) => {
      try {
        const data: WSResponse = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        this.logger.error('Error parseando mensaje:', error);
      }
    };

    this.ws.onerror = (error) => {
      this.logger.error('WebSocket error:', error);
      this.wsState$.next(WebSocketState.ERROR);
      this.handleError('Error en conexión WebSocket');
    };

    this.ws.onclose = (event) => {
      this.logger.debug(`WebSocket cerrado. Code: ${event.code}, Reason: ${event.reason}`);
      this.wsState$.next(WebSocketState.DISCONNECTED);
      this.stopPingInterval();
      
      // Intentar reconectar si no fue cierre intencional
      if (event.code !== 1000 && this.shouldReconnect()) {
        this.attemptReconnect();
      }
    };
  }

  /**
   * Maneja los mensajes recibidos del WebSocket
   */
  private handleMessage(data: WSResponse): void {
    this.messages$.next(data);

    switch (data.type) {
      case 'conversation_started':
        this.metadata.conversationId = data.conversation_id;
        this.logger.debug(`Conversación iniciada: ${data.conversation_id}`);
        break;
        
      case 'transcription':
        this.logger.debug(`Transcripción recibida: ${(data as any).text}`);
        break;
        
      case 'shopping_response':
      case 'audio_response':
        this.metadata.messageCount++;
        this.metadata.lastMessageTime = Date.now();
        this.handleShoppingResponse(data);
        break;
        
      case 'pong':
        this.logger.debug('Pong recibido');
        break;
        
      case 'error':
        this.logger.error('Error del servidor:', data.error);
        this.handleError(data.error);
        break;
    }
  }

  /**
   * Maneja respuestas de shopping
   */
  private handleShoppingResponse(data: WSShoppingResponse): void {
    this.logger.debug(`Respuesta de shopping recibida (${data.shopping_response.duration_ms}ms)`);
    this.logger.debug(`Audio en shopping_response: ${!!data.shopping_response.audio_base64}`);
    this.logger.debug(`Audio en audio_response: ${!!data.audio_response?.audio_base64}`);
    
    // Aquí puedes agregar lógica adicional como reproducir audio si lo necesitas
    if (data.shopping_response.execution_details) {
      this.logger.debug('Detalles de ejecución:', data.shopping_response.execution_details);
    }
  }

  /**
   * Envía un mensaje de texto al servidor
   */
  sendMessage(message: string, trackingId?: string): void {
    if (!this.isConnected) {
      this.logger.error('WebSocket no está conectado');
      this.handleError('No hay conexión con el servidor');
      return;
    }

    const request: WSMessageRequest = {
      type: 'message',
      data: message,
      tracking_id: trackingId || this.generateTrackingId()
    };

    this.send(request);
    this.conversationState$.next(ConversationState.PROCESSING);
  }

  /**
   * Envía audio en base64 al servidor
   */
  sendAudio(audioBase64: string, format: string = 'webm', language: string = 'es', trackingId?: string): void {
    if (!this.isConnected) {
      this.logger.error('WebSocket no está conectado');
      this.handleError('No hay conexión con el servidor');
      return;
    }

    const request = {
      type: 'audio',
      data: audioBase64,
      format: format,
      language: language,
      tracking_id: trackingId || this.generateTrackingId()
    };

    this.send(request as any);
    this.conversationState$.next(ConversationState.PROCESSING);
  }

  /**
   * Envía un ping al servidor
   */
  sendPing(): void {
    if (!this.isConnected) return;

    const request: WSMessageRequest = {
      type: 'ping',
      tracking_id: this.generateTrackingId()
    };

    this.send(request);
  }

  /**
   * Solicita estadísticas de la conversación
   */
  requestStats(): void {
    if (!this.isConnected) return;

    const request: WSMessageRequest = {
      type: 'stats',
      tracking_id: this.generateTrackingId()
    };

    this.send(request);
  }

  /**
   * Envía datos al WebSocket
   */
  private send(data: WSMessageRequest): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.logger.error('No se puede enviar: WebSocket no está abierto');
      return;
    }

    try {
      this.ws.send(JSON.stringify(data));
      this.logger.debug('Mensaje enviado:', data.type);
    } catch (error) {
      this.logger.error('Error enviando mensaje:', error);
      this.handleError('Error al enviar mensaje');
    }
  }

  /**
   * Inicia el intervalo de ping
   */
  private startPingInterval(): void {
    if (!WEBSOCKET_CONFIG.ping.enabled) return;

    this.pingIntervalId = setInterval(() => {
      this.sendPing();
    }, WEBSOCKET_CONFIG.ping.intervalMs);
  }

  /**
   * Detiene el intervalo de ping
   */
  private stopPingInterval(): void {
    if (this.pingIntervalId) {
      clearInterval(this.pingIntervalId);
      this.pingIntervalId = null;
    }
  }

  /**
   * Determina si debe intentar reconectar
   */
  private shouldReconnect(): boolean {
    return this.reconnectAttempt < WEBSOCKET_CONFIG.reconnect.maxAttempts;
  }

  /**
   * Intenta reconectar al WebSocket
   */
  private attemptReconnect(): void {
    this.reconnectAttempt++;
    
    const delay = WEBSOCKET_CONFIG.reconnect.delayMs * 
                  Math.pow(WEBSOCKET_CONFIG.reconnect.backoffMultiplier, this.reconnectAttempt - 1);
    
    this.logger.info(`Reintentando conexión en ${delay}ms (intento ${this.reconnectAttempt}/${WEBSOCKET_CONFIG.reconnect.maxAttempts})`);
    
    setTimeout(() => {
      if (this.metadata.phone) {
        this.connect(this.metadata.phone);
      }
    }, delay);
  }

  /**
   * Desconecta el WebSocket
   */
  disconnect(): void {
    if (this.ws) {
      this.stopPingInterval();
      this.ws.close(1000, 'Desconexión intencional');
      this.ws = null;
    }
    
    this.wsState$.next(WebSocketState.DISCONNECTED);
    this.conversationState$.next(ConversationState.IDLE);
    
    this.logger.info('WebSocket desconectado');
  }

  /**
   * Maneja errores
   */
  private handleError(error: string): void {
    this.errors$.next(error);
  }

  /**
   * Genera un tracking ID único
   */
  private generateTrackingId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // ============= Getters =============

  get isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  get webSocketState(): Observable<WebSocketState> {
    return this.wsState$.asObservable();
  }

  get conversationState(): Observable<ConversationState> {
    return this.conversationState$.asObservable();
  }

  get messages(): Observable<WSResponse> {
    return this.messages$.asObservable();
  }

  get errors(): Observable<string> {
    return this.errors$.asObservable();
  }

  get conversationMetadata(): ConversationMetadata {
    return { ...this.metadata };
  }

  /**
   * Actualiza el estado de la conversación
   */
  setConversationState(state: ConversationState): void {
    this.conversationState$.next(state);
  }
}
