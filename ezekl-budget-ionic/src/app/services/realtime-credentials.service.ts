/**
 * Servicio para obtener credenciales de Azure OpenAI Realtime API
 * Centraliza las llamadas a la API para obtener configuración de Realtime
 */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface RealtimeCredentials {
  azure_openai_endpoint: string;
  azure_openai_api_key: string;
  azure_openai_deployment_name: string;
  server_os?: string;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class RealtimeCredentialsService {
  private readonly API_BASE = '/api/v1/credentials';

  constructor(private http: HttpClient) {}

  /**
   * Obtiene credenciales para Azure OpenAI Realtime API
   */
  getRealtimeCredentials(): Observable<RealtimeCredentials> {
    return this.http.get<RealtimeCredentials>(`${this.API_BASE}/realtime`);
  }
}
