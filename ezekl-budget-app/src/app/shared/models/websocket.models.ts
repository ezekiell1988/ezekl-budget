/**
 * Modelos para WebSocket de Shopping Voice
 */

// ============= Estados =============
export enum WebSocketState {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  ERROR = 'error'
}

export enum ConversationState {
  IDLE = 'idle',
  LISTENING = 'listening',
  PROCESSING = 'processing',
  SPEAKING = 'speaking',
  PAUSED = 'paused'
}

// ============= Mensajes de entrada =============
export interface WSMessageRequest {
  type: 'message' | 'audio' | 'ping' | 'stats';
  data?: string;
  format?: string;  // Para audio: webm, wav, mp3
  language?: string;  // Para audio: es, en
  tracking_id?: string;
}

// ============= Mensajes de respuesta =============
export interface WSBaseResponse {
  type: string;
  tracking_id?: string;
  conversation_id?: string;
  timestamp?: number;
}

export interface WSConversationStarted extends WSBaseResponse {
  type: 'conversation_started';
  phone: string;
  merchant_id: number;
  message: string;
}

export interface WSTranscriptionResponse extends WSBaseResponse {
  type: 'transcription';
  text: string;
  language?: string;
  duration_ms: number;
}

export interface WSShoppingResponse extends WSBaseResponse {
  type: 'shopping_response' | 'audio_response';
  success: boolean;
  transcription?: {
    text: string;
    language?: string;
    duration_ms: number;
  };
  shopping_response: {
    response: string;
    audio_base64?: string;  // Audio generado por ElevenLabs en base64
    duration_ms: number;
    execution_details: ExecutionDetail[];
  };
  audio_response?: {
    audio_base64: string;
    format: string;
    duration_ms: number;
  };
  total_response_time_ms: number;
}

export interface WSPongResponse extends WSBaseResponse {
  type: 'pong';
}

export interface WSStatsResponse extends WSBaseResponse {
  type: 'stats_response';
  conversation_stats: any;
}

export interface WSErrorResponse extends WSBaseResponse {
  type: 'error';
  error: string;
}

export type WSResponse = 
  | WSConversationStarted 
  | WSTranscriptionResponse
  | WSShoppingResponse 
  | WSPongResponse 
  | WSStatsResponse 
  | WSErrorResponse;

// ============= Detalles de ejecución =============
export interface ExecutionDetail {
  tool_name: string;
  duration_ms: number;
  status: string;
  result?: any;
}

// ============= Configuración de conexión =============
export interface WebSocketConfig {
  url: string;
  merchantId: number;
  reconnectAttempts: number;
  reconnectDelay: number;
  pingInterval: number;
}

// ============= Estado de la conversación =============
export interface ConversationMetadata {
  conversationId?: string;
  phone: string;
  startTime?: number;
  messageCount: number;
  lastMessageTime?: number;
}
