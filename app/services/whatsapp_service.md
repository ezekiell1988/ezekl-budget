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

# Redis Configuration (Requerido para autenticación de WhatsApp)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_DECODE_RESPONSES=true
```

### Obtener Phone Number ID

1. Ve a https://developers.facebook.com/
2. Selecciona tu aplicación de WhatsApp Business
3. Ve a "WhatsApp" > "Configuración de API"
4. Copia el "Phone Number ID"

## Arquitectura de Autenticación

### Documentación Completa

Para entender el sistema completo de autenticación unificado (Web, WhatsApp y Microsoft OAuth), consulta:

📄 **[Sistema Unificado de Autenticación](./auth_service.md)**

Este documento incluye:
- Arquitectura de sesiones en Redis
- Flujos de autenticación para Web y WhatsApp
- Integración con Microsoft OAuth
- Stored Procedures de asociación de cuentas
- Ejemplos de testing completos

### Componentes

1. **`app/core/redis.py`**: Cliente Redis genérico y reutilizable para toda la aplicación
2. **`app/services/whatsapp_service.py`**: Servicio completo de WhatsApp incluyendo mensajería y autenticación
3. **`app/api/routes/whatsapp.py`**: Todos los endpoints de WhatsApp (webhook, envío, autenticación)

### Flujo de Autenticación

1. Usuario envía mensaje por WhatsApp → Sistema verifica autenticación
2. Si NO está autenticado: 
   - Sistema genera token único (válido 5 minutos)
   - Envía link de autenticación por WhatsApp
3. Usuario hace clic en link → Página HTML con auto-redirect a Microsoft OAuth
4. Usuario se autentica con Microsoft
5. Callback guarda datos en Redis (válido 24 horas)
6. Usuario puede usar el bot sin restricciones

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
- ✅ Verifica autenticación del usuario antes de procesar
- ✅ Envía link de autenticación si no está autenticado
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

### 10. Solicitar Token de Autenticación (POST)

**Endpoint:** `POST /api/whatsapp/auth/request-token`

**Sin autenticación requerida**

Genera un token único para que un usuario de WhatsApp se autentique con Microsoft.

**Body:**
```json
{
  "phone_number": "5491112345678"
}
```

**Respuesta:**
```json
{
  "success": true,
  "token": "token_generado_aqui",
  "auth_url": "https://tu-dominio.com/api/whatsapp/auth/page?token=...",
  "message": "Token generado exitosamente. Válido por 5 minutos."
}
```

### 11. Verificar Estado de Autenticación (GET)

**Endpoint:** `GET /api/whatsapp/auth/status?phone_number=5491112345678`

**Sin autenticación requerida**

Verifica si un usuario de WhatsApp está autenticado.

**Respuesta (autenticado):**
```json
{
  "authenticated": true,
  "phone_number": "5491112345678",
  "user_data": {
    "codeLogin": 123,
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "authenticated_at": "2025-10-20T10:30:00",
    "expires_at": "2025-10-21T10:30:00"
  },
  "message": "Usuario autenticado correctamente"
}
```

**Respuesta (no autenticado):**
```json
{
  "authenticated": false,
  "phone_number": "5491112345678",
  "user_data": null,
  "message": "Usuario no autenticado"
}
```

### 12. Cerrar Sesión de WhatsApp (DELETE)

**Endpoint:** `DELETE /api/whatsapp/auth/logout?phone_number=5491112345678`

**Sin autenticación requerida**

Cierra la sesión de un usuario de WhatsApp (elimina su autenticación).

**Respuesta:**
```json
{
  "success": true,
  "message": "Sesión cerrada exitosamente para 5491112345678"
}
```

### 13. Página de Autenticación (GET)

**Endpoint:** `GET /api/whatsapp/auth/page?token=TOKEN_GENERADO`

**Sin autenticación requerida**

Página HTML que redirige automáticamente al flujo de autenticación de Microsoft.

**Flujo:**
1. Valida el token de autenticación
2. Extrae el número de teléfono asociado
3. Redirige automáticamente a Microsoft OAuth
4. Pasa el contexto de WhatsApp en el parámetro state

**Casos:**
- ✅ Token válido: Redirige a Microsoft OAuth
- ❌ Token inválido/expirado: Muestra página de error

### 14. Marcar Mensaje como Leído (Interno)

**Método del servicio:**
```python
await whatsapp_service.mark_message_as_read(message_id)
```

**Funcionalidad:**
- Marca un mensaje recibido como leído
- Muestra doble check azul (✓✓) al usuario
- Se ejecuta automáticamente al recibir mensajes
- Mejora la experiencia de usuario con feedback visual

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

### Logs de Autenticación
```
🔒 Usuario no autenticado: 5491112345678 (Juan Pérez)
🔑 Token de autenticación creado para 5491112345678: xYz123abc4...
📤 Link de autenticación enviado a 5491112345678
🔐 Redirigiendo a Microsoft OAuth para WhatsApp user: 5491112345678
✅ Token válido para 5491112345678
✅ Usuario de WhatsApp autenticado exitosamente: 5491112345678
✅ Autenticación guardada para 5491112345678
```

### Logs de Mensaje de Texto (Usuario Autenticado)
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
      
      ✅ Marcando mensaje como leído: wamid.XXX
      ✅ Usuario autenticado: 5491112345678 (Juan Pérez)
      🤖 Procesando mensaje text con IA para 5491112345678...
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
  
  ✅ Marcando mensaje como leído: wamid.XXX
  ✅ Usuario autenticado: 50622703332 (Familia Baltodano)
  🤖 Procesando mensaje audio con IA para 50622703332...
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
  
  ✅ Marcando mensaje como leído: wamid.XXX
  ✅ Usuario autenticado: 5491112345678 (Juan Pérez)
  🤖 Procesando mensaje image con IA para 5491112345678...
  📥 Descargando imagen...
  ✅ Imagen descargada: 45231 bytes
  🖼️ Procesando imagen (45231 bytes)
  🤖 Generando respuesta de IA para Juan Pérez con imagen
  ✅ Respuesta generada exitosamente
  🖼️ Imagen procesada con IA
```

## Métodos del Servicio WhatsApp

### Mensajería

```python
# Enviar texto simple
await whatsapp_service.send_text_message(
    to="5491112345678",
    body="Hola mundo",
    preview_url=True
)

# Enviar imagen
await whatsapp_service.send_image(
    to="5491112345678",
    image_url="https://ejemplo.com/imagen.jpg",
    caption="Mira esta imagen"
)

# Enviar ubicación
await whatsapp_service.send_location(
    to="5491112345678",
    latitude=-34.603722,
    longitude=-58.381592,
    name="Obelisco",
    address="Buenos Aires, Argentina"
)

# Marcar como leído
await whatsapp_service.mark_message_as_read("wamid.XXX...")
```

### Autenticación

```python
# Crear token de autenticación
token = await whatsapp_service.create_auth_token(
    phone_number="5491112345678",
    expires_in_seconds=300  # 5 minutos
)

# Obtener teléfono desde token
phone = await whatsapp_service.get_phone_from_auth_token(token)

# Guardar autenticación de usuario
await whatsapp_service.save_whatsapp_auth(
    phone_number="5491112345678",
    user_data={
        "codeLogin": 123,
        "email": "usuario@ejemplo.com",
        "name": "Juan Pérez"
    },
    expires_in_seconds=86400  # 24 horas
)

# Verificar si está autenticado
is_auth = await whatsapp_service.is_whatsapp_authenticated("5491112345678")

# Obtener datos de autenticación
auth_data = await whatsapp_service.get_whatsapp_auth("5491112345678")

# Extender autenticación
await whatsapp_service.extend_whatsapp_auth(
    phone_number="5491112345678",
    expires_in_seconds=86400
)

# Cerrar sesión (logout)
await whatsapp_service.delete_whatsapp_auth("5491112345678")

# Eliminar token temporal
await whatsapp_service.delete_auth_token(token)
```

## Recursos Adicionales

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Meta for Developers](https://developers.facebook.com/)
- [WhatsApp Business Platform](https://business.whatsapp.com/products/business-platform)
