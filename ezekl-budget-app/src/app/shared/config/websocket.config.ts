/**
 * Configuración para WebSocket
 */
import { environment } from '../../../environments/environment';

export const WEBSOCKET_CONFIG = {
  // Merchant ID por defecto
  defaultMerchantId: 1,
  
  // Versión de API
  apiVersion: 'v1',
  
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
 * Genera la URL completa del WebSocket
 * 
 * Formato desarrollo: ws://localhost:9001/{merchantId}/v1/ws/clickeat/shopping/{phone}?return_audio=true
 * Formato producción: wss://local-host.ezekl.com/{merchantId}/v1/ws/clickeat/shopping/{phone}?return_audio=true
 * 
 * @param phone - Número de teléfono del cliente
 * @param merchantId - ID del merchant (opcional, usa defaultMerchantId si no se proporciona)
 * @param returnAudio - Si se debe recibir audio del backend (true) o solo texto (false). Default: true
 * 
 * Detecta automáticamente el protocolo y dominio según el environment y window.location
 */
export function buildWebSocketUrl(phone: string, merchantId?: number, returnAudio: boolean = true): string {
  const { apiVersion, defaultMerchantId } = WEBSOCKET_CONFIG;
  const merchant = merchantId ?? defaultMerchantId;
  
  // Detectar protocolo WebSocket
  let protocol: string;
  if (environment.wsProtocol) {
    // Usar el protocolo del environment (desarrollo)
    protocol = environment.wsProtocol;
  } else {
    // Detectar automáticamente según HTTP/HTTPS (producción)
    protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  }
  
  // Detectar host
  let baseUrl: string;
  if (environment.wsBaseUrl) {
    // Usar el host del environment (desarrollo)
    baseUrl = environment.wsBaseUrl;
  } else {
    // Usar el host actual del navegador (producción)
    baseUrl = window.location.host;
  }
  
  return `${protocol}://${baseUrl}/${merchant}/${apiVersion}/ws/clickeat/shopping/${phone}?return_audio=${returnAudio}`;
}
