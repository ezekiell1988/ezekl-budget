export const environment = {
  production: true,
  apiUrl: 'api/v1/',
  
  // Configuración de logs en PRODUCCIÓN
  logging: {
    enabled: false, // ❌ Deshabilitar logs en producción (excepto errors críticos)
    showTimestamp: false,
    showContext: false,
    useColors: false
  }
};
