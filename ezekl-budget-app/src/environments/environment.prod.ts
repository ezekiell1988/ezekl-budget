export const environment = {
  production: true,
  apiUrl: '/1/v1/',
  // WebSocket en producción usa el mismo dominio que el navegador
  wsProtocol: '', // Se detecta automáticamente (ws/wss según http/https)
  wsBaseUrl: '' // Se usa window.location.host automáticamente
};
