/**
 * Configuración para WebSocket
 */
import { environment } from '../../../environments/environment';

export const WEBSOCKET_CONFIG = {
  // Merchant ID por defecto
  defaultMerchantId: 1,
  
  // Versión de API
  apiVersion: 'v1',
  
  // Azure OpenAI Realtime API
  azureOpenAI: {
    credentialsEndpoint: 'credentials/realtime',
    apiVersion: '2024-12-01-preview'
  },
  
  // Reintentos de reconexión
  reconnect: {
    maxAttempts: 5,
    delayMs: 3000,
    backoffMultiplier: 1.5
  },
  
  // Ping para mantener conexión viva
  ping: {
    enabled: true,
    intervalMs: 30000
  },
  
  // Timeouts
  timeouts: {
    connectionMs: 10000,
    responseMs: 30000
  }
} as const;

/**
 * Credenciales de Azure OpenAI Realtime
 */
export interface AzureOpenAICredentials {
  azure_openai_endpoint: string;
  azure_openai_api_key: string;
  azure_openai_deployment_name: string;
  server_os: string;
  message: string;
}

/**
 * Obtiene las credenciales de Azure OpenAI desde el API
 * 
 * @returns Promise con las credenciales de Azure OpenAI
 */
export async function getAzureOpenAICredentials(): Promise<AzureOpenAICredentials> {
  const url = `${environment.apiUrl}${WEBSOCKET_CONFIG.azureOpenAI.credentialsEndpoint}`;
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  
  if (!response.ok) {
    throw new Error(`Error al obtener credenciales: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Genera la URL del WebSocket de Azure OpenAI Realtime API
 * 
 * Formato: wss://{resource-name}.openai.azure.com/openai/realtime?api-version={api-version}&deployment={deployment-name}
 * 
 * @param credentials - Credenciales obtenidas del API
 * @returns URL completa del WebSocket de Azure OpenAI
 */
export function buildAzureOpenAIWebSocketUrl(credentials: AzureOpenAICredentials): string {
  const { azure_openai_endpoint, azure_openai_deployment_name } = credentials;
  const { apiVersion } = WEBSOCKET_CONFIG.azureOpenAI;
  
  // Extraer el hostname del endpoint (remover https:// y rutas adicionales)
  const endpointUrl = new URL(azure_openai_endpoint);
  const hostname = endpointUrl.hostname;
  
  return `wss://${hostname}/openai/realtime?api-version=${apiVersion}&deployment=${azure_openai_deployment_name}`;
}

/**
 * Genera la URL completa del WebSocket para ClickEat
 * 
 * Formato desarrollo: ws://localhost:9001/{merchantId}/v1/ws/clickeat/shopping/{phone}?return_audio=true
 * Formato producción: wss://local-host.ezekl.com/{merchantId}/v1/ws/clickeat/shopping/{phone}?return_audio=true
 * 
 * @param phone - Número de teléfono del cliente
 * @param merchantId - ID del merchant (opcional, usa defaultMerchantId si no se proporciona)
 * @param returnAudio - Si se debe recibir audio del backend (true) o solo texto (false). Default: true
 * 
 * Detecta automáticamente el protocolo y dominio según window.location
 */
export function buildWebSocketUrl(phone: string, merchantId?: number, returnAudio: boolean = true): string {
  const { apiVersion, defaultMerchantId } = WEBSOCKET_CONFIG;
  const merchant = merchantId ?? defaultMerchantId;
  
  // Detectar protocolo WebSocket según HTTP/HTTPS
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  
  // Usar el host actual del navegador
  const baseUrl = window.location.host;
  
  return `${protocol}://${baseUrl}/${merchant}/${apiVersion}/ws/clickeat/shopping/${phone}?return_audio=${returnAudio}`;
}
