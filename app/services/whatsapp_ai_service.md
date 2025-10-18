# WhatsApp AI Service - Documentación

## 📋 Descripción

Servicio de inteligencia artificial para WhatsApp que proporciona respuestas automáticas usando Azure OpenAI. Integra GPT-4o para generar respuestas contextuales e inteligentes a los mensajes recibidos por WhatsApp Business API.

---

## 🏗️ Arquitectura

```
Usuario WhatsApp → Meta Webhook → FastAPI → WhatsApp AI Service → Azure OpenAI GPT-4o
                                     ↓                                      ↓
                                WhatsApp API ← Respuesta Automática ← Respuesta IA
```

### Flujo de Conversación

1. **Recepción**: Usuario envía mensaje por WhatsApp
2. **Webhook**: Meta envía notificación al endpoint `/api/whatsapp/webhook`
3. **Procesamiento**: El servicio extrae el mensaje y contexto del usuario
4. **IA**: Se consulta Azure OpenAI con el mensaje y historial de conversación
5. **Respuesta**: La IA genera una respuesta contextual
6. **Envío**: La respuesta se envía automáticamente al usuario por WhatsApp

---

## 🚀 Características Principales

### ✅ Respuestas Automáticas con IA
- Respuestas generadas por GPT-4o de Azure OpenAI
- Contextualizadas según el negocio (Ezekl Budget)
- Tono profesional pero amigable

### 💬 Gestión de Historial
- Mantiene historial de conversación por usuario
- Máximo configurable de mensajes por conversación (default: 10)
- Posibilidad de limpiar historial manualmente

### 🎯 Personalización
- Respuestas adaptadas al nombre del usuario
- Sistema de instrucciones personalizable
- Límite de tokens para respuestas cortas (WhatsApp-friendly)

### 🛡️ Manejo de Errores
- Respuesta de fallback automática en caso de error
- Logging detallado de todas las operaciones
- Manejo graceful de excepciones

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
- Procesa con IA y responde automáticamente
- Solo responde a mensajes de tipo "text"

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
# Azure OpenAI (requerido)
AZURE_OPENAI_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com
AZURE_OPENAI_API_KEY=tu_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o  # Nombre del deployment

# WhatsApp Business API (requerido)
WHATSAPP_ACCESS_TOKEN=tu_token
WHATSAPP_PHONE_NUMBER_ID=tu_phone_id
WHATSAPP_API_VERSION=v24.0
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

El servicio está configurado para responder automáticamente a todos los mensajes de texto que llegan al webhook:

```python
# Ya configurado en whatsapp.py
if message.type == "text" and message.text and message.text.body:
    ai_result = await whatsapp_ai_service.process_and_reply(
        user_message=message.text.body,
        phone_number=message.from_,
        contact_name=contact_name
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

# Limpiar historial de un usuario
whatsapp_ai_service.clear_history("5491112345678")

# Obtener estadísticas
stats = whatsapp_ai_service.get_statistics()
```

---

## 📊 Logging

El servicio registra información detallada:

```
🤖 Generando respuesta de IA para Juan Pérez
📝 Mensaje del usuario: ¿Cómo creo un presupuesto?
✅ Respuesta generada exitosamente
💬 Respuesta: Para crear un presupuesto en Ezekl Budget...
📤 Enviando respuesta de IA a Juan Pérez
✅ Respuesta de IA enviada exitosamente
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

## 🚀 Próximas Mejoras

- [ ] Implementar validación de firma `x-hub-signature-256`
- [ ] Soporte para otros tipos de mensajes (imágenes, audio)
- [ ] Persistencia de historial en base de datos
- [ ] Analytics y métricas avanzadas
- [ ] Rate limiting por usuario
- [ ] A/B testing de prompts
- [ ] Integración con CRM para contexto de usuarios
- [ ] Respuestas con botones interactivos
- [ ] Multi-idioma automático

---

## 📝 Ejemplo Completo

### Conversación Real

**Usuario**: "Hola, ¿qué es Ezekl Budget?"

**IA**: "¡Hola! 👋 Ezekl Budget es una aplicación completa de gestión financiera y presupuestos que te ayuda a organizar tus finanzas personales. ¿Te gustaría saber más sobre alguna funcionalidad específica?"

**Usuario**: "¿Cómo creo mi primer presupuesto?"

**IA**: "Para crear tu primer presupuesto en Ezekl Budget:

1. Ingresa a la app 📱
2. Ve a 'Presupuestos' 
3. Toca el botón '+'
4. Define nombre, monto y categorías

¿Necesitas ayuda con algo más específico?"

---

## 📞 Contacto y Soporte

- **Email**: soporte@ezeklbudget.com
- **Documentación**: https://ezeklbudget.com/docs
- **API Reference**: https://api.ezeklbudget.com/docs

---

## 📄 Licencia

Este código es parte del proyecto Ezekl Budget.
