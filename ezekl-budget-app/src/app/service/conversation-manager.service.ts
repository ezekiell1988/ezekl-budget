import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ConversationState } from '../shared/models';

export interface ConversationMessage {
  type: 'user' | 'bot' | 'system';
  text: string;
  timestamp: Date;
  isError?: boolean;
  executionDetails?: any[];
}

/**
 * Servicio para gestionar el estado y los mensajes de la conversación
 */
@Injectable({
  providedIn: 'root'
})
export class ConversationManagerService {
  private messagesSubject = new BehaviorSubject<ConversationMessage[]>([]);
  private conversationStateSubject = new BehaviorSubject<ConversationState>(ConversationState.IDLE);
  private isBotSpeakingSubject = new BehaviorSubject<boolean>(false);

  // Observables públicos
  messages$: Observable<ConversationMessage[]> = this.messagesSubject.asObservable();
  conversationState$: Observable<ConversationState> = this.conversationStateSubject.asObservable();
  isBotSpeaking$: Observable<boolean> = this.isBotSpeakingSubject.asObservable();

  get messages(): ConversationMessage[] {
    return this.messagesSubject.value;
  }

  get conversationState(): ConversationState {
    return this.conversationStateSubject.value;
  }

  get isBotSpeaking(): boolean {
    return this.isBotSpeakingSubject.value;
  }

  /**
   * Actualiza el estado de la conversación
   */
  setConversationState(state: ConversationState): void {
    this.conversationStateSubject.next(state);
  }

  /**
   * Actualiza el estado de si el bot está hablando
   */
  setBotSpeaking(speaking: boolean): void {
    this.isBotSpeakingSubject.next(speaking);
  }

  /**
   * Agrega un mensaje del usuario
   */
  addUserMessage(text: string): void {
    const message: ConversationMessage = {
      type: 'user',
      text,
      timestamp: new Date()
    };
    this.addMessage(message);
  }

  /**
   * Agrega un mensaje del bot
   */
  addBotMessage(text: string, executionDetails?: any[]): void {
    const message: ConversationMessage = {
      type: 'bot',
      text,
      timestamp: new Date(),
      executionDetails
    };
    this.addMessage(message);
  }

  /**
   * Agrega un mensaje del sistema
   */
  addSystemMessage(text: string, isError: boolean = false): void {
    const message: ConversationMessage = {
      type: 'system',
      text,
      timestamp: new Date(),
      isError
    };
    this.addMessage(message);
  }

  /**
   * Agrega un mensaje al historial
   */
  private addMessage(message: ConversationMessage): void {
    const currentMessages = this.messagesSubject.value;
    this.messagesSubject.next([...currentMessages, message]);
  }

  /**
   * Limpia todos los mensajes
   */
  clearMessages(): void {
    this.messagesSubject.next([]);
  }

  /**
   * Resetea el servicio al estado inicial
   */
  reset(): void {
    this.clearMessages();
    this.setConversationState(ConversationState.IDLE);
    this.setBotSpeaking(false);
  }

  /**
   * Verifica si un objeto tiene propiedades
   */
  hasDetails(details: any): boolean {
    return details && typeof details === 'object' && Object.keys(details).length > 0;
  }

  /**
   * Convierte objeto details a array de pares clave-valor
   */
  getDetailsEntries(details: any): Array<{key: string, value: any}> {
    if (!this.hasDetails(details)) return [];
    return Object.entries(details).map(([key, value]) => ({ key, value }));
  }

  /**
   * Formatea el valor para mostrar (convierte objetos/arrays a JSON)
   */
  formatValue(value: any): string {
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  }

  /**
   * Formatea la duración en milisegundos
   */
  formatDuration(ms: number): string {
    if (ms < 1000) return `${ms}ms`;
    const seconds = (ms / 1000).toFixed(2);
    return `${seconds}s`;
  }

  /**
   * Calcula el tiempo total de ejecución sumando todos los duration_ms
   */
  getTotalDuration(executionDetails: any[]): number {
    if (!executionDetails || !Array.isArray(executionDetails)) return 0;
    return executionDetails.reduce((total, detail) => {
      return total + (detail.duration_ms || 0);
    }, 0);
  }

  /**
   * Calcula el porcentaje de tiempo que tomó una operación respecto al total
   */
  getPercentage(duration: number, total: number): number {
    if (total === 0) return 0;
    return (duration / total) * 100;
  }
}
