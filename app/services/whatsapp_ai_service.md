# WhatsApp AI Service - Documentación

## 📋 Descripción

Servicio de inteligencia artificial para WhatsApp que proporciona respuestas automáticas usando Azure OpenAI. Integra **GPT-5** (o1 reasoning model) para generar respuestas contextuales e inteligentes, con soporte multimodal para **texto, imágenes, audios y documentos PDF**.

**Características principales:**
- 🤖 Respuestas inteligentes con GPT-5
- 🎤 Transcripción de audio a texto con gpt-4o-transcribe
- 🖼️ Procesamiento de imágenes
- 📄 **Análisis directo de documentos PDF (sin extracción de texto)**
- ✓✓ Marcado automático de mensajes como leídos
- 💬 Historial de conversación por usuario
- 🔄 Respuestas automáticas contextuales

---

## 🏗️ Arquitectura

```
Usuario WhatsApp → Meta Webhook → FastAPI → WhatsApp AI Service
                        ↓                           ↓
                   ✓✓ Leído                  Procesamiento:
                                              - Texto → GPT-5
                                              - Audio → Transcripción → GPT-5
                                              - Imagen → GPT-5
                        ↓                           ↓
                  WhatsApp API ← Respuesta Automática ← Azure OpenAI
```

### Flujo de Conversación Completo

1. **Recepción**: Usuario envía mensaje (texto/audio/imagen) por WhatsApp
2. **Webhook**: Meta envía notificación al endpoint `/api/whatsapp/webhook`
3. **✓✓ Marcado como leído**: Se marca el mensaje con doble check azul inmediatamente
4. **Procesamiento multimodal**:
   - **Audio**: Transcripción automática con Azure OpenAI (gpt-4o-transcribe)
   - **Imagen**: Análisis visual con GPT-5
   - **Texto**: Procesamiento directo
5. **IA**: GPT-5 genera respuesta contextual basada en el historial
6. **Envío**: La respuesta se envía automáticamente al usuario por WhatsApp

---

## 🚀 Características Principales

### ✅ Respuestas Automáticas con IA
- Respuestas generadas por **GPT-5** (o1 reasoning model) de Azure OpenAI
- Contextualizadas según el negocio (Ezekl Budget)
- Tono profesional pero amigable
- Reasoning avanzado para respuestas más inteligentes

### 🎤 Procesamiento de Audio
- Transcripción automática con **gpt-4o-transcribe** de Azure OpenAI
- Soporta múltiples formatos: OGG, MP3, WAV, M4A
- Transcripción directa sin conversión de formato
- La transcripción se procesa naturalmente como texto por GPT-5
- Sin prefijos artificiales - respuesta natural al contenido del audio

### 🖼️ Procesamiento de Imágenes
- Análisis visual con GPT-5 (visión multimodal)
- Soporta JPG, PNG, WebP
- Caption opcional con la imagen
- Respuestas contextuales sobre el contenido visual

### 📄 Procesamiento de PDFs
- **Análisis directo por GPT-5**: El modelo recibe el PDF completo codificado en base64
- **Sin extracción de texto**: No se usa PyPDF2 ni librerías externas
- **Procesamiento nativo**: GPT-5 analiza el PDF directamente como lo hace con imágenes
- **Con o sin caption**: Puedes enviar solo el PDF o acompañarlo con una pregunta
- **Respuesta inmediata**: El modelo analiza y responde en el mismo mensaje
- **Sin límites artificiales**: El modelo determina cuánto puede procesar del documento

### ✓✓ Confirmación de Lectura
- Marca mensajes como leídos automáticamente
- Doble check azul aparece inmediatamente
- Mejor experiencia de usuario con feedback visual

### 💬 Gestión de Historial
- Mantiene historial de conversación por usuario
- Máximo configurable de mensajes por conversación (default: 10)
- Posibilidad de limpiar historial manualmente
- Contexto completo en cada interacción

### 🎯 Personalización
- Respuestas adaptadas al nombre del usuario
- Sistema de instrucciones personalizable
- Límite de tokens configurable para WhatsApp
- Max 8000 tokens de completition para reasoning (GPT-5)

### 🛡️ Manejo de Errores
- Respuesta de fallback automática en caso de error
- Logging detallado de todas las operaciones
- Manejo graceful de excepciones
- Recuperación automática de errores de transcripción

---

## 📦 Componentes

### 1. `whatsapp_ai_service.py`

Servicio principal que maneja:
- Inicialización de Azure OpenAI client
- Gestión de historial de conversaciones
- Generación de respuestas con IA
- Integración con WhatsApp Business API

### 2. Endpoints en `whatsapp.py`

#### Webhook (Automático)
```http
POST /api/whatsapp/webhook
```
- Recibe mensajes de WhatsApp automáticamente
- Marca mensajes como leídos (✓✓ azul) inmediatamente
- Procesa con IA y responde automáticamente
- Soporta: **texto, imágenes, audios y documentos PDF**
- Audio: transcribe automáticamente antes de procesar
- Imagen: analiza contenido visual con GPT-5
- **PDF: envía el documento completo directamente a GPT-5 para análisis**

#### Chat con IA (Manual)
```http
POST /api/whatsapp/ai/chat
```
**Parámetros:**
- `message`: Mensaje del usuario
- `phone_number`: Número de teléfono (para contexto)
- `contact_name`: Nombre opcional del contacto

**Respuesta:**
```json
{
  "response": "¡Hola! 👋 Soy el asistente de Ezekl Budget...",
  "phone_number": "5491112345678",
  "contact_name": "Juan Pérez"
}
```

#### Enviar Respuesta de IA
```http
POST /api/whatsapp/ai/reply
```
**Parámetros:**
- `message`: Mensaje del usuario
- `phone_number`: Número destino
- `contact_name`: Nombre opcional

**Respuesta:**
```json
{
  "success": true,
  "ai_response": "Respuesta generada...",
  "whatsapp_message_id": "wamid.xxx"
}
```

#### Limpiar Historial
```http
DELETE /api/whatsapp/ai/history/{phone_number}
```

#### Estadísticas
```http
GET /api/whatsapp/ai/statistics
```
**Respuesta:**
```json
{
  "active_conversations": 5,
  "total_messages": 42,
  "max_history_per_conversation": 10
}
```

---

## ⚙️ Configuración

### Variables de Entorno (.env)

```bash
# Azure OpenAI - Chat (GPT-5) (requerido)
AZURE_OPENAI_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com
AZURE_OPENAI_API_KEY=tu_api_key
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-5  # Deployment de GPT-5 para chat
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Azure OpenAI - Audio Transcription (requerido para audios)
AZURE_OPENAI_AUDIO_DEPLOYMENT_NAME=gpt-4o-transcribe  # Deployment de transcripción
AZURE_OPENAI_AUDIO_API_VERSION=2025-03-01-preview

# WhatsApp Business API (requerido)
WHATSAPP_ACCESS_TOKEN=tu_token
WHATSAPP_PHONE_NUMBER_ID=tu_phone_id
WHATSAPP_API_VERSION=v21.0
```

### Personalización del Servicio

En `whatsapp_ai_service.py`, puedes modificar:

#### System Prompt
```python
self.system_prompt = """Eres un asistente virtual de Ezekl Budget...
Tu función es:
- Responder consultas sobre la aplicación
- Ayudar con dudas sobre presupuestos
...
"""
```

#### Parámetros de Configuración
```python
self.max_history_messages = 10      # Mensajes a recordar
self.max_response_tokens = 150      # Tokens máximos (más corto)
```

#### Parámetros de Generación
```python
temperature=0.7,           # Creatividad (0.0 - 2.0)
max_tokens=150,            # Longitud de respuesta
top_p=0.9,                 # Nucleus sampling
frequency_penalty=0.5,     # Penalización repetición
presence_penalty=0.5       # Penalización temas
```

---

## 🔧 Uso

### 1. Respuesta Automática (Recomendado)

El servicio está configurado para responder automáticamente a mensajes de **texto, audio e imágenes**:

```python
# Ya configurado en whatsapp.py
if message.type in ["text", "image", "audio"]:
    # ✓✓ Marcar como leído inmediatamente
    await whatsapp_service.mark_message_as_read(message.id)
    
    # Procesar según tipo
    if message.type == "text":
        user_text = message.text.body
        
    elif message.type == "image":
        # Descargar y procesar imagen
        image_data = await whatsapp_service.get_media_content(message.image.id)
        user_text = message.image.caption or "¿Qué ves en esta imagen?"
        
    elif message.type == "audio":
        # Descargar audio - la transcripción es automática
        audio_data = await whatsapp_service.get_media_content(message.audio.id)
        user_text = None  # La transcripción reemplazará esto
    
    elif message.type == "document":
        # Descargar documento PDF
        document_data = await whatsapp_service.get_media_content(message.document.id)
        pdf_data = document_data
        filename = message.document.filename
        user_text = None  # El texto se extrae del PDF automáticamente
    
    # Generar y enviar respuesta
    ai_result = await whatsapp_ai_service.process_and_reply(
        user_message=user_text,
        phone_number=message.from_,
        contact_name=contact_name,
        image_data=image_data,
        audio_data=audio_data,
        pdf_data=pdf_data,
        filename=filename,
        media_type=media_type
    )
```

### 2. Uso Programático

```python
from app.services.whatsapp_ai_service import whatsapp_ai_service

# Solo generar respuesta (sin enviar)
response = await whatsapp_ai_service.generate_response(
    user_message="¿Cómo creo un presupuesto?",
    phone_number="5491112345678",
    contact_name="Juan"
)

# Generar y enviar automáticamente
result = await whatsapp_ai_service.process_and_reply(
    user_message="¿Cómo creo un presupuesto?",
    phone_number="5491112345678",
    contact_name="Juan"
)

# Procesar PDF
result = await whatsapp_ai_service.process_and_reply(
    user_message="¿Cuál es el presupuesto total?",  # Pregunta sobre el PDF
    phone_number="5491112345678",
    contact_name="Juan",
    pdf_data=pdf_bytes,
    filename="documento.pdf"
)

# O enviar PDF sin pregunta para análisis general
result = await whatsapp_ai_service.process_and_reply(
    user_message=None,  # Sin pregunta específica
    phone_number="5491112345678",
    contact_name="Juan",
    pdf_data=pdf_bytes,
    filename="presupuesto.pdf"
)

# Limpiar historial de un usuario
whatsapp_ai_service.clear_history("5491112345678")

# Obtener estadísticas
stats = whatsapp_ai_service.get_statistics()
```

---

## 📊 Logging

El servicio registra información detallada para cada operación:

### Logs de Texto
```
✅ Marcando mensaje como leído: wamid.XXX
🤖 Generando respuesta de IA para Juan Pérez
📝 Mensaje del usuario: ¿Cómo creo un presupuesto?
🔧 Usando deployment: gpt-5
📊 Token usage - Prompt: 192, Completion: 714, Total: 906
🧠 Reasoning tokens: 640
📝 Visible tokens: 74
✅ Respuesta generada exitosamente
💬 Respuesta: Para crear un presupuesto en Ezekl Budget...
📤 Enviando respuesta de IA a Juan Pérez
✅ Respuesta de IA enviada exitosamente
```

### Logs de Audio
```
✅ Marcando mensaje como leído: wamid.XXX
📥 Descargando audio...
✅ Audio descargado: 8383 bytes
🎤 Procesando audio (8383 bytes)
🎙️ Transcribiendo audio con Azure OpenAI (8383 bytes, formato: ogg)...
📡 URL: .../gpt-4o-transcribe/audio/transcriptions?api-version=2025-03-01-preview
📥 Respuesta de transcripción: 200
✅ Audio transcrito: 'Hola, ¿qué día es mañana?'
🤖 Generando respuesta de IA para Juan Pérez con audio
📝 Mensaje del usuario: Hola, ¿qué día es mañana?
✅ Respuesta generada exitosamente
💬 Respuesta: ¡Hola! Mañana es sábado 18 de octubre...
```

### Logs de Imagen
```
✅ Marcando mensaje como leído: wamid.XXX
📥 Descargando imagen...
✅ Imagen descargada: 45231 bytes
🖼️ Procesando imagen (45231 bytes)
🤖 Generando respuesta de IA para Juan Pérez con imagen
✅ Respuesta generada exitosamente
💬 Respuesta: Veo en la imagen...
```

### Logs de PDF
```
✅ Marcando mensaje como leído: wamid.XXX
📥 Descargando documento...
✅ Documento descargado: 125847 bytes
📄 Procesando PDF: presupuesto.pdf (125847 bytes)
🤖 Generando respuesta de IA para Juan Pérez con PDF
✅ Respuesta generada exitosamente
💬 Respuesta: Este presupuesto anual tiene un total de $450,000...
```

---

## 🎯 Mejores Prácticas

### 1. Mantén las Respuestas Cortas
WhatsApp funciona mejor con respuestas concisas:
```python
max_response_tokens = 150  # ~100-150 palabras
```

### 2. Usa Emojis con Moderación
Los emojis hacen las respuestas más amigables pero no abuses:
```python
"¡Hola! 👋 Puedo ayudarte con Ezekl Budget"  # ✅ Bien
"¡¡¡Hola!!! 👋😊🎉💰📱"                     # ❌ Demasiado
```

### 3. Proporciona Información de Contacto
Siempre ofrece alternativas si la IA no puede ayudar:
```python
"Si necesitas ayuda adicional, contacta a soporte@ezeklbudget.com"
```

### 4. Limpia el Historial Periódicamente
Para conversaciones largas o problemas de contexto:
```python
whatsapp_ai_service.clear_history(phone_number)
```

---

## 🔒 Seguridad

### Autenticación
Todos los endpoints manuales requieren autenticación:
```python
current_user: dict = Depends(get_current_user)
```

### Validación de Webhook
Meta envía firma `x-hub-signature-256` para validar la autenticidad:
```python
# TODO: Implementar validación de firma
x_hub_signature_256: Optional[str] = Header(None)
```

---

## 🐛 Troubleshooting

### Error: "Cliente de Azure OpenAI no inicializado"
**Causa**: Variables de entorno faltantes
**Solución**: Verificar `.env` tiene `AZURE_OPENAI_*` configurado

### Error: "WhatsApp no configurado"
**Causa**: Credenciales de WhatsApp faltantes
**Solución**: Verificar `WHATSAPP_ACCESS_TOKEN` y `WHATSAPP_PHONE_NUMBER_ID`

### La IA no responde automáticamente
**Causa**: Webhook no configurado correctamente en Meta
**Solución**: 
1. Verificar URL del webhook en Meta Developer Console
2. Verificar que el webhook esté suscrito a eventos "messages"
3. Revisar logs del servidor

### Respuestas muy largas
**Causa**: `max_response_tokens` muy alto
**Solución**: Reducir a 100-150 tokens para WhatsApp

---

## 📈 Métricas y Monitoreo

### Estadísticas Disponibles
```python
stats = whatsapp_ai_service.get_statistics()
# {
#   "active_conversations": 5,
#   "total_messages": 42,
#   "max_history_per_conversation": 10
# }
```

### Logs Importantes
- ✅ Respuestas exitosas
- ❌ Errores de IA o WhatsApp
- 🤖 Mensajes procesados
- 📊 Tokens utilizados

---

## ✅ Funcionalidades Completadas

- [x] ✅ **Soporte multimodal**: texto, imágenes, audios y PDFs
- [x] ✅ **Transcripción de audio**: gpt-4o-transcribe integrado
- [x] ✅ **Procesamiento de imágenes**: GPT-5 visión multimodal
- [x] ✅ **Procesamiento de PDFs**: análisis directo por GPT-5 sin extracción de texto
- [x] ✅ **Marcado de mensajes como leídos**: doble check azul automático
- [x] ✅ **Respuestas automáticas con GPT-5**: o1 reasoning model
- [x] ✅ **Historial de conversación**: contexto por usuario
- [x] ✅ **HTTPClient optimizado**: multipart/form-data para audios
- [x] ✅ **Sin dependencias externas**: eliminado ffmpeg y PyPDF2

## 🚀 Próximas Mejoras

- [ ] Implementar validación de firma `x-hub-signature-256`
- [ ] Soporte para videos con transcripción
- [ ] Persistencia de historial en base de datos
- [ ] Analytics y métricas avanzadas
- [ ] Rate limiting por usuario
- [ ] A/B testing de prompts
- [ ] Integración con CRM para contexto de usuarios
- [ ] Respuestas con botones interactivos
- [ ] Multi-idioma automático
- [ ] Streaming de respuestas para mensajes largos
- [ ] Cache de transcripciones de audio

---

## 📝 Ejemplos Completos

### Ejemplo 1: Conversación de Texto

**Usuario**: "Hola, ¿qué es Ezekl Budget?"

**Sistema**: ✓✓ (marca como leído)

**IA**: "¡Hola! 👋 Ezekl Budget es una aplicación completa de gestión financiera y presupuestos que te ayuda a organizar tus finanzas personales. ¿Te gustaría saber más sobre alguna funcionalidad específica?"

**Usuario**: "¿Cómo creo mi primer presupuesto?"

**Sistema**: ✓✓ (marca como leído)

**IA**: "Para crear tu primer presupuesto en Ezekl Budget:

1. Ingresa a la app 📱
2. Ve a 'Presupuestos' 
3. Toca el botón '+'
4. Define nombre, monto y categorías

¿Necesitas ayuda con algo más específico?"

---

### Ejemplo 2: Mensaje de Audio

**Usuario**: 🎤 *[Envía audio de voz: "Hola, ¿qué día es mañana?"]*

**Sistema**: 
1. ✓✓ Marca como leído
2. 🎙️ Transcribe: "Hola, ¿qué día es mañana?"
3. 🤖 GPT-5 procesa la transcripción

**IA**: "¡Hola! Mañana es sábado 18 de octubre de 2025. ¿Necesitas ayuda con algo relacionado a tus finanzas o presupuestos? 😊"

---

### Ejemplo 3: Imagen con Caption

**Usuario**: 🖼️ *[Envía imagen de un recibo]* + Caption: "¿Puedo agregar esto a mi presupuesto?"

**Sistema**:
1. ✓✓ Marca como leído
2. 📥 Descarga imagen
3. 🤖 GPT-5 analiza visualmente

**IA**: "¡Claro! Veo en el recibo un gasto de $1,250 en supermercado del 17 de octubre. Puedes agregarlo a tu presupuesto en la categoría 'Alimentación'. ¿Quieres que te guíe en el proceso? 📊"

---

### Ejemplo 4: Documento PDF (Análisis Directo)

**Usuario**: 📄 *[Envía archivo: "presupuesto_anual_2025.pdf"]*

**Sistema**:
1. ✓✓ Marca como leído
2. 📥 Descarga documento (125,847 bytes)
3. � Codifica PDF en base64
4. 🤖 GPT-5 analiza el PDF completo

**IA**: "He analizado el presupuesto anual 2025. El documento contiene:

📊 **Resumen Ejecutivo:**
- Presupuesto total: $450,000
- Distribuido en 6 departamentos
- Período: Enero - Diciembre 2025

**Principales partidas:**
- Marketing: $45,000 (10%)
- Recursos Humanos: $180,000 (40%)
- Operaciones: $150,000 (33%)
- Tecnología: $45,000 (10%)
- Administración: $30,000 (7%)

¿Te gustaría que profundice en algún área específica? 📈"

**Usuario**: "Desglosame el presupuesto de marketing"

**Sistema**:
1. ✓✓ Marca como leído
2. 🤖 GPT-5 usa el historial (ya tiene el PDF en contexto)

**IA**: "Según el documento, el presupuesto de Marketing ($45,000) se distribuye así:

💰 **Desglose detallado:**
- Publicidad digital: $20,000 (44%)
  - Google Ads: $10,000
  - Meta Ads: $7,000
  - LinkedIn Ads: $3,000
- Eventos y ferias: $15,000 (33%)
- Material promocional: $10,000 (23%)
  - Diseño gráfico: $4,000
  - Impresión: $6,000

El documento indica que es un incremento del 15% respecto al año anterior. ¿Necesitas más detalles? �"

---
3. 🖼️ GPT-5 analiza imagen + caption

**IA**: "Claro que sí! Veo que es un recibo de compra. Para agregarlo a tu presupuesto en Ezekl Budget:

1. Abre la app
2. Ve a 'Gastos'
3. Toca '+' para nuevo gasto
4. Ingresa el monto y categoría
5. Opcional: Adjunta la foto del recibo

¿Necesitas ayuda con algo más?"

---

## 📞 Contacto y Soporte

- **Email**: soporte@ezeklbudget.com
- **Documentación**: https://ezeklbudget.com/docs
- **API Reference**: https://api.ezeklbudget.com/docs

---

## 📄 Licencia

Este código es parte del proyecto Ezekl Budget.
