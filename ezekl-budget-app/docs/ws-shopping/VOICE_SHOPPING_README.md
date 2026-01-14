# Asistente de Voz - Voice Shopping

Página de asistente de voz con WebSocket para realizar compras por voz en tiempo real.

## 📁 Estructura de Archivos

### Modelos (`/shared/models/`)
- `websocket.models.ts` - Tipos e interfaces para WebSocket y estados de conversación

### Configuraciones (`/shared/config/`)
- `websocket.config.ts` - Configuración del WebSocket (URL, reconexión, ping)
- `audio.config.ts` - Configuración de audio (micrófono, grabación, detección de voz)

### Servicios (`/service/`)
- `audio-recorder.service.ts` - Manejo de grabación de audio con MediaRecorder API
- `shopping-websocket.service.ts` - Gestión de conexión WebSocket y mensajes

### Página (`/pages/voice-shopping/`)
- `voice-shopping.ts` - Componente principal
- `voice-shopping.html` - Template
- `voice-shopping.scss` - Estilos

## 🚀 Características

### Estados de Conexión
- **DISCONNECTED**: Sin conexión
- **CONNECTING**: Conectando...
- **CONNECTED**: Conectado y listo
- **ERROR**: Error en conexión

### Estados de Conversación
- **IDLE**: Esperando
- **LISTENING**: Escuchando al usuario
- **PROCESSING**: Procesando mensaje
- **SPEAKING**: Bot hablando
- **PAUSED**: Escucha pausada

### Controles

1. **Iniciar Conversación**
   - Ingresa número de teléfono
   - Click en "Iniciar Conversación"
   - Permite acceso al micrófono

2. **Mute (Silenciar)**
   - Solo habilitado cuando el bot está hablando
   - Toggle para activar/desactivar el flag de mute
   - Cuando está activo, el micrófono NO se reactivará automáticamente al terminar el bot
   - Icono: `volume-mute-outline` (normal) / `mic-off-outline` (activo)
   - Color: Amarillo (warning) / Rojo (danger cuando está muteado)

3. **Stop (Descartar)**
   - Disponible siempre durante la conversación
   - Detiene el micrófono inmediatamente
   - Limpia el audio que esté en caché
   - NO envía nada al WebSocket
   - Útil para cancelar lo que se está grabando
   - Icono: `trash-outline`
   - Color: Gris (medium)

**Interrupción Automática del Bot:**
   - Si el bot está hablando y detectas que quieres hablar
   - **Solo comienza a hablar** - el sistema detectará automáticamente tu voz
   - El audio del bot se detendrá inmediatamente
   - Tu micrófono se activará para capturar tu mensaje
   - No necesitas presionar ningún botón
   - Umbral de detección: nivel de audio > 30

4. **Colgar (Finalizar)**
   - Disponible siempre durante la conversación
   - Libera audio pendiente de envío
   - Detiene la reproducción del bot si está hablando
   - Desconecta el WebSocket
   - Limpia recursos y regresa al estado inicial
   - Icono: `call-outline`
   - Color: Rojo (danger)

## 🔧 Configuración

### WebSocket
Edita `/shared/config/websocket.config.ts`:

```typescript
export const WEBSOCKET_CONFIG = {
  protocol: 'ws',        // ws o wss
  host: 'localhost',     // IP o dominio
  port: 8880,           // Puerto
  defaultMerchantId: 1, // Merchant por defecto
  // ... más configuraciones
}
```

### Audio
Edita `/shared/config/audio.config.ts`:

```typescript
export const AUDIO_CONFIG = {
  microphone: {
    sampleRate: 16000,        // Hz
    channelCount: 1,          // Mono
    echoCancellation: true,
    noiseSuppression: true,
  },
  recording: {
    silenceThresholdMs: 1500, // Tiempo de silencio para enviar
    silenceLevel: 30,         // Nivel de audio considerado silencio
  }
}
```

## 📡 Protocolo WebSocket

### URL de conexión
```
ws://localhost:8880/1/v1/ws/clickeat/shopping/{phone}?return_audio=true|false
```

**Parámetros:**
- `phone`: Número de teléfono del cliente
- `return_audio` (Query): Si se debe generar y retornar audio (true) o solo texto (false). Default: false

### Mensajes de entrada (Cliente → Servidor)

**Enviar mensaje:**
```json
{
  "type": "message",
  "data": "texto del mensaje",
  "tracking_id": "opcional"
}
```

**Ping:**
```json
{
  "type": "ping",
  "tracking_id": "opcional"
}
```

**Solicitar estadísticas:**
```json
{
  "type": "stats",
  "tracking_id": "opcional"
}
```

### Mensajes de salida (Servidor → Cliente)

**Conversación iniciada:**
```json
{
  "type": "conversation_started",
  "conversation_id": "uuid",
  "phone": "50683681485",
  "merchant_id": 1,
  "message": "Conexión iniciada",
  "timestamp": 1234567890
}
```

**Respuesta de shopping:**
```json
{
  "type": "shopping_response",
  "success": true,
  "conversation_id": "uuid",
  "tracking_id": "track-123",
  "shopping_response": {
    "response": "texto de respuesta",
    "duration_ms": 1234,
    "execution_details": [...]
  },
  "total_response_time_ms": 5678
}
```

**Error:**
```json
{
  "type": "error",
  "error": "mensaje de error",
  "conversation_id": "uuid",
  "tracking_id": "track-123"
}
```

## 🎨 Interfaz de Usuario

### Indicadores Visuales
- **Nivel de audio**: Barra de progreso muestra intensidad del micrófono
- **Estado del micrófono**: Ícono animado cuando está escuchando
- **Botón de mute**: Cambia de amarillo (pause) a rojo (mic-off) según estado
- **Estado de conversación**: Muestra "Silenciado" cuando el mute está activo
- **Badges de estado**: Colores según estado (verde=ok, amarillo=procesando, rojo=error)

### Historial de Mensajes
- **Usuario**: Mensajes en azul, alineados a la derecha
- **Bot**: Mensajes en gris, alineados a la izquierda
- **Sistema**: Mensajes centrados (verde=info, rojo=error)

## 🔐 Permisos Necesarios

- **Micrófono**: Requerido para grabación de voz
  - El navegador solicitará permiso al iniciar
  - Solo funciona en HTTPS o localhost

## 🐛 Solución de Problemas

### "No se pudo acceder al micrófono"
- Verifica permisos del navegador
- Asegúrate de estar en HTTPS o localhost
- Revisa configuración del sistema operativo

### "WebSocket no conecta"
- Verifica que el backend esté corriendo
- Revisa configuración de host/puerto en `websocket.config.ts`
- Comprueba firewall y CORS

### "Audio no se envía"
- Verifica nivel de audio (debe superar el umbral de silencio)
- Ajusta `silenceLevel` en `audio.config.ts` si es necesario
- Comprueba consola del navegador para errores

## 📝 Flujo de Funcionamiento

1. Usuario ingresa teléfono y presiona "Iniciar"
2. Sistema solicita permisos de micrófono
3. Se establece conexión WebSocket
4. Servidor envía `conversation_started`
5. Sistema inicia grabación automáticamente
6. Usuario habla → Audio se graba continuamente
7. Al detectar silencio → Audio se convierte a Base64 y se envía
8. Servidor procesa con ShoppingProcessor (genera texto + audio ElevenLabs)
9. Servidor responde con texto en `shopping_response.response` y audio en `audio_response.audio_base64`
10. Sistema muestra texto y reproduce audio del bot (con logs de diagnóstico)
11. Al terminar el audio, reinicia escucha automáticamente (solo si NO está en mute)
12. Si está en mute, el micrófono permanece silenciado hasta que el usuario lo reactive
13. Ciclo se repite hasta "Finalizar"

**Nota importante**: El audio viene en `response.audio_response.audio_base64` cuando `return_audio=true`, no en `shopping_response.audio_base64`.

## 🔄 Detección de Silencio

El sistema usa dos métricas:
- **Nivel de audio**: Promedio de frecuencias del micrófono
- **Tiempo de silencio**: Tiempo transcurrido sin sonido

Cuando `nivel < silenceLevel` por más de `silenceThresholdMs`, se considera fin de frase y se envía el audio.

## 🎯 Navegación

La página está disponible en la ruta:
```
/voice-shopping
```

Sin protección de AuthGuard para facilitar pruebas.

## 📦 Dependencias

- **Ionic Angular Standalone**: Componentes UI
- **RxJS**: Manejo de observables
- **MediaRecorder API**: Grabación de audio
- **WebSocket API**: Comunicación en tiempo real

## 🚧 Próximas Mejoras

- [x] ~~Conversión de audio a base64~~ ✅ COMPLETADO
- [x] ~~Reproducción de audio de respuestas~~ ✅ COMPLETADO y CORREGIDO
  - [x] Audio se busca correctamente en `audio_response.audio_base64`
  - [x] Logs de diagnóstico agregados para troubleshooting
  - [x] Manejo de errores mejorado en reproducción
  - [x] **Optimizado para iOS/Safari** - Usa Blob + ObjectURL en lugar de data URI
  - [x] Atributo `playsinline` para compatibilidad iOS
  - [x] Limpieza automática de recursos (revoke ObjectURL)
- [ ] Soporte para múltiples idiomas
- [ ] Historial persistente de conversaciones
- [ ] Configuración de volumen y velocidad de reproducción
- [ ] Modo offline con cola de mensajes
- [ ] Cancelación de reproducción de audio del bot
- [ ] Visualización de forma de onda del audio

---

**Desarrollado con** ❤️ **usando Angular 20+ y Ionic**
