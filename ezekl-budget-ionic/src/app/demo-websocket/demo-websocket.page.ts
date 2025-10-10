import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';
import {
  // IonHeader, IonToolbar, IonTitle no usados
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardSubtitle,
  IonCardContent,
  IonChip,
  IonLabel,
  IonIcon,
  IonItem,
  IonList,
  IonBadge,
  IonGrid,
  // IonRow, IonCol no usados
  AlertController,
  ToastController,
  MenuController,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  wifi,
  cloudOffline,
  refresh,
  pulse,
  chatbubble,
  trash,
} from 'ionicons/icons';

import { AppHeaderComponent } from '../shared/components/app-header/app-header.component';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

interface WebSocketMessage {
  id: string;
  type: string;
  content: string;
  timestamp: string;
}

interface CredentialsResponse {
  azure_openai_endpoint: string;
  azure_openai_deployment_name: string;
  message: string;
  server_os?: string;
}

type ConnectionStatus = 'connected' | 'connecting' | 'disconnected';

@Component({
  selector: 'app-demo-websocket',
  templateUrl: './demo-websocket.page.html',
  styleUrls: ['./demo-websocket.page.scss'],
  imports: [
    CommonModule,
    // IonHeader, IonToolbar, IonTitle no usados - usa AppHeaderComponent
    IonContent,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardSubtitle,
    IonCardContent,
    IonChip,
    IonLabel,
    IonIcon,
    IonItem,
    IonList,
    IonBadge,
    IonGrid,
    // IonRow, IonCol no usados
    AppHeaderComponent,
  ],
})
export class DemoWebsocketPage implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

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

  constructor(
    private router: Router,
    private alertController: AlertController,
    private toastController: ToastController,
    private menuController: MenuController,
    private http: HttpClient
  ) {
    // Registrar iconos
    addIcons({
      wifi,
      cloudOffline,
      refresh,
      pulse,
      chatbubble,
      trash,
    });
  }

  async ngOnInit() {
    // Cargar configuración del servidor y luego configurar WebSocket
    await this.loadServerConfigAndConnect();
  }

  private async loadServerConfigAndConnect(): Promise<void> {
    try {
      // Obtener configuración del servidor desde /api/credentials/websocket
      const credentials = await firstValueFrom(
        this.http.get<CredentialsResponse>('/api/credentials/websocket')
      );

      console.log('📋 Configuración del servidor cargada:', {
        server_os: credentials.server_os,
        endpoint: credentials.azure_openai_endpoint
      });

      // Configurar URL del WebSocket según el SO del servidor
      this.setupWebSocketUrl(credentials.server_os);

      // Conectar al WebSocket
      this.connect();
    } catch (error) {
      console.error('❌ Error cargando configuración del servidor:', error);
      console.log('⚠️ Usando configuración por defecto para WebSocket');

      // Intentar conectar de todas formas con configuración por defecto
      this.setupWebSocketUrl();
      this.connect();
    }
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    this.disconnect();
  }

  private setupWebSocketUrl(serverOS?: string): void {
    // Usar la misma URL base que el frontend, cambiando solo el protocolo a WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let host = window.location.host;

    // FIX SOLO PARA WINDOWS: Reemplazar 'localhost' con '127.0.0.1'
    // En Windows, localhost puede resolver a IPv6 (::1) causando problemas con WebSockets
    // Este fix se aplica SOLO cuando el servidor está corriendo en Windows
    const isServerWindows = serverOS === 'Windows';

    if (isServerWindows && host.startsWith('localhost')) {
      host = host.replace('localhost', '127.0.0.1');
      console.log('🔧 [Windows Server] WebSocket usando 127.0.0.1 en lugar de localhost');
      console.log('   Razón: El servidor está corriendo en Windows y localhost puede resolver a IPv6');
    }

    // Servidor híbrido: mismo host y puerto para frontend, API y WebSocket
    this.wsUrl = `${protocol}//${host}/ws/`;

    console.log('🔌 WebSocket configurado:', {
      url: this.wsUrl,
      serverOS: serverOS || 'Desconocido',
      windowsFixApplied: isServerWindows && host.includes('127.0.0.1')
    });
  }

  private connect(): void {
    if (
      this.connectionStatus === 'connecting' ||
      this.connectionStatus === 'connected'
    ) {
      return;
    }

    this.connectionStatus = 'connecting';

    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = (event) => {
        this.connectionStatus = 'connected';
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onclose = (event) => {
        this.connectionStatus = 'disconnected';
        if (event.code !== 1000) {
          this.scheduleReconnect();
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

      switch (message.type) {
        case 'welcome':
          this.addMessage('welcome', message.message);
          break;
        case 'pong':
          this.lastPong = this.formatTime(new Date().toISOString());
          this.addMessage(
            'pong',
            `Pong recibido (latencia: ${this.calculateLatency(message)}ms)`
          );
          break;
        case 'echo':
          this.addMessage('echo', `Echo: ${message.echo}`);
          break;
        case 'error':
          this.addMessage('error', message.message);
          break;
        default:
          this.addMessage(
            'response',
            message.message || JSON.stringify(message)
          );
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
      timestamp: new Date().toISOString(),
    };

    this.messages.unshift(message);

    // Mantener solo los últimos N mensajes
    if (this.messages.length > this.maxMessages) {
      this.messages = this.messages.slice(0, this.maxMessages);
    }
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;

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
      message: 'ping from client',
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
      timestamp: new Date().toISOString(),
    };

    this.ws.send(JSON.stringify(echoMessage));
    this.addMessage('echo', 'Mensaje echo enviado');
  }

  reconnect(): void {
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
