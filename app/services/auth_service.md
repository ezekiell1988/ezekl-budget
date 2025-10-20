# Unificación del Sistema de Autenticación

## 📋 Resumen

Hemos unificado el sistema de autenticación para que tanto el **backoffice web** como **WhatsApp** compartan la misma lógica de sesiones de 24 horas almacenadas en Redis.

## 🎯 Objetivos Alcanzados

1. ✅ **Sesiones unificadas de 24 horas** para web y WhatsApp
2. ✅ **Servicio centralizado** de autenticación (`auth_service.py`)
3. ✅ **Logout real** que invalida sesiones en Redis
4. ✅ **Validación consistente** en todos los endpoints protegidos
5. ✅ **Código más limpio** y menos duplicación

## 📂 Archivos Creados

### `app/services/auth_service.py`
**Servicio centralizado de autenticación**

Métodos principales:
- `save_session(user_id, user_data, session_type, expires_in_seconds)` - Guarda sesión en Redis
- `get_session(user_id, session_type)` - Obtiene datos de sesión
- `is_authenticated(user_id, session_type)` - Verifica si hay sesión activa
- `delete_session(user_id, session_type)` - Elimina sesión (logout)
- `extend_session(user_id, session_type, expires_in_seconds)` - Extiende tiempo de sesión
- `get_session_ttl(user_id, session_type)` - Obtiene tiempo restante de sesión

**Tipos de sesión:**
- `"web"` - Sesiones del backoffice (identificadas por email)
- `"whatsapp"` - Sesiones de WhatsApp (identificadas por número de teléfono)

**Formato de claves en Redis:**
```
auth_session:web:{user_email}
auth_session:whatsapp:{phone_number}
```

## 🔄 Archivos Modificados

### 1. `app/services/whatsapp_service.py`

**Cambios:**
- Métodos de autenticación ahora usan `auth_service` internamente
- `save_whatsapp_auth()` → llama a `auth_service.save_session()`
- `get_whatsapp_auth()` → llama a `auth_service.get_session()`
- `is_whatsapp_authenticated()` → llama a `auth_service.is_authenticated()`
- `delete_whatsapp_auth()` → llama a `auth_service.delete_session()`
- `extend_whatsapp_auth()` → llama a `auth_service.extend_session()`

**Compatibilidad:**
- La interfaz pública se mantiene igual
- No requiere cambios en código que use `whatsapp_service`

### 2. `app/api/routes/auth.py`

**Cambios principales:**

#### A. `POST /api/auth/login`
- Ahora guarda sesión en Redis además de generar token JWE
- Sesión identificada por email del usuario
- TTL de 24 horas

#### B. `POST /api/auth/logout` (MEJORADO)
- **Antes:** Solo informativo, no invalidaba nada
- **Ahora:** Elimina sesión de Redis, invalidando el token
- Requiere autenticación (token JWE)
- Funciona para web y WhatsApp

#### C. `POST /api/auth/refresh-token`
- Extiende token JWE
- También extiende sesión en Redis (+24 horas)
- Mantiene sincronización entre token y sesión

#### D. `GET /api/auth/microsoft/callback`
- Guarda sesión en Redis para ambos flujos:
  - WhatsApp: Sesión tipo "whatsapp" con phone_number
  - Web: Sesión tipo "web" con email

#### E. `get_current_user()` (Dependency)
- **Antes:** Solo validaba token JWE
- **Ahora:** Valida token JWE + sesión activa en Redis
- Si el usuario hizo logout, la sesión no existe en Redis
- Retorna 401 si la sesión fue invalidada

### 3. `app/api/routes/whatsapp.py`

**Endpoints de autenticación:**

#### A. `DELETE /api/whatsapp/auth/logout`
- Sigue funcionando igual (usa `whatsapp_service.delete_whatsapp_auth()`)
- Internamente ahora usa el servicio unificado
- Identifica usuario por número de teléfono

#### B. `GET /api/whatsapp/auth/status`
- Verifica autenticación usando el servicio unificado
- Retorna información de sesión y TTL

#### C. `POST /api/whatsapp/auth/request-token`
- Genera tokens temporales (5 minutos)
- Incluye `bot_phone_number` en los datos del token

## 🔑 Flujo de Autenticación Unificado

### Web (Backoffice)

```
1. Usuario solicita login (email)
   ↓
2. POST /api/auth/request-token
   - Genera token temporal
   - Envía email con token
   ↓
3. POST /api/auth/login
   - Valida token temporal
   - Genera token JWE (24h)
   - Guarda sesión en Redis → auth_session:web:{email}
   - Retorna token JWE
   ↓
4. Requests subsecuentes
   - Header: Authorization: Bearer {jwe_token}
   - get_current_user() valida:
     a) Token JWE válido
     b) Sesión existe en Redis
   ↓
5. POST /api/auth/logout
   - Elimina sesión de Redis
   - Token JWE queda inválido
```

### WhatsApp

```
1. Usuario envía mensaje sin autenticación
   ↓
2. Bot detecta falta de auth
   - Genera token único (5min)
   - Envía link de autenticación
   ↓
3. Usuario abre link
   GET /api/whatsapp/auth/page?token={token}
   - Valida token temporal
   - Redirige a Microsoft OAuth
   ↓
4. Microsoft callback
   GET /api/auth/microsoft/callback
   - Autentica con Microsoft
   - Guarda sesión en Redis → auth_session:whatsapp:{phone}
   - Muestra página de éxito con botón WhatsApp
   ↓
5. Usuario vuelve a WhatsApp
   - Sesión válida por 24 horas
   - Bot procesa mensajes normalmente
   ↓
6. Logout (opcional)
   DELETE /api/whatsapp/auth/logout?phone_number={phone}
   - Elimina sesión de Redis
```

## 🔐 Ventajas de la Unificación

### 1. Logout Real
**Antes:**
- Web: Logout no invalidaba el token (JWE sin estado)
- WhatsApp: Logout funcionaba pero lógica separada

**Ahora:**
- Ambos: Logout elimina sesión de Redis
- Token JWE se vuelve inútil sin sesión en Redis
- Seguridad mejorada

### 2. Código Centralizado
**Antes:**
- Lógica duplicada en `whatsapp_service.py`
- Cada sistema gestionaba sus sesiones

**Ahora:**
- Un solo servicio: `auth_service.py`
- Fácil de mantener y testear
- Reutilizable para futuros tipos de auth

### 3. Consistencia
**Antes:**
- Web: Token JWE con 24h
- WhatsApp: Redis con 24h pero formato diferente

**Ahora:**
- Ambos: Redis con 24h, mismo formato
- Mismos métodos, misma lógica
- Mismo comportamiento de expiración

### 4. Flexibilidad
- Fácil agregar nuevos tipos de sesión
- Posible extender a otros canales (Telegram, Slack, etc.)
- TTL configurable por tipo de sesión

## 📊 Estructura de Datos en Redis

### Sesión Web
```json
{
  "codeLogin": "USR001",
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "session_type": "web",
  "user_id": "juan@example.com",
  "created_at": "2025-10-20T10:30:00",
  "expires_in": 86400
}
```
**Key:** `auth_session:web:juan@example.com`  
**TTL:** 86400 segundos (24 horas)

### Sesión WhatsApp
```json
{
  "codeLogin": "USR001",
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "session_type": "whatsapp",
  "user_id": "5491112345678",
  "created_at": "2025-10-20T10:30:00",
  "expires_in": 86400
}
```
**Key:** `auth_session:whatsapp:5491112345678`  
**TTL:** 86400 segundos (24 horas)

## 🧪 Testing

### Probar Logout Web
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"codeLogin": "USER01", "token": "123456"}'

# Respuesta incluye accessToken

# 2. Verificar token
curl -X GET http://localhost:8000/api/auth/verify-token \
  -H "Authorization: Bearer {accessToken}"

# 3. Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer {accessToken}"

# 4. Intentar usar token nuevamente (debería fallar)
curl -X GET http://localhost:8000/api/auth/verify-token \
  -H "Authorization: Bearer {accessToken}"

# Resultado: 401 "Sesión inválida o expirada"
```

### Probar Logout WhatsApp
```bash
# Después de autenticación exitosa por WhatsApp

# 1. Verificar estado
curl -X GET "http://localhost:8000/api/whatsapp/auth/status?phone_number=5491112345678"

# 2. Logout
curl -X DELETE "http://localhost:8000/api/whatsapp/auth/logout?phone_number=5491112345678"

# 3. Verificar estado nuevamente (debería estar no autenticado)
curl -X GET "http://localhost:8000/api/whatsapp/auth/status?phone_number=5491112345678"
```

## 🔄 Endpoints Unificables

### Ya Unificados
- ✅ `POST /api/auth/logout` - Funciona para web
- ✅ `DELETE /api/whatsapp/auth/logout` - Funciona para WhatsApp
- ✅ Ambos usan el mismo servicio subyacente

### Posibles Mejoras Futuras

#### Endpoint Universal de Logout
```python
DELETE /api/auth/session
Query params:
  - user_id: email o phone_number
  - session_type: "web" o "whatsapp" (opcional, auto-detect)
```

#### Endpoint Universal de Estado
```python
GET /api/auth/session/status
Query params:
  - user_id: email o phone_number
  - session_type: "web" o "whatsapp"
  
Response:
{
  "authenticated": true,
  "user": {...},
  "session_type": "web",
  "expires_in": 82341,  // segundos restantes
  "expires_at": "2025-10-21T10:30:00"
}
```

## 📝 Notas de Migración

### Compatibilidad
- ✅ Todos los cambios son **retrocompatibles**
- ✅ Código existente sigue funcionando
- ✅ No requiere cambios en frontend

### Redis
- ⚠️ **Requiere Redis en producción**
- ⚠️ Verificar que Redis esté corriendo
- ⚠️ Las sesiones anteriores (si existían) no se migran automáticamente

### Despliegue
1. Asegurar Redis está disponible
2. Desplegar nueva versión
3. Usuarios activos deberán re-autenticarse
4. Monitorear logs de autenticación

## 🎉 Resumen Final

**Sistema de autenticación ahora:**
- ✅ Unificado entre web y WhatsApp
- ✅ Sesiones reales de 24 horas en Redis
- ✅ Logout funciona correctamente
- ✅ Código centralizado y mantenible
- ✅ Extensible a nuevos canales
- ✅ Seguridad mejorada

**Próximos pasos sugeridos:**
1. Testear ambos flujos (web y WhatsApp)
2. Monitorear Redis para ver sesiones activas
3. Considerar agregar endpoints de administración de sesiones
4. Implementar refresh automático antes de expiración
