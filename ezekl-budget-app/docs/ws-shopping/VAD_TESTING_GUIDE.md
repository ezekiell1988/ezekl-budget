# 🧪 Guía de Prueba - Sistema VAD

## ✅ Preparación

### 1. Verificar que el Backend esté corriendo
```bash
cd /Users/ezequielbaltodanocubillo/Documents/clickeat/voice-bot
source env/bin/activate
python start.py
```

**Debe mostrar:**
```
🚀 Servidor corriendo en http://localhost:8880
```

### 2. Iniciar la aplicación Angular
```bash
cd voice-bot-app
npm start
```

**Navegar a:**
```
http://localhost:8100/voice-shopping
```

## 🎯 Pruebas de Funcionalidad VAD

### Test 1: Interrupción Básica ✅

**Objetivo:** Verificar que puedes interrumpir al bot cuando habla

**Pasos:**
1. Ingresa tu número de teléfono
2. Click en "Iniciar Conversación"
3. Permite acceso al micrófono cuando te lo pida
4. Espera a que el bot comience a responder (verás "Bot hablando...")
5. **Mientras el bot habla, di algo en voz alta**

**Resultado Esperado:**
- ✅ El audio del bot se detiene inmediatamente
- ✅ El estado cambia a "Escuchando..."
- ✅ Aparece mensaje: "⚡ Has interrumpido al asistente. Habla ahora..."
- ✅ Tu voz comienza a grabarse automáticamente

**Logs en Consola:**
```
🎤 VAD continuo activado (umbral: 40, frames: 3)
🎤 VAD: Voz detectada (nivel 65) mientras bot habla - Interrumpiendo...
🛑 VAD: Usuario interrumpiendo al bot
```

---

### Test 2: No Interrumpir con Ruido Bajo ✅

**Objetivo:** Verificar que ruido ambiental no interrumpe al bot

**Pasos:**
1. Inicia conversación
2. Espera a que el bot hable
3. **Haz ruidos suaves** (teclado, movimiento, etc.)

**Resultado Esperado:**
- ✅ El bot continúa hablando sin interrupción
- ✅ La barra de nivel muestra algo de actividad pero no interrumpe
- ✅ No hay mensajes de interrupción

**Por qué funciona:**
El sistema usa **frames consecutivos** (3 frames por defecto), por lo que ruidos momentáneos no activan la interrupción.

---

### Test 3: Múltiples Interrupciones ✅

**Objetivo:** Verificar que puedes interrumpir varias veces

**Pasos:**
1. Inicia conversación y haz una pregunta
2. Interrumpe al bot cuando responda
3. Haz otra pregunta
4. Interrumpe de nuevo

**Resultado Esperado:**
- ✅ Cada interrupción funciona correctamente
- ✅ No hay errores en consola
- ✅ El sistema se mantiene estable

---

### Test 4: Visualización del Nivel de Audio ✅

**Objetivo:** Verificar que la UI muestra el nivel de audio

**Pasos:**
1. Inicia conversación
2. Observa la barra de progreso azul debajo del estado
3. Habla y observa cómo cambia

**Resultado Esperado:**
- ✅ La barra se mueve en tiempo real con tu voz
- ✅ Muestra valores de 0-255
- ✅ Funciona incluso cuando el bot habla

---

### Test 5: Estado Mute vs VAD ✅

**Objetivo:** Verificar interacción entre mute y VAD

**Pasos:**
1. Inicia conversación
2. Espera a que el bot hable
3. Click en el botón MUTE (amarillo)
4. Intenta hablar

**Resultado Esperado:**
- ✅ El bot se interrumpe
- ✅ El micrófono se activa
- ✅ El mute se desactiva automáticamente
- ✅ Puedes hablar normalmente

**Código relevante:**
```typescript
// En interruptBot()
this._isMuted = false; // Desactiva mute automáticamente
```

---

## 🔧 Ajustes de Sensibilidad

### Si NO puedes interrumpir al bot:

**Edita:** `src/app/shared/config/audio.config.ts`

```typescript
vad: {
  energyThreshold: 30,    // ↓ Bajar de 40 a 30
  consecutiveFrames: 2    // ↓ Bajar de 3 a 2
}
```

### Si el bot se interrumpe con TODO:

**Edita:** `src/app/shared/config/audio.config.ts`

```typescript
vad: {
  energyThreshold: 50,    // ↑ Subir de 40 a 50
  consecutiveFrames: 5    // ↑ Subir de 3 a 5
}
```

---

## 📊 Monitoreo Avanzado

### Ver valores en tiempo real

Abre la consola del navegador (F12) y pega:

```javascript
// Ver nivel de audio actual
setInterval(() => {
  console.log('Nivel audio:', document.querySelector('ion-progress-bar').value);
}, 500);
```

### Ver estado de VAD

```javascript
// Verificar si VAD está activo
console.log('VAD activo:', audioRecorder.isVADActive);
console.log('Frames consecutivos:', audioRecorder.consecutiveVoiceFrames);
console.log('Voz detectada:', audioRecorder.hasVoiceDetected);
```

---

## 🐛 Troubleshooting

### Problema: "No se puede acceder al micrófono"

**Soluciones:**
1. Verifica permisos del navegador
2. Usa Chrome/Edge (mejor compatibilidad)
3. Verifica que estés en HTTPS o localhost
4. Prueba con otro micrófono si tienes

### Problema: El bot nunca se interrumpe

**Diagnóstico:**
1. Abre consola (F12)
2. Busca: `🎤 VAD continuo activado`
3. Habla y busca: `🎤 VAD: Voz detectada`

**Si no ves "VAD continuo activado":**
- El servicio no se inicializó
- Verifica que `startConversation()` se ejecutó correctamente

**Si no ves "Voz detectada":**
- Habla más fuerte
- Baja `energyThreshold` a 25-30
- Verifica que el micrófono funciona en otra app

### Problema: Se interrumpe con eco/audio del bot

**Soluciones:**
1. **Usa audífonos** (mejor solución)
2. Verifica que `echoCancellation: true`
3. Aumenta `energyThreshold` a 50-60

**Verificar echoCancellation:**
```typescript
// En audio.config.ts
microphone: {
  echoCancellation: true,  // ✅ Debe estar en true
  noiseSuppression: true,  // ✅ Debe estar en true
  autoGainControl: true    // ✅ Debe estar en true
}
```

---

## 📈 Métricas de Éxito

### ✅ Funcionamiento Correcto

- **Tasa de detección**: >90% (interrumpe cuando hablas)
- **Falsos positivos**: <10% (no interrumpe con ruido)
- **Latencia**: <200ms (desde hablar hasta interrupción)
- **Estabilidad**: Sin errores en múltiples interrupciones

### 🎯 Valores Típicos

**Ambiente silencioso:**
- Nivel de audio en silencio: 0-15
- Nivel de audio hablando: 50-150
- Threshold recomendado: 30-35

**Ambiente con ruido:**
- Nivel de audio en silencio: 20-40
- Nivel de audio hablando: 70-180
- Threshold recomendado: 45-55

---

## 🎓 Entendiendo los Logs

### Log: `🎤 VAD continuo activado (umbral: 40, frames: 3)`
**Significado:** El sistema VAD está monitoreando el micrófono

### Log: `🎤 VAD: Voz detectada (nivel 65) mientras bot habla`
**Significado:** Se detectó voz con nivel 65, se va a interrumpir

### Log: `🛑 VAD: Usuario interrumpiendo al bot`
**Significado:** Se ejecutó la interrupción, el bot se detuvo

### Log: `⚡ Has interrumpido al asistente. Habla ahora...`
**Significado:** Mensaje visible al usuario en la UI

---

## ✅ Checklist de Prueba Completa

- [ ] Test 1: Interrupción básica funciona
- [ ] Test 2: Ruido bajo no interrumpe
- [ ] Test 3: Múltiples interrupciones funcionan
- [ ] Test 4: Visualización de nivel de audio
- [ ] Test 5: Interacción mute vs VAD
- [ ] Sin errores en consola
- [ ] Logs correctos en consola
- [ ] Experiencia fluida y natural

---

## 📝 Reporte de Pruebas

### Ambiente de Prueba
- **Navegador:** _____________
- **Sistema Operativo:** _____________
- **Micrófono:** _____________
- **Audífonos:** Sí / No

### Configuración Usada
```typescript
vad: {
  energyThreshold: ____,
  consecutiveFrames: ____
}
```

### Resultados
- ✅ / ❌ Interrupción básica
- ✅ / ❌ Evita falsos positivos
- ✅ / ❌ Múltiples interrupciones
- ✅ / ❌ Visualización correcta
- ✅ / ❌ Sin errores

### Notas Adicionales:
```
_______________________________________________
_______________________________________________
_______________________________________________
```

---

**Fecha de última actualización:** 13 de enero de 2026  
**Versión de prueba:** 1.0.0
