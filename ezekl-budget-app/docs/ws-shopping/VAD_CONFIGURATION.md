# 🎤 Configuración del Sistema VAD (Voice Activity Detection)

## ✅ Sistema VAD Implementado

El sistema de **detección de actividad de voz (VAD)** permite **interrumpir automáticamente al bot** cuando el usuario habla mientras el asistente está reproduciendo su respuesta.

## 🔧 Cómo Funciona

### Flujo de Detección VAD

```
Usuario habla mientras bot responde
         ↓
Micrófono captura audio continuamente
         ↓
Análisis de nivel de audio (0-255)
         ↓
¿Nivel > energyThreshold (40)?
         ↓ SI
Incrementa frames consecutivos
         ↓
¿consecutiveFrames >= 3?
         ↓ SI
✅ VOZ DETECTADA - Interrumpe al bot
         ↓
• Detiene audio del bot
• Cambia a estado LISTENING
• Inicia grabación del usuario
```

## ⚙️ Configuración

Edita el archivo: [audio.config.ts](../../src/app/shared/config/audio.config.ts)

```typescript
vad: {
  enabled: true,
  
  // Umbral de energía para considerar que hay voz (0-255)
  // Valor más bajo = más sensible
  // Valor más alto = menos sensible
  energyThreshold: 40,
  
  // Número de frames consecutivos con voz para activar
  // Valor más bajo = reacciona más rápido (puede tener falsos positivos)
  // Valor más alto = más confiable (puede ser lento)
  consecutiveFrames: 3
}
```

## 📊 Ajustes Recomendados por Escenario

### 🔊 Ambiente Ruidoso
```typescript
vad: {
  energyThreshold: 60,    // Más alto para ignorar ruido
  consecutiveFrames: 5    // Más frames para confirmar
}
```

### 🤫 Ambiente Silencioso
```typescript
vad: {
  energyThreshold: 30,    // Más sensible
  consecutiveFrames: 2    // Reacciona más rápido
}
```

### ⚡ Interrupción Rápida (Puede tener falsos positivos)
```typescript
vad: {
  energyThreshold: 35,
  consecutiveFrames: 1    // Interrupción instantánea
}
```

### 🎯 Balance Óptimo (Recomendado)
```typescript
vad: {
  energyThreshold: 40,    // Balance entre sensibilidad y confiabilidad
  consecutiveFrames: 3    // Confirmación rápida pero confiable
}
```

## 🐛 Solución de Problemas

### Problema: El bot se interrumpe con ruidos de fondo

**Solución**: Aumentar `energyThreshold` y/o `consecutiveFrames`

```typescript
vad: {
  energyThreshold: 50,    // ↑ Aumentar
  consecutiveFrames: 5    // ↑ Aumentar
}
```

### Problema: No puedo interrumpir al bot cuando hablo

**Solución**: Disminuir `energyThreshold` y/o `consecutiveFrames`

```typescript
vad: {
  energyThreshold: 30,    // ↓ Disminuir
  consecutiveFrames: 2    // ↓ Disminuir
}
```

### Problema: El bot se interrumpe al principio de cada respuesta

**Causa**: El audio del bot se está capturando por el micrófono

**Soluciones**:
1. **Usar audífonos** (recomendado)
2. **Aumentar umbral**:
   ```typescript
   vad: {
     energyThreshold: 50,
     consecutiveFrames: 4
   }
   ```
3. **Verificar configuración de micrófono**:
   ```typescript
   microphone: {
     echoCancellation: true,  // ✅ Debe estar en true
     noiseSuppression: true   // ✅ Debe estar en true
   }
   ```

## 📈 Monitoreo en Tiempo Real

### Ver nivel de audio en consola

El sistema registra automáticamente:

```
🎤 VAD continuo activado (umbral: 40, frames: 3)
🎤 VAD: Voz detectada (nivel 65) mientras bot habla - Interrumpiendo...
🛑 VAD: Usuario interrumpiendo al bot
```

### Visualización en UI

La barra de progreso en la interfaz muestra el **nivel de audio en tiempo real** (0-255):

- **Verde** (0-85): Silencio/ruido bajo
- **Amarillo** (86-170): Audio medio
- **Rojo** (171-255): Audio alto (voz detectada)

## 🔬 Pruebas

### Test Manual

1. **Iniciar conversación**
2. **Esperar a que el bot responda**
3. **Hablar mientras el bot está hablando**
4. **Verificar que se interrumpa automáticamente**

### Consola del navegador

```javascript
// Ver nivel de audio actual
audioLevel = 0; // Se actualiza en tiempo real

// Ver si se detectó voz
console.log('Voz detectada:', audioRecorder.hasVoiceDetected);
```

## 📝 Logs de Depuración

### En el servicio AudioRecorderService

```typescript
// Cuando se activa VAD
🎤 VAD continuo activado (umbral: 40, frames: 3)

// Cuando se desactiva
🎤 VAD continuo desactivado
```

### En el componente VoiceShoppingPage

```typescript
// Cuando se detecta voz durante bot speaking
🎤 VAD: Voz detectada (nivel 65) mientras bot habla - Interrumpiendo...

// Cuando se interrumpe
🛑 VAD: Usuario interrumpiendo al bot

// Mensaje al usuario
⚡ Has interrumpido al asistente. Habla ahora...
```

## 🎯 Mejores Prácticas

1. **Usar audífonos**: Evita que el micrófono capture el audio del bot
2. **Ambiente controlado**: Minimizar ruido de fondo
3. **Probar configuración**: Ajustar según tu ambiente específico
4. **Monitorear logs**: Revisar la consola para ver comportamiento
5. **Iteración gradual**: Cambiar un parámetro a la vez

## 🔄 Ciclo de Vida del VAD

```typescript
// 1. Al iniciar conversación
async startConversation() {
  await this.audioRecorder.initialize();
  this.audioRecorder.startContinuousVAD(); // ✅ VAD activado
}

// 2. Durante la conversación
// VAD monitorea continuamente, incluso cuando el bot habla

// 3. Al detectar voz mientras bot habla
private subscribeToAudioRecorder() {
  if (this.conversationState === ConversationState.SPEAKING && 
      this.audioRecorder.hasVoiceDetected) {
    this.interruptBot(); // ✅ Interrupción automática
  }
}

// 4. Al finalizar conversación
stopConversation() {
  this.audioRecorder.cleanup(); // Detiene VAD automáticamente
}
```

## 🆘 Soporte

Si el VAD no funciona correctamente:

1. **Verificar permisos de micrófono**
2. **Revisar consola del navegador** para errores
3. **Probar con diferentes umbrales** (30-60)
4. **Usar audífonos** para evitar eco
5. **Verificar que `vad.enabled` sea `true`**

## 📚 Referencias

- [Web Audio API - AnalyserNode](https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode)
- [MediaRecorder API](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)
- [Voice Activity Detection (Wikipedia)](https://en.wikipedia.org/wiki/Voice_activity_detection)

---

**Última actualización**: 13 de enero de 2026
