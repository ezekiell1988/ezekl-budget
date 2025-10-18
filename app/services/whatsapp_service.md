# WhatsApp Business API - Documentación

## Configuración

### Variables de Entorno (.env)

```env
# WhatsApp Business API Configuration
WHATSAPP_ACCESS_TOKEN=tu_access_token_de_whatsapp
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=tu_business_account_id
WHATSAPP_VERIFY_TOKEN=tu_verify_token_secreto
WHATSAPP_API_VERSION=v21.0
```

### Obtener Phone Number ID

1. Ve a https://developers.facebook.com/
2. Selecciona tu aplicación de WhatsApp Business
3. Ve a "WhatsApp" > "Configuración de API"
4. Copia el "Phone Number ID"

## Endpoints Disponibles

### 1. Verificación del Webhook (GET)

**Endpoint:** `GET /api/whatsapp/webhook`

Meta llama a este endpoint para verificar tu webhook.

**Parámetros:**
- `hub.mode`: "subscribe"
- `hub.verify_token`: Token configurado en .env
- `hub.challenge`: Cadena a retornar

**Configuración en Meta:**
1. Ve a tu app en Meta for Developers
2. WhatsApp > Configuración
3. Callback URL: `https://tu-dominio.com/api/whatsapp/webhook`
4. Verify Token: `tu_verify_token_secreto` (el mismo que configuraste en .env)
5. Suscríbete a los eventos: `messages`

### 2. Recibir Webhooks (POST)

**Endpoint:** `POST /api/whatsapp/webhook`

Meta envía notificaciones aquí cuando ocurren eventos.

**Sin autenticación requerida** (Meta envía directamente)

**Funcionalidad implementada:**
- ✅ Marca mensajes como leídos automáticamente (doble check azul)
- ✅ Procesa mensajes de texto con IA
- ✅ Procesa imágenes con análisis visual
- ✅ Transcribe y procesa mensajes de audio
- ✅ Responde automáticamente con GPT-5
- ✅ Mantiene historial de conversación por usuario

### 3. Estado del Servicio (GET)

**Endpoint:** `GET /api/whatsapp/status`

**Sin autenticación requerida**

Verifica la configuración del servicio de WhatsApp.

**Respuesta:**
```json
{
  "service": "WhatsApp Business API",
  "configured": true,
  "api_version": "v21.0",
  "phone_number_id_set": true,
  "access_token_set": true,
  "supported_message_types": [
    "text",
    "image",
    "video",
    "document",
    "audio",
    "location",
    "contacts",
    "template",
    "interactive"
  ],
  "webhook_configured": true,
  "features": {
    "receive_messages": true,
    "send_messages": true,
    "validate_signature": false
  }
}
```

### 4. Enviar Mensaje (POST)

**Endpoint:** `POST /api/whatsapp/send`

**🔒 Requiere autenticación JWT**

Envía cualquier tipo de mensaje de WhatsApp.

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Body (Texto simple):**
```json
{
  "to": "5491112345678",
  "type": "text",
  "text": {
    "body": "Hola, este es un mensaje de prueba"
  }
}
```

**Body (Imagen con URL):**
```json
{
  "to": "5491112345678",
  "type": "image",
  "image": {
    "link": "https://ejemplo.com/imagen.jpg",
    "caption": "Mira esta imagen"
  }
}
```

**Body (Mensaje interactivo con botones):**
```json
{
  "to": "5491112345678",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": {
      "text": "¿Qué deseas hacer?"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "btn1",
            "title": "Ver productos"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "btn2",
            "title": "Soporte"
          }
        }
      ]
    }
  }
}
```

### 5. Enviar Texto Simple (POST)

**Endpoint:** `POST /api/whatsapp/send/text`

**🔒 Requiere autenticación JWT**

Endpoint simplificado para enviar solo texto.

**Query Parameters:**
- `to`: Número de teléfono (ej: "5491112345678")
- `message`: Contenido del mensaje
- `preview_url`: true/false (opcional, default: false)

**Ejemplo:**
```
POST /api/whatsapp/send/text?to=5491112345678&message=Hola%20mundo
```

### 6. Enviar Imagen (POST)

**Endpoint:** `POST /api/whatsapp/send/image`

**🔒 Requiere autenticación JWT**

**Query Parameters:**
- `to`: Número de teléfono
- `image_url`: URL pública de la imagen (opcional)
- `image_id`: ID de imagen subida (opcional)
- `caption`: Texto descriptivo (opcional)

### 7. Enviar Documento (POST)

**Endpoint:** `POST /api/whatsapp/send/document`

**🔒 Requiere autenticación JWT**

**Query Parameters:**
- `to`: Número de teléfono
- `document_url`: URL pública del documento
- `filename`: Nombre del archivo (opcional)
- `caption`: Texto descriptivo (opcional)

### 8. Enviar Ubicación (POST)

**Endpoint:** `POST /api/whatsapp/send/location`

**🔒 Requiere autenticación JWT**

**Query Parameters:**
- `to`: Número de teléfono
- `latitude`: Latitud
- `longitude`: Longitud
- `name`: Nombre del lugar (opcional)
- `address`: Dirección (opcional)

### 9. Enviar Plantilla (POST)

**Endpoint:** `POST /api/whatsapp/send/template`

**🔒 Requiere autenticación JWT**

**Query Parameters:**
- `to`: Número de teléfono
- `template_name`: Nombre de la plantilla aprobada
- `language_code`: Código de idioma (default: "es")

### 10. Marcar Mensaje como Leído (POST)

**Endpoint:** Usado internamente por el webhook

**Método del servicio:**
```python
await whatsapp_service.mark_message_as_read(message_id)
```

**Funcionalidad:**
- Marca un mensaje recibido como leído
- Muestra doble check azul (✓✓) al usuario
- Se ejecuta automáticamente al recibir mensajes
- Mejora la experiencia de usuario con feedback visual

**Ejemplo programático:**
```python
# Marcar mensaje como leído
success = await whatsapp_service.mark_message_as_read("wamid.XXX...")

if success:
    print("✅ Mensaje marcado como leído")
```

## Tipos de Mensajes Soportados

### 1. Texto (text)
- Máximo 4096 caracteres
- Soporta emojis
- Puede mostrar preview de URLs

### 2. Imagen (image)
- Formatos: JPG, PNG
- Tamaño máximo: 5MB
- Caption opcional (max 1024 caracteres)

### 3. Video (video)
- Formatos: MP4, 3GPP
- Tamaño máximo: 16MB
- Caption opcional

### 4. Documento (document)
- Formatos: PDF, DOC, DOCX, XLS, XLSX, PPT, TXT, etc.
- Tamaño máximo: 100MB
- Caption opcional

### 5. Audio (audio)
- Formatos: AAC, M4A, AMR, MP3, OGG
- Tamaño máximo: 16MB

### 6. Ubicación (location)
- Coordenadas de latitud y longitud
- Nombre y dirección opcionales

### 7. Contactos (contacts)
- Compartir información de contacto
- Nombre, teléfonos, emails, direcciones, etc.

### 8. Plantilla (template)
- Mensajes pre-aprobados por Meta
- Único tipo permitido fuera de ventana de 24 horas

### 9. Interactivo (interactive)
- Mensajes con botones (máximo 3)
- Mensajes con listas
- Header, body y footer personalizables

## Formato de Números de Teléfono

Los números de teléfono deben estar en formato internacional sin el símbolo +:

- ✅ Correcto: `"5491112345678"` (Argentina)
- ✅ Correcto: `"521234567890"` (México)
- ✅ Correcto: `"34612345678"` (España)
- ❌ Incorrecto: `"+5491112345678"`
- ❌ Incorrecto: `"1112345678"` (sin código de país)

## Limitaciones

### Ventana de 24 Horas
- Puedes enviar cualquier tipo de mensaje durante 24 horas después de que el usuario te escriba
- Después de 24 horas, solo puedes enviar plantillas aprobadas
- Cuando el usuario responde, la ventana se renueva

### Límites de Mensajería
- Límite inicial: ~1,000 conversaciones únicas por día
- Se incrementa automáticamente según el uso y calidad
- Consulta límites actuales en Meta Business Manager

### Restricciones de Contenido
- No spam
- No contenido prohibido (violencia, drogas, etc.)
- No mensajes masivos sin consentimiento
- Seguir políticas de Meta

## Seguridad

### Validación de Webhook (TODO)
Meta firma los webhooks con `x-hub-signature-256`. Deberías validar esta firma en producción:

```python
import hmac
import hashlib

def validate_signature(payload: str, signature: str, app_secret: str) -> bool:
    expected_signature = hmac.new(
        app_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

## Testing

### 1. Probar Webhook Verification

```bash
curl "http://localhost:8001/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=TU_VERIFY_TOKEN&hub.challenge=CHALLENGE_ACCEPTED"
```

Debe retornar: `CHALLENGE_ACCEPTED`

**Nota**: Reemplaza `TU_VERIFY_TOKEN` con el valor de tu variable `WHATSAPP_VERIFY_TOKEN` del archivo `.env`

### 2. Probar Estado del Servicio

```bash
curl http://localhost:8001/api/whatsapp/status
```

### 3. Enviar Mensaje de Texto

```bash
curl -X POST "http://localhost:8001/api/whatsapp/send/text" \
  -H "Authorization: Bearer TU_TOKEN_JWT" \
  -d "to=5491112345678" \
  -d "message=Hola desde la API"
```

## Logs

El sistema genera logs detallados:

### Logs de Mensaje de Texto
```
📱 WEBHOOK DE WHATSAPP RECIBIDO
📦 Tipo de objeto: whatsapp_business_account
📋 ENTRADA #1
  - WhatsApp Business Account ID: 123456789
  🔄 CAMBIO #1
    - Campo: messages
    📨 MENSAJES ENTRANTES: 1
      💬 MENSAJE #1
        - ID: wamid.XXX
        - De: 5491112345678
        - Tipo: text
        - Contenido: 'Hola'
        - Nombre del contacto: Juan Pérez
      
      🤖 Procesando mensaje text con IA para 5491112345678...
      ✅ Marcando mensaje como leído: wamid.XXX
      ✅ Mensaje marcado como leído exitosamente
      🤖 Generando respuesta de IA para Juan Pérez
      ✅ Respuesta generada exitosamente
      📤 Enviando respuesta de IA a Juan Pérez
      ✅ Respuesta de IA enviada: wamid.YYY
```

### Logs de Mensaje de Audio
```
📱 WEBHOOK DE WHATSAPP RECIBIDO
📨 MENSAJES ENTRANTES: 1
  💬 MENSAJE #1
    - ID: wamid.XXX
    - De: 50622703332
    - Tipo: audio
    - Audio ID: 1301795761634718
    - MIME Type: audio/ogg; codecs=opus
    - Es mensaje de voz: Sí
    - Nombre del contacto: Familia Baltodano
  
  🤖 Procesando mensaje audio con IA para 50622703332...
  ✅ Marcando mensaje como leído: wamid.XXX
  📥 Descargando audio...
  ✅ Audio descargado: 8383 bytes
  🎤 Procesando audio (8383 bytes)
  🎙️ Transcribiendo audio con Azure OpenAI (8383 bytes, formato: ogg)...
  📥 Respuesta de transcripción: 200
  ✅ Audio transcrito: 'Hola, ¿qué día es mañana?'
  🤖 Generando respuesta de IA para Familia Baltodano con audio
  ✅ Respuesta generada exitosamente
  💬 Respuesta: ¡Hola! Mañana es sábado 18 de octubre...
  📤 Enviando respuesta de IA a Familia Baltodano (audio)
  ✅ Respuesta de IA enviada: wamid.YYY
  🎤 Audio procesado con IA
```

### Logs de Imagen
```
📱 WEBHOOK DE WHATSAPP RECIBIDO
📨 MENSAJES ENTRANTES: 1
  💬 MENSAJE #1
    - Tipo: image
    - Imagen ID: 123456789
    - MIME Type: image/jpeg
    - Caption: 'Mira esta foto'
  
  🤖 Procesando mensaje image con IA para 5491112345678...
  ✅ Marcando mensaje como leído: wamid.XXX
  📥 Descargando imagen...
  ✅ Imagen descargada: 45231 bytes
  🖼️ Procesando imagen (45231 bytes)
  🤖 Generando respuesta de IA para Juan Pérez con imagen
  ✅ Respuesta generada exitosamente
  🖼️ Imagen procesada con IA
```

## Recursos Adicionales

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Meta for Developers](https://developers.facebook.com/)
- [WhatsApp Business Platform](https://business.whatsapp.com/products/business-platform)
