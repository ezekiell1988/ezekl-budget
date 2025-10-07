# Demo Realtime - Azure OpenAI Realtime API

## 📋 Descripción

Implementación completa de un chat en tiempo real estilo WhatsApp que integra la API de Azure OpenAI Realtime. Soporta conversaciones por voz y texto con transcripción en tiempo real, detección de voz (VAD) del lado del servidor, y reproducción automática de respuestas de audio.

---

## 🏗️ Arquitectura de la Solución

### Tecnologías Utilizadas

- **Frontend**: Ionic 8.0.0 + Angular 20.0.0 (Standalone Components)
- **Backend**: FastAPI con endpoints para credenciales de Azure
- **Azure AI**: Azure OpenAI Realtime API
  - **Deployment**: `gpt-realtime` (Sweden Central)
  - **API Version**: `2024-10-01-preview`
  - **Región**: Sweden Central (disponibilidad regional)
- **Audio Processing**: Web Audio API + AudioWorklet
- **WebSocket**: Comunicación bidireccional en tiempo real

---

## 📦 Interfaces y Modelos

### `RealtimeCredentials`
```typescript
interface RealtimeCredentials {
  azure_openai_endpoint: string;     // URL del endpoint de Azure OpenAI
  azure_openai_api_key: string;      // API Key para autenticación
  azure_openai_deployment_name: string; // Nombre del deployment (ej: gpt-4o-realtime)
  server_os?: string;                // Sistema operativo del servidor (opcional)
  message: string;                   // Mensaje de estado
}
```

**Propósito**: Almacenar las credenciales necesarias para conectarse a Azure OpenAI Realtime API.

---

### `ChatMessage`
```typescript
interface ChatMessage {
  id: string;                  // ID único del mensaje (del servidor o generado)
  role: 'user' | 'assistant';  // Rol del emisor
  type: 'text' | 'audio';      // Tipo de mensaje
  content: string;             // Contenido del mensaje o transcripción
  timestamp: string;           // Marca de tiempo ISO
  audioBlob?: Blob;            // Blob de audio para reproducción (opcional)
  transcription?: string;      // Transcripción del audio (opcional)
  tokens?: number;             // Cantidad de tokens utilizados (opcional)
  isTranscribing?: boolean;    // Si está transcribiendo actualmente (opcional)
}
```

**Propósito**: Representar cada mensaje del chat con toda su información asociada.

---

## 🔧 Variables de Estado del Componente

### Estado de Conexión
```typescript
isConnected: boolean = false;           // Si hay conexión activa con Azure
isConnecting: boolean = false;          // Si está en proceso de conexión
connectionStatusText: string = 'Desconectado'; // Texto del estado de conexión
```

### WebSocket
```typescript
private ws: WebSocket | null = null;    // Instancia de WebSocket
private wsUrl: string = '';             // URL completa del WebSocket
```

### Mensajes
```typescript
messages: ChatMessage[] = [];           // Array de mensajes del chat
messageText: string = '';               // Texto del input del usuario
isAssistantThinking: boolean = false;   // Si el asistente está procesando
```

### Audio y Grabación
```typescript
isRecording: boolean = false;           // Si está grabando (legacy)
isMuted: boolean = false;               // Si el micrófono está silenciado
isListeningMode: boolean = false;       // Si está en modo escucha continua
recordingDuration: number = 0;          // Duración en segundos de la grabación
private recordingInterval: any = null;  // Interval para contar segundos
private audioContext: AudioContext | null = null;      // Contexto de audio Web Audio API
private audioStream: MediaStream | null = null;        // Stream del micrófono
private audioWorkletNode: AudioWorkletNode | null = null; // Nodo procesador de audio
private hasAudioBeenSent: boolean = false; // Flag para validar si se envió audio
```

### VAD (Voice Activity Detection)
```typescript
vadActive: boolean = false;             // Si el VAD detectó habla
private vadAnalyser: AnalyserNode | null = null;       // Analizador de audio (unused)
private vadCheckInterval: any = null;   // Interval para chequeo VAD (unused)
private vadThreshold: number = -50;     // Umbral en dB para detectar voz (unused)
```
**Nota**: El VAD se maneja del lado del servidor (server_vad), las variables locales están presentes pero no se usan.

### Control de Reproducción
```typescript
isAssistantSpeaking: boolean = false;   // Si el asistente está "hablando" (procesando respuesta)
isPlayingAudio: boolean = false;        // Si hay audio reproduciéndose
currentPlayingMessageId: string | null = null; // ID del mensaje que se está reproduciendo
private currentAudioSource: AudioBufferSourceNode | null = null; // Fuente de audio actual
```

### Mapeo de Audio y Tracking
```typescript
private audioBuffersByMessage: Map<string, string[]> = new Map(); // Buffers de audio por mensaje
private currentResponseId: string | null = null;         // ID de la respuesta actual
private currentAssistantMessageId: string | null = null; // ID del mensaje del asistente actual
private currentUserMessageId: string | null = null;      // ID del mensaje del usuario actual
```

### Sistema de Ping-Pong y Reconexión
```typescript
private pingInterval: any = null;                // Interval para enviar pings periódicos
private pongTimeout: any = null;                 // Timeout para esperar pong
private readonly PING_INTERVAL_MS = 25000;      // Ping cada 25 segundos
private readonly PONG_TIMEOUT_MS = 10000;       // Esperar pong máximo 10 segundos
private reconnectAttempts: number = 0;           // Contador de intentos de reconexión
private readonly MAX_RECONNECT_ATTEMPTS = 5;    // Máximo 5 intentos de reconexión
private isReconnecting: boolean = false;         // Si está en proceso de reconexión
connectionLatency: number | null = null;         // Latencia en ms (público para UI)
private lastPingTime: number = 0;                // Timestamp del último ping enviado
```

**Propósito**: Mantener la conexión WebSocket activa y detectar desconexiones tempranamente. Implementa reconexión automática con backoff exponencial.

---

## 🔄 Ciclo de Vida del Componente

### `ngOnInit()`
Se ejecuta al inicializar el componente:
1. Llama a `connectToRealtime()` para establecer la conexión WebSocket

### `ngAfterViewInit()`
Se ejecuta después de inicializar la vista:
1. Hace scroll al final del chat con un delay

### `ngOnDestroy()`
Se ejecuta al destruir el componente:
1. Llama a `stopPingPong()` para detener el sistema de ping-pong
2. Llama a `disconnect()` para cerrar el WebSocket
3. Llama a `stopListening()` para detener el micrófono
4. Detiene todos los tracks del `audioStream`

---

## 🌐 Funciones de Conexión

### `connectToRealtime()`
Establece la conexión con Azure OpenAI Realtime API.

**Flujo**:
1. Cambia estado a `isConnecting = true`
2. Obtiene credenciales del backend: `GET /api/credentials/realtime`
3. Construye la URL del WebSocket:
   ```
   wss://<hostname>/openai/realtime?api-version=2025-08-28&deployment=<deployment>&api-key=<key>
   ```
   **Nota**: Usa la versión de API `2025-08-28` que es la más reciente y estable (NO preview). La versión anterior `2024-10-01-preview` fue retirada.
4. Crea la conexión WebSocket
5. Configura event listeners:
   - `onopen`: Llama a `sendSessionConfig()` y `startPingPong()`
   - `onmessage`: Llama a `handleRealtimeMessage()`
   - `onerror`: Registra errores y actualiza estado
   - `onclose`: Actualiza estado de desconexión e intenta reconexión automática si no fue cierre intencional

**Manejo de Errores**: Captura excepciones y actualiza `connectionStatusText`

---

### `sendSessionConfig()`
Envía la configuración inicial de la sesión a Azure OpenAI.

**Configuración Enviada**:
```json
{
  "type": "session.update",
  "session": {
    "modalities": ["text", "audio"],
    "instructions": "Eres un asistente útil y amigable...",
    "voice": "alloy",
    "input_audio_format": "pcm16",
    "output_audio_format": "pcm16",
    "input_audio_transcription": {
      "model": "whisper-1"
    },
    "turn_detection": {
      "type": "server_vad",
      "threshold": 0.5,
      "prefix_padding_ms": 300,
      "silence_duration_ms": 500
    }
  }
}
```

**Parámetros Clave**:
- `deployment`: **gpt-realtime** (configurado en Azure, API version 2024-10-01-preview)
- `modalities`: Soporta texto y audio
- `voice`: Voz del asistente (alloy, echo, shimmer, etc.)
- `input_audio_format` / `output_audio_format`: PCM16 (16-bit PCM)
- `input_audio_transcription`: Usa Whisper para transcribir entrada
- `turn_detection`: VAD del servidor con umbral 0.5, silencio de 500ms

---

### `disconnect()`
Cierra la conexión WebSocket de forma segura.

**Flujo**:
1. Detiene el sistema de ping-pong con `stopPingPong()`
2. Cierra el WebSocket si existe
3. Resetea la variable `ws` a null
4. Limpia `connectionLatency`

---

## 🏓 Sistema de Ping-Pong y Reconexión Automática

### `startPingPong()`
Inicia el sistema de ping-pong para mantener la conexión activa.

**Flujo**:
1. Detiene cualquier ping-pong anterior con `stopPingPong()`
2. Inicia un `setInterval` que ejecuta `sendPing()` cada 25 segundos
3. Registra en consola el inicio del sistema

**Propósito**: Prevenir timeouts de conexión por inactividad y detectar desconexiones tempranamente.

---

### `stopPingPong()`
Detiene el sistema de ping-pong.

**Flujo**:
1. Limpia el `pingInterval` si existe
2. Limpia el `pongTimeout` si existe
3. Registra en consola la detención del sistema

---

### `sendPing()`
Envía un mensaje ping al servidor para verificar conexión.

**Flujo**:
1. Valida que el WebSocket esté abierto
2. Omite el ping si hay actividad activa (`isListeningMode` o `isPlayingAudio`)
3. Guarda el timestamp actual en `lastPingTime`
4. Envía mensaje JSON: `{ type: 'ping' }`
5. Inicia un timeout de 10 segundos esperando el `pong`
6. Si no se recibe pong, llama a `handlePongTimeout()`

**Manejo de Errores**: Si falla el envío, llama a `handlePongTimeout()`

---

### `handlePong()`
Procesa la respuesta pong del servidor.

**Flujo**:
1. Calcula latencia: `Date.now() - lastPingTime`
2. Actualiza `connectionLatency` (visible en UI)
3. Cancela el `pongTimeout`
4. Registra latencia en consola
5. Fuerza actualización de UI con `detectChanges()`

---

### `handlePongTimeout()`
Maneja el caso cuando no se recibe pong a tiempo.

**Flujo**:
1. Registra error en consola
2. Limpia el `pongTimeout`
3. Llama a `disconnect()` para cerrar conexión
4. Llama a `attemptReconnection()` para reintentar

**Indicador**: La conexión está inactiva o perdida.

---

### `attemptReconnection()`
Intenta reconectar automáticamente con backoff exponencial.

**Flujo**:
1. Valida que no esté reconectando y no haya excedido intentos máximos (5)
2. Incrementa `reconnectAttempts`
3. Calcula delay con backoff exponencial: `2^attempts` segundos (máx 30s)
4. Actualiza `connectionStatusText` con intento actual
5. Espera el delay calculado
6. Llama a `connectToRealtime()`
7. Si falla, reintenta recursivamente hasta alcanzar el máximo

**Backoff Exponencial**:
- Intento 1: 2 segundos
- Intento 2: 4 segundos
- Intento 3: 8 segundos
- Intento 4: 16 segundos
- Intento 5: 30 segundos (máximo)

**Al Conectar**: Resetea `reconnectAttempts = 0` para futuras desconexiones.

---

## 📨 Manejo de Mensajes WebSocket

### `handleRealtimeMessage(data: string)`
Procesa todos los mensajes recibidos del servidor OpenAI.

**Eventos Manejados**:

#### 1. `session.created` / `session.updated`
Confirmación de configuración de sesión.

#### 2. `response.created`
Se crea una nueva respuesta:
- Captura `response.id` en `currentResponseId`

#### 3. `response.output_item.added`
Se agrega un nuevo item de salida:
- Si es del asistente, llama a `createAssistantAudioMessage(itemId)`

#### 4. `conversation.item.created`
Se crea un nuevo item en la conversación:
- Si es del asistente: `isAssistantThinking = true`
- Si es del usuario: llama a `createUserAudioMessage(itemId)`

#### 5. `conversation.item.input_audio_transcription.completed`
Transcripción del audio del usuario completada:
- Llama a `updateUserTranscription(itemId, transcript)`

#### 6. `response.audio_transcript.delta`
Fragmento de transcripción del audio de respuesta:
- Llama a `updateAssistantTranscription(delta)`

#### 7. `response.audio_transcript.done`
Transcripción del audio completada:
- Llama a `finalizeAssistantTranscription()`

#### 8. `response.text.delta` / `response.text.done`
Fragmentos o texto completo de respuesta:
- Llama a `appendAssistantMessage()` o `addAssistantMessage()`

#### 9. `response.audio.delta`
Fragmento de audio de respuesta:
- Llama a `storeAudioDelta(delta)` para almacenar

#### 10. `response.audio.done`
Audio completo recibido:
- Llama a `finalizeAudioMessage()` para convertir y reproducir

#### 11. `response.done`
Respuesta completamente procesada:
- Extrae tokens con `updateMessageTokens(usage)`
- Resetea `currentResponseId`
- Limpia `currentAssistantMessageId` después de 100ms

#### 12. `input_audio_buffer.speech_started`
VAD detectó inicio de habla:
- `vadActive = true`

#### 13. `input_audio_buffer.speech_stopped`
VAD detectó fin de habla:
- `vadActive = false`

#### 14. `pong`
Respuesta del servidor al ping:
- Llama a `handlePong()` para calcular latencia
- Cancela timeout de desconexión

#### 15. `error`
Error del servidor:
- Registra error en consola
- `isAssistantThinking = false`

---

## 💬 Funciones de Mensajería de Texto

### `sendTextMessage()`
Envía un mensaje de texto al asistente.

**Flujo**:
1. Valida que hay texto, conexión y WebSocket abierto
2. Agrega mensaje del usuario a la UI con `addUserMessage()`
3. Envía evento `conversation.item.create` al servidor:
   ```json
   {
     "type": "conversation.item.create",
     "item": {
       "type": "message",
       "role": "user",
       "content": [{"type": "input_text", "text": "..."}]
     }
   }
   ```
4. Solicita respuesta con `response.create`
5. Limpia input y activa `isAssistantThinking`

### `addUserMessage(content, type)`
Agrega un mensaje del usuario a la UI.

**Parámetros**:
- `content`: Texto del mensaje
- `type`: 'text' o 'audio'

**Flujo**:
1. Crea objeto `ChatMessage` con ID temporal
2. Agrega al array `messages`
3. Hace scroll al final del chat

### `addAssistantMessage(content)`
Agrega un mensaje del asistente a la UI.

### `appendAssistantMessage(delta)`
Agrega texto incremental al último mensaje del asistente.

---

## 🎤 Funciones de Audio en Tiempo Real

### `startListening()`
Inicia el modo de escucha continua con streaming de audio.

**Flujo**:
1. Valida conexión y que no esté en modo escucha o asistente hablando
2. Solicita acceso al micrófono con `getUserMedia()`:
   - `echoCancellation: true`
   - `noiseSuppression: true`
   - `sampleRate: 24000` (24kHz)
   - `channelCount: 1` (mono)
3. Crea `AudioContext` a 24kHz
4. Crea fuente de audio desde el stream
5. Agrega `AudioWorklet` con código del procesador
6. Conecta: `source → audioWorkletNode → destination`
7. Configura listener `port.onmessage` para recibir buffers de audio
8. En cada mensaje:
   - Convierte Float32 a PCM16 con `floatToPCM16()`
   - Convierte a Base64 con `arrayBufferToBase64()`
   - Envía al servidor: `input_audio_buffer.append`
   - Marca `hasAudioBeenSent = true` en el primer envío
9. Activa `isListeningMode = true`
10. Inicia contador de duración

**AudioWorklet Processor**:
- Buffer de 4800 samples (200ms a 24kHz)
- Acumula samples hasta llenar el buffer
- Envía buffer completo al thread principal

### `floatToPCM16(float32Array)`
Convierte audio Float32 [-1, 1] a PCM16 [-32768, 32767].

**Algoritmo**:
```typescript
const s = Math.max(-1, Math.min(1, sample)); // Clamp
pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
```

### `arrayBufferToBase64(buffer)`
Convierte ArrayBuffer a string Base64 para transmisión.

---

### `toggleMute()`
Alterna entre silenciado y activo.

**Efecto**:
- Cambia `isMuted`
- Cuando está silenciado, el listener en `AudioWorklet.onmessage` no envía audio al servidor

---

### `stopListening()`
Detiene el modo de escucha continua.

**Flujo**:
1. Valida que esté en modo escucha
2. Silencia inmediatamente: `isMuted = true`
3. Desconecta y limpia `audioWorkletNode`
4. Detiene todos los tracks del `audioStream`
5. Cierra el `audioContext`
6. Detiene el `recordingInterval`
7. Resetea estados: `isListeningMode`, `isMuted`, `recordingDuration`
8. **NO detiene la reproducción de audio del asistente**
9. Valida estado del buffer:
   - Si `hasAudioBeenSent && vadActive`: Hace `commit` y solicita respuesta
   - Sino: Solo hace `clear` del buffer

**Importante**: El VAD debe estar activo para confirmar que hubo habla real y evitar el error `input_audio_buffer_commit_empty`.

---

## 🎵 Funciones de Audio del Asistente

### `createAssistantAudioMessage(itemId)`
Crea un mensaje de audio del asistente en la UI.

**Flujo**:
1. Crea objeto `ChatMessage` con:
   - `id = itemId` (del servidor)
   - `type = 'audio'`
   - `isTranscribing = true`
   - `transcription = ''`
2. Agrega al array `messages`
3. Guarda `itemId` en `currentAssistantMessageId`
4. Inicializa array vacío en `audioBuffersByMessage.set(itemId, [])`

### `storeAudioDelta(audioBase64)`
Almacena fragmentos de audio recibidos del servidor.

**Flujo**:
1. Valida que exista `currentAssistantMessageId`
2. Marca `isAssistantSpeaking = true` (pausa escucha)
3. Agrega el fragmento base64 al array en `audioBuffersByMessage`

### `finalizeAudioMessage()`
Finaliza el audio del asistente y lo reproduce automáticamente.

**Flujo**:
1. Obtiene el mensaje y los buffers almacenados
2. Si hay buffers:
   - Convierte array de base64 a Blob con `base64ArrayToBlob()`
   - Asigna el blob al mensaje: `message.audioBlob = audioBlob`
   - Después de 100ms, llama a `playAudio(message)`
3. Si NO hay buffers:
   - Después de 500ms, reactiva escucha: `isAssistantSpeaking = false`

### `base64ArrayToBlob(base64Array)`
Convierte array de strings base64 a un Blob de audio PCM16.

**Algoritmo**:
1. Decodifica cada string base64 a binario
2. Calcula longitud total
3. Crea `Uint8Array` del tamaño total
4. Copia todos los datos concatenados
5. Retorna `Blob` con tipo `audio/pcm`

---

### `playAudio(message)`
Reproduce el audio de un mensaje.

**Flujo**:
1. Valida que tenga `audioBlob` y no haya audio reproduciéndose
2. Marca estados:
   - `isPlayingAudio = true`
   - `isAssistantSpeaking = true`
   - `currentPlayingMessageId = message.id`
3. Crea `AudioContext` a 24kHz
4. Lee el blob con `FileReader`
5. Convierte PCM16 a `AudioBuffer` con `pcm16ToAudioBuffer()`
6. Crea `AudioBufferSourceNode`
7. Conecta: `source → destination`
8. Configura `onended`:
   - Espera 500ms (anti-loop)
   - Resetea estados: `isPlayingAudio`, `isAssistantSpeaking`, `currentPlayingMessageId`, `vadActive`, `hasAudioBeenSent`
9. Inicia reproducción: `source.start(0)`

### `pcm16ToAudioBuffer(arrayBuffer, audioContext)`
Convierte ArrayBuffer PCM16 a AudioBuffer para reproducción.

**Algoritmo**:
1. Crea `Int16Array` del buffer
2. Crea `Float32Array` del mismo tamaño
3. Normaliza: `float32[i] = int16[i] / 32768.0`
4. Crea `AudioBuffer` de 1 canal a 24kHz
5. Copia datos normalizados al buffer
6. Retorna `AudioBuffer`

---

### `stopAudio()`
Detiene la reproducción de audio manualmente.

**Flujo**:
1. Si hay `currentAudioSource`, lo detiene con `stop()`
2. Limpia `currentAudioSource`
3. Espera 500ms (anti-loop)
4. Resetea estados: `isPlayingAudio`, `isAssistantSpeaking`, `currentPlayingMessageId`, `vadActive`, `hasAudioBeenSent`

---

## 📝 Funciones de Transcripción

### `createUserAudioMessage(itemId)`
Crea o actualiza el mensaje de audio del usuario.

**Flujo**:
1. Busca mensaje temporal del usuario (sin ID del servidor)
2. Si existe:
   - Actualiza `id` con el del servidor
   - Marca `isTranscribing = true`
   - Guarda en `currentUserMessageId`
3. Si NO existe:
   - Crea nuevo mensaje con `type = 'audio'`
   - `content = '🎤 Mensaje de voz'`
   - `isTranscribing = true`

### `updateUserTranscription(itemId, transcript)`
Actualiza la transcripción del usuario cuando está completa.

**Flujo**:
1. Busca mensaje por `itemId`
2. Actualiza `transcription` y `content` con el texto
3. Marca `isTranscribing = false`

### `updateAssistantTranscription(delta)`
Agrega fragmentos de transcripción del asistente.

**Flujo**:
1. Valida `currentAssistantMessageId`
2. Busca mensaje
3. Inicializa `transcription` si no existe
4. Concatena el `delta`

### `finalizeAssistantTranscription()`
Finaliza la transcripción del asistente.

**Flujo**:
1. Busca mensaje por `currentAssistantMessageId`
2. Marca `isTranscribing = false`
3. Reemplaza `content` con la `transcription` completa

---

## 🪙 Función de Tokens

### `updateMessageTokens(usage)`
Actualiza los tokens utilizados en los mensajes del usuario y asistente.

**Parámetros del objeto `usage`**:
```typescript
{
  input_tokens: number,   // Tokens del usuario (entrada)
  output_tokens: number,  // Tokens del asistente (salida)
  total_tokens: number    // Total (input + output)
}
```

**Flujo**:
1. Extrae `inputTokens`, `outputTokens`, `totalTokens`
2. Si hay `currentUserMessageId` y `inputTokens > 0`:
   - Busca mensaje del usuario
   - Asigna `tokens = inputTokens`
3. Si hay `currentAssistantMessageId` y `outputTokens > 0`:
   - Busca mensaje del asistente
   - Asigna `tokens = outputTokens`
4. Recrea array de mensajes: `this.messages = [...this.messages]`
5. Fuerza 3 ciclos de detección de cambios de Angular:
   - `markForCheck()` + `detectChanges()` inmediato
   - Otro en `setTimeout(0)`
   - Otro en `setTimeout(100)`

**Nota**: La recreación del array y múltiples ciclos de detección son necesarios para que Angular actualice la UI con los badges de tokens.

---

## 🔄 Diagrama de Ciclo de Vida de OpenAI Realtime API

```
┌─────────────────────────────────────────────────────────────────┐
│                    INICIO DE CONEXIÓN                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │   connectToRealtime   │
                  └───────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ GET /api/credentials  │
                  └───────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ WebSocket Connection (wss://) │
              └───────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │    ws.onopen() →      │
                  │  sendSessionConfig()  │
                  └───────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ Envía: session.update         │
              │ - modalities: [text, audio]   │
              │ - voice: alloy                │
              │ - turn_detection: server_vad  │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ Recibe: session.created       │
              └───────────────────────────────┘
                              │
┌─────────────────────────────┴─────────────────────────────┐
│                                                             │
▼                                                             ▼
┌─────────────────────────────────┐    ┌──────────────────────────────────┐
│       FLUJO DE VOZ              │    │      FLUJO DE TEXTO              │
└─────────────────────────────────┘    └──────────────────────────────────┘
              │                                        │
              ▼                                        ▼
  ┌───────────────────────┐              ┌────────────────────────┐
  │   startListening()    │              │   sendTextMessage()    │
  └───────────────────────┘              └────────────────────────┘
              │                                        │
              ▼                                        ▼
  ┌───────────────────────┐              ┌────────────────────────┐
  │ getUserMedia()        │              │ conversation.item      │
  │ - 24kHz, mono         │              │ .create (type: text)   │
  └───────────────────────┘              └────────────────────────┘
              │                                        │
              ▼                                        │
  ┌───────────────────────┐                           │
  │ AudioWorklet          │                           │
  │ - Buffer: 4800        │                           │
  │ - Float32 → PCM16     │                           │
  └───────────────────────┘                           │
              │                                        │
              ▼                                        │
  ┌───────────────────────┐                           │
  │ Streaming continuo:   │                           │
  │ input_audio_buffer    │                           │
  │ .append (cada 200ms)  │                           │
  └───────────────────────┘                           │
              │                                        │
              ▼                                        │
  ┌───────────────────────┐                           │
  │ Server VAD detecta    │                           │
  │ habla (threshold 0.5) │                           │
  └───────────────────────┘                           │
              │                                        │
              ▼                                        │
  ┌───────────────────────┐                           │
  │ Eventos recibidos:    │                           │
  │ - speech_started      │                           │
  │   (vadActive = true)  │                           │
  │ - speech_stopped      │                           │
  │   (vadActive = false) │                           │
  └───────────────────────┘                           │
              │                                        │
              ▼                                        │
  ┌───────────────────────┐                           │
  │   stopListening()     │                           │
  └───────────────────────┘                           │
              │                                        │
              ▼                                        │
  ┌───────────────────────┐                           │
  │ Si vadActive &&       │                           │
  │ hasAudioBeenSent:     │                           │
  │ - buffer.commit       │                           │
  │ - response.create     │                           │
  │                       │                           │
  │ Sino:                 │                           │
  │ - buffer.clear        │                           │
  └───────────────────────┘                           │
              │                                        │
              └───────────────┬────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   PROCESAMIENTO DEL SERVIDOR  │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ Eventos recibidos:            │
              │                               │
              │ 1. response.created           │
              │    (captura response.id)      │
              │                               │
              │ 2. conversation.item.created  │
              │    - role: user               │
              │    → createUserAudioMessage() │
              │                               │
              │ 3. conversation.item          │
              │    .input_audio_transcription │
              │    .completed                 │
              │    → updateUserTranscription()│
              │                               │
              │ 4. response.output_item.added │
              │    - role: assistant          │
              │    → createAssistantAudio     │
              │       Message()               │
              │                               │
              │ 5. response.audio_transcript  │
              │    .delta                     │
              │    → updateAssistant          │
              │       Transcription()         │
              │                               │
              │ 6. response.audio_transcript  │
              │    .done                      │
              │    → finalizeAssistant        │
              │       Transcription()         │
              │                               │
              │ 7. response.audio.delta       │
              │    → storeAudioDelta()        │
              │    (almacena fragmentos)      │
              │                               │
              │ 8. response.audio.done        │
              │    → finalizeAudioMessage()   │
              │    (convierte y reproduce)    │
              │                               │
              │ 9. response.done              │
              │    → updateMessageTokens()    │
              │    (input/output tokens)      │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   REPRODUCCIÓN DE AUDIO       │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ base64ArrayToBlob()           │
              │ → Convierte fragmentos a Blob │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ playAudio()                   │
              │ - isAssistantSpeaking = true  │
              │ - currentPlayingMessageId set │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ pcm16ToAudioBuffer()          │
              │ → Convierte a AudioBuffer     │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ AudioBufferSourceNode.start() │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ source.onended →              │
              │ - Espera 500ms (anti-loop)    │
              │ - isPlayingAudio = false      │
              │ - isAssistantSpeaking = false │
              │ - vadActive = false           │
              │ - currentPlayingMessageId null│
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   LISTO PARA NUEVA INTERACCIÓN│
              └───────────────────────────────┘
```

---

## 🔀 Diagrama de Interacción: Audio ⇄ Texto

```
┌─────────────────────────────────────────────────────────────────┐
│              PÁGINA DEMO-REALTIME (Estado Inicial)              │
│                                                                  │
│  [🎤 Micrófono] [📝 Input de Texto] [📤 Enviar]                │
│                                                                  │
│  isListeningMode = false                                        │
│  isConnected = true                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │                                          │
         ▼                                          ▼
┌─────────────────────┐                  ┌──────────────────────┐
│  USUARIO PRESIONA   │                  │  USUARIO ESCRIBE     │
│  BOTÓN MICRÓFONO 🎤 │                  │  EN INPUT DE TEXTO   │
└─────────────────────┘                  └──────────────────────┘
         │                                          │
         ▼                                          │
┌─────────────────────┐                            │
│ startListening()    │                            │
│ - Solicita permiso  │                            │
│ - Crea AudioWorklet │                            │
│ - isListeningMode   │                            │
│   = true            │                            │
└─────────────────────┘                            │
         │                                          │
         ▼                                          │
┌─────────────────────────────────────┐            │
│   UI CAMBIA A MODO VOZ:             │            │
│                                      │            │
│  [🔴 MUTE] [⏹️ STOP]                │            │
│  Input de Texto: DESHABILITADO      │            │
│  Botón Enviar: DESHABILITADO        │            │
│                                      │            │
│  Indicador:                          │            │
│  🔵 Escuchando... 0s                 │            │
└─────────────────────────────────────┘            │
         │                                          │
         ▼                                          │
┌─────────────────────────────────────┐            │
│ STREAMING DE AUDIO EN TIEMPO REAL   │            │
│                                      │            │
│ Cada 200ms (4800 samples):          │            │
│ - Float32 → PCM16 → Base64          │            │
│ - Envía: input_audio_buffer.append  │            │
│                                      │            │
│ Usuario puede:                       │            │
│ 1. Presionar MUTE (toggleMute)      │            │
│    → isMuted = !isMuted             │            │
│    → Se detiene envío de audio      │            │
│    → Icono cambia: 🔴 ⇄ 🟢         │            │
│                                      │            │
│ 2. Presionar STOP (stopListening)   │            │
│    → Ver flujo abajo                 │            │
└─────────────────────────────────────┘            │
         │                                          │
         ▼                                          │
┌─────────────────────────────────────┐            │
│ USUARIO PRESIONA STOP ⏹️            │            │
└─────────────────────────────────────┘            │
         │                                          │
         ▼                                          │
┌─────────────────────────────────────┐            │
│ stopListening()                     │            │
│                                      │            │
│ 1. isMuted = true (silencia)        │            │
│ 2. Desconecta AudioWorklet          │            │
│ 3. Detiene stream del micrófono     │            │
│ 4. Cierra AudioContext              │            │
│ 5. isListeningMode = false          │            │
│                                      │            │
│ 6. Valida buffer:                   │            │
│    Si vadActive && hasAudioBeenSent:│            │
│      → buffer.commit                │            │
│      → response.create              │            │
│    Sino:                             │            │
│      → buffer.clear (no commit)     │            │
│                                      │            │
│ 7. NO detiene reproducción de audio │            │
│    del asistente si está activa     │            │
└─────────────────────────────────────┘            │
         │                                          │
         ▼                                          │
┌─────────────────────────────────────┐            │
│   UI REGRESA A MODO TEXTO:          │            │
│                                      │            │
│  [🎤 Micrófono] [📝 Input] [📤]    │◄───────────┘
│  Input de Texto: HABILITADO         │
│  Botón Enviar: HABILITADO           │
│                                      │
│  Usuario puede:                      │
│  1. Escribir mensaje y enviar       │
│     → sendTextMessage()             │
│  2. Presionar micrófono de nuevo    │
│     → startListening()              │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ RESPUESTA DEL ASISTENTE             │
│                                      │
│ - Audio se reproduce automáticamente│
│ - Durante reproducción:              │
│   * isAssistantSpeaking = true      │
│   * No se puede iniciar escucha     │
│   * startListening() está bloqueado │
│                                      │
│ - Al terminar reproducción:          │
│   * isAssistantSpeaking = false     │
│   * Se puede volver a usar micrófono│
└─────────────────────────────────────┘
```

---

## 🎛️ Flujo Detallado: Mute y Stop

### BOTÓN MUTE (Solo en modo escucha)

```
┌─────────────────────────────────────┐
│ Estado: isListeningMode = true      │
│         isMuted = false             │
│         Audio streaming activo      │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Usuario presiona MUTE 🔴            │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ toggleMute()                        │
│ → isMuted = true                    │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Efecto:                             │
│ - AudioWorklet sigue capturando     │
│ - Listener en onmessage chequea:    │
│   if (!isMuted && ...) {            │
│     // envía audio                  │
│   }                                  │
│ - NO se envía audio al servidor     │
│ - Icono cambia a 🔴                 │
│ - Color cambia a warning            │
│ - Indicador: "Silenciado"           │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Usuario presiona MUTE de nuevo      │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ toggleMute()                        │
│ → isMuted = false                   │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Efecto:                             │
│ - Listener vuelve a enviar audio    │
│ - Icono cambia a 🟢                 │
│ - Color cambia a success            │
│ - Indicador: "Escuchando..."        │
└─────────────────────────────────────┘
```

---

### BOTÓN STOP GENERAL (Solo en modo escucha)

```
┌─────────────────────────────────────┐
│ Estado: isListeningMode = true      │
│         Audio streaming activo      │
│         (puede estar en mute o no)  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Usuario presiona STOP ⏹️            │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ stopListening()                     │
│                                      │
│ Paso 1: Detener captura de audio    │
│ - isMuted = true (silencia)         │
│ - audioWorkletNode.disconnect()     │
│ - audioStream.getTracks().stop()    │
│ - audioContext.close()              │
│ - clearInterval(recordingInterval)  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Paso 2: Resetear estados            │
│ - isListeningMode = false           │
│ - isMuted = false                   │
│ - recordingDuration = 0             │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Paso 3: Validar buffer de audio     │
│                                      │
│ ¿hasAudioBeenSent && vadActive?     │
└─────────────────────────────────────┘
         │
    ┌────┴────┐
    │         │
   SÍ        NO
    │         │
    ▼         ▼
┌───────┐ ┌────────┐
│COMMIT │ │ CLEAR  │
└───────┘ └────────┘
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ Envía:  │ │ Envía:       │
│ buffer  │ │ buffer.clear │
│ .commit │ │              │
│         │ │ (sin commit) │
│ response│ │              │
│ .create │ │              │
└─────────┘ └──────────────┘
    │         │
    └────┬────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Paso 4: UI regresa a modo texto     │
│                                      │
│ Botones visibles:                    │
│ - [🎤 Micrófono] habilitado         │
│ - [📝 Input] habilitado             │
│ - [📤 Enviar] habilitado            │
│                                      │
│ Indicador de escucha: OCULTO        │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ IMPORTANTE:                          │
│                                      │
│ Si hay audio del asistente           │
│ reproduciéndose:                     │
│                                      │
│ - isPlayingAudio = true              │
│ - currentPlayingMessageId != null   │
│ - Reproducción NO se detiene        │
│ - Audio sigue hasta terminar        │
│                                      │
│ Usuario puede:                       │
│ - Detener audio con botón Stop      │
│   individual del mensaje             │
│ - Escribir texto mientras se         │
│   reproduce                          │
│ - NO puede iniciar micrófono hasta   │
│   que termine el audio              │
└─────────────────────────────────────┘
```

---

## 🎮 Controles de Reproducción Individual

```
┌─────────────────────────────────────┐
│ Mensaje de audio del asistente      │
│ con audioBlob disponible             │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Estado inicial:                      │
│ - isPlayingAudio = false            │
│ - currentPlayingMessageId = null    │
│                                      │
│ UI muestra:                          │
│ [▶️ Reproducir] habilitado          │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Usuario presiona [▶️ Reproducir]    │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ playAudio(message)                  │
│                                      │
│ - isPlayingAudio = true             │
│ - isAssistantSpeaking = true        │
│ - currentPlayingMessageId = msg.id  │
│                                      │
│ Convierte PCM16 → AudioBuffer       │
│ Reproduce con AudioBufferSourceNode │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ UI de ESTE mensaje cambia a:        │
│ [⏹️ Detener] habilitado             │
│                                      │
│ Otros mensajes con audio:            │
│ [▶️ Reproducir] DESHABILITADO       │
│ (disabled=true porque isPlayingAudio│
│  está activo)                        │
└─────────────────────────────────────┘
         │
    ┌────┴────┐
    │         │
 OPCIÓN A  OPCIÓN B
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ Audio   │ │ Usuario      │
│ termina │ │ presiona Stop│
│ solo    │ │              │
└─────────┘ └──────────────┘
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│onended()│ │ stopAudio()  │
└─────────┘ └──────────────┘
    │         │
    └────┬────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Espera 500ms (anti-loop)            │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Resetea estados:                     │
│ - isPlayingAudio = false            │
│ - isAssistantSpeaking = false       │
│ - currentPlayingMessageId = null    │
│ - vadActive = false                 │
│ - hasAudioBeenSent = false          │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ UI vuelve al estado inicial:        │
│                                      │
│ Todos los mensajes con audio:       │
│ [▶️ Reproducir] habilitado          │
│                                      │
│ Botón micrófono: habilitado         │
│ (si no hay isAssistantSpeaking)     │
└─────────────────────────────────────┘
```

---

## 🏓 Diagrama del Sistema de Ping-Pong

```
┌─────────────────────────────────────────────────────────────────┐
│                  SISTEMA DE PING-PONG ACTIVO                     │
│                (Mantiene conexión WebSocket viva)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Cada 25 segundos (PING_INTERVAL)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────┐
│ ¿Hay actividad activa?              │
│ (isListeningMode || isPlayingAudio) │
└─────────────────────────────────────┘
         │                    │
    SÍ   │                    │  NO
         ▼                    ▼
┌─────────────────┐  ┌─────────────────────┐
│ OMITIR PING     │  │ ENVIAR PING         │
│ (no interferir) │  │                     │
└─────────────────┘  └─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ sendPing()                                                       │
│ 1. lastPingTime = Date.now()                                    │
│ 2. ws.send({ type: 'ping' })                                    │
│ 3. Inicia timeout de 10 segundos (PONG_TIMEOUT)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│   PONG RECIBIDO         │       │   TIMEOUT (10s)         │
│   (antes de 10s)        │       │   (no hay pong)         │
└─────────────────────────┘       └─────────────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│ handlePong()            │       │ handlePongTimeout()     │
│ - Calcula latencia      │       │ - Registra error        │
│ - Cancela timeout       │       │ - disconnect()          │
│ - Actualiza UI          │       │ - attemptReconnection() │
│ - connectionLatency     │       └─────────────────────────┘
│   visible               │                   │
└─────────────────────────┘                   │
              │                               ▼
              │                   ┌─────────────────────────┐
              │                   │ RECONEXIÓN AUTOMÁTICA   │
              │                   └─────────────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CONEXIÓN SALUDABLE                             │
│              (Ping-Pong continúa cada 25s)                       │
└─────────────────────────────────────────────────────────────────┘
```

### Reconexión Automática con Backoff Exponencial

```
┌─────────────────────────────────────┐
│ DESCONEXIÓN DETECTADA               │
│ (Error, Timeout, Cierre inesperado) │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ ¿reconnectAttempts < 5?             │
└─────────────────────────────────────┘
         │           │
    NO   │           │  SÍ
         ▼           ▼
┌───────────────┐  ┌──────────────────────────┐
│ FALLAR        │  │ attemptReconnection()    │
│ "Reconexión   │  │                          │
│  fallida"     │  │ 1. reconnectAttempts++   │
└───────────────┘  │ 2. delay = 2^attempts s  │
                   │ 3. Esperar delay         │
                   │ 4. connectToRealtime()   │
                   └──────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
         ÉXITO│                           │FALLO
              ▼                           ▼
┌──────────────────────────┐  ┌────────────────────────┐
│ CONECTADO                │  │ Reintentar             │
│ - reconnectAttempts = 0  │  │ (si attempts < 5)      │
│ - startPingPong()        │  └────────────────────────┘
│ - connectionLatency null │              │
└──────────────────────────┘              │
              │                           │
              └───────────────┬───────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │  Backoff Exponencial:     │
              │  Intento 1: 2s            │
              │  Intento 2: 4s            │
              │  Intento 3: 8s            │
              │  Intento 4: 16s           │
              │  Intento 5: 30s (máx)     │
              └───────────────────────────┘
```

---

## 🔧 Herramientas de Desarrollo

### Angular Change Detection
Para actualizar tokens en la UI, se usa una estrategia agresiva:
1. Recrear array: `this.messages = [...this.messages]`
2. `cdr.markForCheck()` + `cdr.detectChanges()` (inmediato)
3. Repetir en `setTimeout(0)` y `setTimeout(100)`

Esto fuerza a Angular a detectar los cambios en objetos dentro del array.

---

## 📊 Monitoreo y Logs

### Logs Esenciales Activos
- `console.log('📦 response.done completo:', message)` - Muestra objeto completo con usage
- `console.error('❌ Error del servidor:', message.error)` - Errores del servidor OpenAI
- `console.error('❌ Error WebSocket:', error)` - Errores de conexión
- `console.log('✅ Conectado a Azure OpenAI Realtime API')` - Conexión exitosa
- `console.log('🔌 Desconectado de Azure OpenAI Realtime API')` - Desconexión
- `console.log('🏓 Sistema de ping-pong iniciado/detenido')` - Estado del ping-pong
- `console.log('🏓 Ping enviado')` - Cada ping enviado
- `console.log('🏓 Pong recibido - Latencia: Xms')` - Pong con latencia calculada
- `console.error('❌ No se recibió pong - conexión perdida')` - Timeout de pong
- `console.log('🔄 Intento de reconexión X/5 en Yms')` - Intentos de reconexión

---

## 🐛 Validaciones y Manejo de Errores

### Prevención de `input_audio_buffer_commit_empty`
```typescript
if (this.hasAudioBeenSent && this.vadActive) {
  // Commit solo si hubo audio Y el VAD detectó habla real
  this.ws.send(JSON.stringify({ type: 'input_audio_buffer.commit' }));
  this.ws.send(JSON.stringify({ type: 'response.create' }));
} else {
  // Solo limpiar buffer si no cumple las condiciones
  this.ws.send(JSON.stringify({ type: 'input_audio_buffer.clear' }));
}
```

### Anti-Loop en Reproducción
Delay de 500ms antes de resetear estados después de reproducción para evitar que el asistente se escuche a sí mismo.

---

## 🎨 Estilos y UX

- **WhatsApp-style**: Mensajes del usuario a la derecha (color primary), asistente a la izquierda (color light)
- **Modo Oscuro**: Soportado nativamente por variables CSS de Ionic
- **Indicadores visuales**:
  - 🟢 Escuchando (success)
  - 🔴 Silenciado (warning)
  - ⚫ Asistente hablando (medium)
- **Badges de tokens**: Con icono ⚡ flash
- **Botones disabled**: Input y enviar deshabilitados en modo voz

---

## 🔐 Seguridad

- API Key nunca expuesta en el cliente (se obtiene del backend)
- WebSocket con WSS (encrypted)
- Validación de estados antes de acciones críticas

---

## 📝 Notas Técnicas

### Formato de Audio
- **Entrada**: PCM16 mono 24kHz
- **Salida**: PCM16 mono 24kHz
- **Streaming**: Buffers de 200ms (4800 samples)

### Transcripción
- **Modelo**: Whisper-1
- **En tiempo real**: Fragmentos incrementales con `.delta`, finalizado con `.done`

### VAD (Voice Activity Detection)
- **Tipo**: Server-side (OpenAI maneja detección)
- **Threshold**: 0.5 (balance entre sensibilidad y falsos positivos)
- **Silence duration**: 500ms antes de considerar fin de habla

### Sistema de Ping-Pong
- **Intervalo de ping**: 25 segundos (mantiene conexión activa)
- **Timeout de pong**: 10 segundos (detecta desconexión)
- **Omite pings**: Durante streaming de audio o reproducción (evita interferencias)
- **Latencia**: Calculada y visible en UI (ms entre ping y pong)
- **Reconexión**: Automática con backoff exponencial (hasta 5 intentos)
- **Backoff**: 2, 4, 8, 16, 30 segundos progresivamente
- **API Version**: 2025-08-28 (estable)

---

## 🚀 Próximas Mejoras Potenciales

1. **Persistencia**: Guardar conversaciones en localStorage o backend
2. ✅ **Reconexión automática**: Sistema de ping-pong implementado con reconexión automática y backoff exponencial
3. **Configuración de voz**: Permitir seleccionar entre diferentes voces (alloy, echo, shimmer)
4. **Historial de tokens**: Acumulado total de tokens por sesión
5. **Exportar conversación**: Descargar chat como texto o JSON
6. **Soporte multi-idioma**: Detección automática de idioma del usuario
7. **Compresión de audio**: Usar formato más eficiente que PCM16
8. **Streaming de texto**: Mostrar texto del asistente mientras se genera (no solo audio)
9. **Indicador de latencia**: Mostrar latencia de conexión en UI con código de colores
10. **Métricas de reconexión**: Dashboard de estadísticas de conexión y reconexiones

---

## 📚 Referencias

- [Azure OpenAI Realtime API Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/realtime-audio-quickstart)
- [Azure OpenAI API Version Lifecycle](https://learn.microsoft.com/en-us/azure/ai-services/openai/api-version-deprecation)
- [Supported Models - gpt-realtime](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/models#audio-models)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet)
- [Ionic Framework](https://ionicframework.com/docs)
- [Angular Change Detection](https://angular.dev/guide/signals)

---

**Autor**: Ezequiel Baltodano  
**Fecha**: 6 de octubre de 2025  
**Versión**: 1.0.0
