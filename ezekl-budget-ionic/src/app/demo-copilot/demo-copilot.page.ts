import { Component, OnInit, OnDestroy, AfterViewInit, ViewChild, ElementRef, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  IonToolbar,
  IonContent,
  IonGrid,
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
  IonSegment,
  IonSegmentButton,
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  send,
  chatbubblesOutline,
  wifi,
  cloudOffline,
  refresh,
} from 'ionicons/icons';
import { AppHeaderComponent } from '../shared/components/app-header/app-header.component';
import { AuthService } from '../services/auth.service';

interface ChatMessage {
  id: string;
  role: 'user' | 'bot';
  text: string;
  timestamp: string;
}

interface DirectLineToken {
  token: string;
  conversationId: string;
  streamUrl?: string;
  expires_in?: number;
}

@Component({
  selector: 'app-demo-copilot',
  templateUrl: './demo-copilot.page.html',
  styleUrls: ['./demo-copilot.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonToolbar,
    IonContent,
    IonGrid,
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
    IonSegment,
    IonSegmentButton,
    AppHeaderComponent,
  ],
})
export class DemoCopilotPage implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('chatContainer') chatContainer!: ElementRef;

  // ==================== MODO DE CHAT ====================
  chatMode: 'custom' | 'embed' = 'custom'; // Cambiar a custom temporalmente hasta configurar auth

  // ==================== CONFIGURACIÓN COPILOT STUDIO ====================
  private readonly copilotConfig = {
    environmentId: '3c48723d-81b5-473a-9006-a54c8652fe7c',
    tenantId: '2f80d4e1-da0e-4b6d-84da-30f67e280e4b',
    botId: '821348e9-0a4b-4805-9085-492c217c0bd0',
    schemaName: 'cr389_agent_ROzgg7',
    directLineEndpoint: 'https://directline.botframework.com/v3/directline',
  };

  // Estado de conexión
  isConnected = false;
  isConnecting = false;
  connectionStatusText = 'Desconectado';

  // Mensajes
  messages: ChatMessage[] = [];
  messageText = '';
  isBotTyping = false;

  // Direct Line
  private token = '';
  private conversationId = '';
  private streamUrl = '';
  private watermark = '';
  private pollingInterval: any = null;

  // Usuario
  private userName: string = 'Usuario';

  constructor(
    private cdr: ChangeDetectorRef,
    private authService: AuthService,
    private http: HttpClient
  ) {
    addIcons({
      send,
      chatbubblesOutline,
      wifi,
      cloudOffline,
      refresh,
    });
  }

  async ngOnInit() {
    // Cargar nombre del usuario
    this.loadUserName();

    // Solo conectar a Direct Line si está en modo custom
    if (this.chatMode === 'custom') {
      await this.connectToDirectLine();
    }
  }

  onChatModeChange() {
    // Si cambia a modo custom, conectar a Direct Line
    if (this.chatMode === 'custom' && !this.isConnected) {
      this.connectToDirectLine();
    }
    // Si cambia a embed, limpiar la conexión de Direct Line
    if (this.chatMode === 'embed') {
      this.disconnect();
    }
  }

  private loadUserName(): void {
    const user = this.authService.currentUser;
    if (user?.nameLogin) {
      this.userName = user.nameLogin;
    }
  }

  ngAfterViewInit() {
    setTimeout(() => this.scrollToBottom(), 0);
  }

  ngOnDestroy() {
    this.disconnect();
  }

  // ==================== CONEXIÓN DIRECT LINE ====================

  private async connectToDirectLine(): Promise<void> {
    try {
      this.isConnecting = true;
      this.connectionStatusText = 'Conectando...';
      this.cdr.detectChanges();

      // Obtener token de Direct Line desde nuestro backend seguro
      const tokenResponse = await firstValueFrom(
        this.http.get<DirectLineToken>(`${environment.apiUrl}/api/copilot/token`)
      );

      if (!tokenResponse || !tokenResponse.token) {
        throw new Error('Error al generar token de Direct Line');
      }

      this.token = tokenResponse.token;
      this.conversationId = tokenResponse.conversationId;
      this.streamUrl = tokenResponse.streamUrl || '';

      // Conexión exitosa
      this.isConnected = true;
      this.connectionStatusText = 'Conectado';
      console.log('✅ Conectado a Copilot Studio');

      // Iniciar polling de mensajes
      this.startPolling();
    } catch (error) {
      console.error('❌ Error al conectar:', error);
      this.connectionStatusText = 'Error de conexión';
      this.isConnected = false;
    } finally {
      this.isConnecting = false;
      this.cdr.detectChanges();
    }
  }

  private startPolling(): void {
    // Polling cada 2 segundos para obtener nuevos mensajes
    this.pollingInterval = setInterval(() => {
      this.getMessages();
    }, 2000);
  }

  private async getMessages(): Promise<void> {
    if (!this.token || !this.conversationId) return;

    try {
      const url = `${this.copilotConfig.directLineEndpoint}/conversations/${this.conversationId}/activities${
        this.watermark ? `?watermark=${this.watermark}` : ''
      }`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (!response.ok) return;

      const data = await response.json();
      this.watermark = data.watermark;

      // Procesar actividades nuevas
      if (data.activities && data.activities.length > 0) {
        for (const activity of data.activities) {
          // Ignorar mensajes del usuario
          if (activity.from.id === 'user') continue;

          // Agregar mensaje del bot
          if (activity.type === 'message' && activity.text) {
            this.addBotMessage(activity.text);
          }
        }
      }
    } catch (error) {
      console.error('Error al obtener mensajes:', error);
    }
  }

  private disconnect(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
    this.isConnected = false;
    this.connectionStatusText = 'Desconectado';
  }

  // ==================== ENVÍO DE MENSAJES ====================

  async sendMessage(): Promise<void> {
    if (!this.messageText.trim() || !this.isConnected) return;

    const userMessage = this.messageText.trim();
    this.messageText = '';

    // Agregar mensaje del usuario
    this.addUserMessage(userMessage);

    // Mostrar indicador de escritura
    this.isBotTyping = true;

    try {
      // Enviar mensaje a Direct Line
      const response = await fetch(
        `${this.copilotConfig.directLineEndpoint}/conversations/${this.conversationId}/activities`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'message',
            from: { id: 'user', name: this.userName },
            text: userMessage,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Error al enviar mensaje');
      }

      console.log('✅ Mensaje enviado');
    } catch (error) {
      console.error('❌ Error al enviar mensaje:', error);
      this.addBotMessage('Lo siento, hubo un error al enviar tu mensaje.');
      this.isBotTyping = false;
    }
  }

  // ==================== MANEJO DE MENSAJES ====================

  private addUserMessage(text: string): void {
    const message: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: text,
      timestamp: new Date().toISOString(),
    };
    this.messages.push(message);
    this.cdr.detectChanges();
    this.scrollToBottom();
  }

  private addBotMessage(text: string): void {
    const message: ChatMessage = {
      id: `bot-${Date.now()}`,
      role: 'bot',
      text: text,
      timestamp: new Date().toISOString(),
    };
    this.messages.push(message);
    this.isBotTyping = false;
    this.cdr.detectChanges();
    this.scrollToBottom();
  }

  // ==================== UTILIDADES ====================

  private scrollToBottom(): void {
    setTimeout(() => {
      if (this.chatContainer?.nativeElement) {
        this.chatContainer.nativeElement.scrollTo(0, this.chatContainer.nativeElement.scrollHeight);
      }
    }, 100);
  }

  formatTime(isoString: string): string {
    const date = new Date(isoString);
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
  }
}
