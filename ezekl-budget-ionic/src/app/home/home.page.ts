import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardSubtitle,
  IonCardContent,
  IonChip,
  IonLabel,
  IonIcon,
  IonButton
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  wifi,
  cloudOffline,
  refresh,
  pulse,
  chatbubble,
  trash
} from 'ionicons/icons';

interface WebSocketMessage {
  id: string;
  type: string;
  content: string;
  timestamp: string;
}

type ConnectionStatus = 'connected' | 'connecting' | 'disconnected';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  imports: [
    CommonModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardSubtitle,
    IonCardContent,
    IonChip,
    IonLabel,
    IonIcon,
    IonButton
  ],
})
export class HomePage implements OnInit, OnDestroy {
  // Estado del WebSocket
  connectionStatus: ConnectionStatus = 'disconnected';
  ws: WebSocket | null = null;
  wsUrl: string = '';
  reconnectAttempts: number = 0;
  maxReconnectAttempts: number = 5;
  reconnectInterval: number = 3000; // 3 segundos

  // Ping-Pong
  pingInterval: any = null;
  pingIntervalTime: number = 30000; // 30 segundos
  lastPing: string = '';
  lastPong: string = '';

  // Mensajes
  messages: WebSocketMessage[] = [];
  maxMessages: number = 10;

  constructor() {
    // Registrar iconos
    addIcons({ wifi, cloudOffline, refresh, pulse, chatbubble, trash });

    // Configurar URL del WebSocket
    this.setupWebSocketUrl();
  }

  ngOnInit() {
    console.log('🏠 HomePage iniciando...');
    this.connect();
  }

  ngOnDestroy() {
    console.log('🏠 HomePage destruyendo...');
    this.disconnect();
  }

  private setupWebSocketUrl(): void {
    // Usar la misma URL base que el frontend, cambiando solo el protocolo a WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;

    // Servidor híbrido: mismo host y puerto para frontend, API y WebSocket
    // Nota: "/ws/" con barra final según nueva estructura de routers
    this.wsUrl = `${protocol}//${host}/ws/`;

    console.log('🔌 WebSocket URL configurada:', this.wsUrl);
  }

  private connect(): void {
    if (this.connectionStatus === 'connecting' || this.connectionStatus === 'connected') {
      return;
    }

    console.log('🔌 Intentando conectar WebSocket...');
    this.connectionStatus = 'connecting';

    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = (event) => {
        console.log('✅ WebSocket conectado', event);
        this.connectionStatus = 'connected';
        this.reconnectAttempts = 0;
        this.addMessage('system', 'Conectado al servidor WebSocket');
        this.startPingInterval();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket desconectado', event);
        this.connectionStatus = 'disconnected';
        this.stopPingInterval();
        this.addMessage('system', `Conexión cerrada (código: ${event.code})`);

        // Intentar reconectar automáticamente
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        } else {
          this.addMessage('error', 'Máximo de intentos de reconexión alcanzado');
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ Error WebSocket:', error);
        this.addMessage('error', 'Error de conexión WebSocket');
      };

    } catch (error) {
      console.error('❌ Error creando WebSocket:', error);
      this.connectionStatus = 'disconnected';
      this.addMessage('error', `Error creando conexión: ${error}`);
      this.scheduleReconnect();
    }
  }

  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data);
      console.log('📨 Mensaje recibido:', message);

      switch (message.type) {
        case 'welcome':
          this.addMessage('welcome', message.message);
          break;
        case 'pong':
          this.lastPong = this.formatTime(new Date().toISOString());
          this.addMessage('pong', `Pong recibido (latencia: ${this.calculateLatency(message)}ms)`);
          break;
        case 'echo':
          this.addMessage('echo', `Echo: ${message.echo}`);
          break;
        case 'error':
          this.addMessage('error', message.message);
          break;
        default:
          this.addMessage('response', message.message || JSON.stringify(message));
      }
    } catch (error) {
      console.error('❌ Error parseando mensaje:', error);
      this.addMessage('error', `Mensaje no válido: ${data}`);
    }
  }

  private calculateLatency(pongMessage: any): number {
    if (pongMessage.client_timestamp) {
      const sentTime = new Date(pongMessage.client_timestamp).getTime();
      const receivedTime = new Date().getTime();
      return receivedTime - sentTime;
    }
    return 0;
  }

  private addMessage(type: string, content: string): void {
    const message: WebSocketMessage = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      type,
      content,
      timestamp: new Date().toISOString()
    };

    this.messages.unshift(message);

    // Mantener solo los últimos N mensajes
    if (this.messages.length > this.maxMessages) {
      this.messages = this.messages.slice(0, this.maxMessages);
    }
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    console.log(`🔄 Programando reconexión (intento ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    setTimeout(() => {
      if (this.connectionStatus === 'disconnected') {
        this.connect();
      }
    }, this.reconnectInterval * this.reconnectAttempts); // Backoff exponencial
  }

  private startPingInterval(): void {
    this.stopPingInterval();
    this.pingInterval = setInterval(() => {
      this.sendPing();
    }, this.pingIntervalTime);
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private disconnect(): void {
    this.stopPingInterval();
    if (this.ws) {
      this.ws.close(1000, 'Cliente desconectándose');
      this.ws = null;
    }
    this.connectionStatus = 'disconnected';
  }

  // Métodos públicos para el template
  sendPing(): void {
    if (this.connectionStatus !== 'connected' || !this.ws) {
      return;
    }

    const pingMessage = {
      type: 'ping',
      timestamp: new Date().toISOString(),
      message: 'ping from client'
    };

    this.ws.send(JSON.stringify(pingMessage));
    this.lastPing = this.formatTime(new Date().toISOString());
    this.addMessage('ping', 'Ping enviado');
  }

  sendEcho(): void {
    if (this.connectionStatus !== 'connected' || !this.ws) {
      return;
    }

    const echoMessage = {
      type: 'echo',
      message: `Test echo desde cliente - ${new Date().toLocaleTimeString()}`,
      timestamp: new Date().toISOString()
    };

    this.ws.send(JSON.stringify(echoMessage));
    this.addMessage('echo', 'Mensaje echo enviado');
  }

  reconnect(): void {
    console.log('🔄 Reconexión manual iniciada...');
    this.disconnect();
    this.reconnectAttempts = 0;
    setTimeout(() => this.connect(), 1000);
  }

  clearMessages(): void {
    this.messages = [];
  }

  getStatusText(): string {
    switch (this.connectionStatus) {
      case 'connected':
        return 'Conectado';
      case 'connecting':
        return 'Conectando...';
      case 'disconnected':
        return 'Desconectado';
      default:
        return 'Desconocido';
    }
  }

  formatTime(isoString: string): string {
    if (!isoString) return '';
    return new Date(isoString).toLocaleTimeString();
  }

  trackByMessage(index: number, message: WebSocketMessage): string {
    return message.id;
  }
}
