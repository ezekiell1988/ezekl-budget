/**
 * Servicio para obtener credenciales de WebSocket
 * Centraliza las llamadas a la API para obtener configuración del servidor
 */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface WebSocketCredentials {
  azure_openai_endpoint: string;
  azure_openai_deployment_name: string;
  message: string;
  server_os?: string;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketCredentialsService {
  private readonly API_BASE = '/api/v1/credentials';

  constructor(private http: HttpClient) {}

  /**
   * Obtiene credenciales para WebSocket demo
   */
  getWebSocketCredentials(): Observable<WebSocketCredentials> {
    return this.http.get<WebSocketCredentials>(`${this.API_BASE}/websocket`);
  }
}
