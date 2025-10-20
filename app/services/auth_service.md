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

### Probar Login Tradicional Web
```bash
# 1. Solicitar token
curl -X POST http://localhost:8000/api/auth/request-token \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@example.com"}'

# 2. Login con token recibido por email
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"codeLogin": "USR001", "token": "123456"}'

# Respuesta incluye accessToken

# 3. Verificar token
curl -X GET http://localhost:8000/api/auth/verify-token \
  -H "Authorization: Bearer {accessToken}"

# 4. Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer {accessToken}"

# 5. Intentar usar token nuevamente (debería fallar)
curl -X GET http://localhost:8000/api/auth/verify-token \
  -H "Authorization: Bearer {accessToken}"

# Resultado: 401 "Sesión inválida o expirada"
```

### Probar Microsoft OAuth - Web (Primera Vez)
```bash
# 1. Abrir en navegador
http://localhost:8000/api/auth/microsoft/login

# 2. Autenticar con Microsoft
# Sistema ejecuta spLoginMicrosoftAddOrEdit automáticamente

# 3. Si es primera vez, redirige a:
# /#/login?microsoft_pending=true&codeLoginMicrosoft={uuid}&displayName={name}

# 4. Frontend envía asociación
curl -X POST http://localhost:8000/api/auth/microsoft/associate \
  -H "Content-Type: application/json" \
  -d '{
    "codeLogin": "USR001",
    "codeLoginMicrosoft": "uuid-de-microsoft"
  }'

# 5. Respuesta con token JWE para usar en Authorization header
```

### Probar Microsoft OAuth - Web (Ya Asociado)
```bash
# 1. Abrir en navegador
http://localhost:8000/api/auth/microsoft/login

# 2. Autenticar con Microsoft
# Sistema detecta asociación existente

# 3. Redirige automáticamente con token:
# /#/login?microsoft_success=true&token={jwe_token}

# 4. Login automático, listo para usar
```

### Probar WhatsApp con Microsoft (Primera Vez)
```bash
# 1. Simular que usuario no está autenticado
curl -X GET "http://localhost:8000/api/whatsapp/auth/status?phone_number=5491112345678"

# 2. Generar token de autenticación
curl -X POST http://localhost:8000/api/whatsapp/auth/request-token \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "5491112345678"}'

# 3. Abrir link retornado en navegador
# http://localhost:8000/api/whatsapp/auth/page?token={token}

# 4. Sistema redirige a Microsoft OAuth automáticamente

# 5. Después de autenticar, muestra formulario para codeLogin

# 6. Usuario ingresa codeLogin
# JavaScript hace POST a /api/auth/microsoft/associate/whatsapp

# 7. Verificar autenticación
curl -X GET "http://localhost:8000/api/whatsapp/auth/status?phone_number=5491112345678"

# Resultado: authenticated = true
```

### Probar Logout WhatsApp
```bash
# 1. Verificar estado
curl -X GET "http://localhost:8000/api/whatsapp/auth/status?phone_number=5491112345678"

# 2. Logout
curl -X DELETE "http://localhost:8000/api/whatsapp/auth/logout?phone_number=5491112345678"

# 3. Verificar estado nuevamente
curl -X GET "http://localhost:8000/api/whatsapp/auth/status?phone_number=5491112345678"

# Resultado: authenticated = false
```

### Probar Sesiones en Redis
```bash
# Ver todas las sesiones activas
redis-cli KEYS "auth_session:*"

# Ver datos de sesión web
redis-cli GET "auth_session:web:usuario@example.com"

# Ver datos de sesión WhatsApp
redis-cli GET "auth_session:whatsapp:5491112345678"

# Ver TTL de sesión
redis-cli TTL "auth_session:web:usuario@example.com"

# Eliminar sesión manualmente (forzar logout)
redis-cli DEL "auth_session:web:usuario@example.com"
```

## 🔄 Endpoints Unificables

### Ya Unificados
- ✅ `POST /api/auth/logout` - Funciona para web (con opción de logout de Microsoft)
- ✅ `DELETE /api/whatsapp/auth/logout` - Funciona para WhatsApp
- ✅ Ambos usan el mismo servicio subyacente

### Logout con Microsoft (Nuevo) ⭐

El endpoint de logout ahora soporta un parámetro opcional `microsoft_logout` que permite cerrar sesión también en Microsoft Azure AD.

#### Endpoint Mejorado

```http
POST /api/auth/logout?microsoft_logout=true
Authorization: Bearer {jwe_token}
```

#### Tipos de Logout

**1. Logout Local (Default) - `microsoft_logout=false`**
```
Usuario → Tu App → Redis
```
- ✅ Invalida la sesión en Redis
- ✅ El token JWE queda inútil
- ❌ El usuario sigue logueado en Microsoft
- ✅ **Recomendado para la mayoría de casos**

**Respuesta:**
```json
{
  "success": true,
  "message": "Sesión cerrada exitosamente"
}
```

**2. Logout Completo con Microsoft - `microsoft_logout=true`**
```
Usuario → Tu App → Redis → Microsoft Azure AD → Usuario
```
- ✅ Invalida la sesión en Redis
- ✅ El token JWE queda inútil
- ✅ Cierra sesión en Microsoft completamente
- ✅ Afecta TODAS las apps que usan ese login de Microsoft
- ⚠️ **Solo usar si el usuario lo solicita explícitamente**

**Respuesta:**
```json
{
  "success": true,
  "message": "Sesión cerrada exitosamente",
  "microsoft_logout_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/logout?post_logout_redirect_uri=...",
  "redirect_required": true
}
```

#### Implementación en Frontend

**Opción 1: Logout Simple (Default)**
```typescript
async function logout() {
  try {
    const token = localStorage.getItem('accessToken');
    
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');
      window.location.href = '/#/login';
    }
  } catch (error) {
    console.error('Error en logout:', error);
  }
}
```

**Opción 2: Logout con Microsoft**
```typescript
async function logoutWithMicrosoft() {
  try {
    const token = localStorage.getItem('accessToken');
    
    const response = await fetch('/api/auth/logout?microsoft_logout=true', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');
      
      if (data.redirect_required && data.microsoft_logout_url) {
        // Redirigir al logout de Microsoft
        window.location.href = data.microsoft_logout_url;
      } else {
        window.location.href = '/#/login';
      }
    }
  } catch (error) {
    console.error('Error en logout:', error);
  }
}
```

**Opción 3: Modal de Confirmación (Recomendado)**
```typescript
async function showLogoutOptions() {
  const choice = await showModal({
    title: 'Cerrar Sesión',
    message: '¿Cómo deseas cerrar sesión?',
    options: [
      {
        label: 'Solo esta aplicación',
        value: 'local',
        description: 'Seguirás conectado en Microsoft'
      },
      {
        label: 'Cerrar sesión completa',
        value: 'microsoft',
        description: 'Cerrará sesión en Microsoft y todas las aplicaciones'
      }
    ]
  });
  
  if (choice === 'local') {
    await logout();
  } else if (choice === 'microsoft') {
    await logoutWithMicrosoft();
  }
}
```

#### Configuración Requerida en Azure Entra ID

⚠️ **IMPORTANTE:** Para que el logout de Microsoft funcione, debes configurar el **Post Logout Redirect URI** en Entra ID:

1. **Acceder a Azure Portal**
   - Ve a https://portal.azure.com
   - Navega a **Entra ID** (anteriormente Azure Active Directory)

2. **Seleccionar tu App Registration**
   - Ve a **App registrations**
   - Selecciona tu aplicación (Ezekl Budget)

3. **Configurar Post Logout Redirect URI**
   - Ve a **Authentication**
   - En la sección **Front-channel logout URL**, agrega:
     ```
     http://localhost:8001/#/login?logout=success    (desarrollo)
     https://budget.ezekl.com/#/login?logout=success (producción)
     ```
   - Click en **Save**

**¿Qué pasa si NO configuro esto?**

❌ El logout de Microsoft fallará con error:
```
AADSTS50011: The reply URL specified in the request does not match 
the reply URLs configured for the application
```

#### Ventajas y Desventajas

**Ventajas del Logout con Microsoft:**
- ✅ **Cierre completo:** Previene acceso no autorizado si alguien más usa la computadora
- ✅ **Cumplimiento:** Requerido en algunos entornos corporativos
- ✅ **Control total:** Usuario decide cuándo cerrar sesión de Microsoft

**Desventajas:**
- ⚠️ **Afecta otras apps:** Cierra sesión en TODAS las apps que usan ese Microsoft Account
- ⚠️ **UX confuso:** Usuario puede no entender por qué se cerró sesión en Outlook, Teams, etc.
- ⚠️ **Re-login molesto:** Usuario debe volver a autenticarse en todos lados

**Recomendaciones:**
1. **Default = Logout Local** - La mayoría de usuarios prefieren esto
2. **Explicar claramente** - Si ofreces logout de Microsoft, explica qué hace
3. **Considerar contexto** - Computadoras compartidas → logout completo recomendado
4. **Testing frecuente** - Probar en dev/staging antes de producción

#### Testing del Logout con Microsoft

```bash
# 1. Login normal
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"codeLogin": "USR001", "token": "12345"}'

# 2. Logout con Microsoft
curl -X POST "http://localhost:8001/api/auth/logout?microsoft_logout=true" \
  -H "Authorization: Bearer {accessToken}"

# Resultado incluye microsoft_logout_url

# 3. Abrir microsoft_logout_url en navegador
# Microsoft cerrará sesión y redirigirá a tu app

# 4. Verificar que Microsoft cerró sesión
curl -X GET http://localhost:8001/api/auth/microsoft
# Microsoft debe pedir credenciales nuevamente
```

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

## 🔐 Autenticación con Microsoft OAuth

### Descripción General

El sistema soporta autenticación con Microsoft OAuth (Azure AD) tanto para web como para WhatsApp, integrándose perfectamente con el sistema unificado de sesiones.

### Stored Procedures Utilizados

#### 1. `spLoginMicrosoftAddOrEdit`
**Propósito:** Guardar o actualizar datos de una cuenta de Microsoft

**Input:**
```json
{
  "id": "uuid-microsoft",
  "mail": "usuario@company.com",
  "displayName": "Usuario Ejemplo",
  "userPrincipalName": "usuario@company.onmicrosoft.com",
  "givenName": "Usuario",
  "surname": "Ejemplo",
  "jobTitle": "Cargo",
  "department": "Departamento",
  "companyName": "Empresa",
  "officeLocation": "Oficina",
  "businessPhones": ["555-1234"],
  "mobilePhone": "555-9999",
  "tenantId": "tenant-uuid",
  "preferredLanguage": "es-MX"
}
```

**Output:**
```json
{
  "success": true,
  "operation": "INSERT|UPDATE",
  "idLoginMicrosoft": 123,
  "associationStatus": "associated|needs_association",
  "microsoftUser": {...},
  "linkedUser": {...}  // Solo si associationStatus = "associated"
}
```

**Lógica:**
1. Busca usuario Microsoft existente
2. INSERT o UPDATE según corresponda
3. Verifica asociación con `tbLogin`
4. Retorna estado de asociación

#### 2. `spLoginLoginMicrosoftAssociate`
**Propósito:** Asociar cuenta de Microsoft con usuario existente

**Input:**
```json
{
  "codeLogin": "USR001",
  "codeLoginMicrosoft": "uuid-microsoft"
}
```

**Output:**
```json
{
  "success": true,
  "message": "Cuentas asociadas exitosamente",
  "idAssociation": 789,
  "userData": {
    "idLogin": 456,
    "codeLogin": "USR001",
    "nameLogin": "Usuario",
    "phoneLogin": "5551234567",
    "emailLogin": "usuario@example.com"
  }
}
```

**Validaciones:**
- ✅ Verifica existencia de `codeLogin` y `codeLoginMicrosoft`
- ✅ Previene doble asociación
- ✅ Crea registro en `tbLoginLoginMicrosoft`

### Flujo Microsoft OAuth - Web

```
1. Usuario hace clic en "Login con Microsoft"
   ↓
2. GET /api/auth/microsoft/login
   - Redirige a Microsoft OAuth
   ↓
3. Usuario autentica en Microsoft
   ↓
4. GET /api/auth/microsoft/callback?code=xxx
   - Intercambia code por access_token
   - Consulta Microsoft Graph API
   - EXEC spLoginMicrosoftAddOrEdit
   ↓
5a. Si associationStatus = "associated":
    - Genera token JWE
    - Guarda sesión: auth_session:web:{email}
    - Redirige: /#/login?microsoft_success=true&token={jwe}
    ✅ Login automático exitoso
    
5b. Si associationStatus = "needs_association":
    - Redirige: /#/login?microsoft_pending=true&
                codeLoginMicrosoft={id}&
                displayName={name}&email={email}
    ↓
6. Frontend muestra formulario para codeLogin
   ↓
7. POST /api/auth/microsoft/associate
   Body: {codeLogin, codeLoginMicrosoft}
   - EXEC spLoginLoginMicrosoftAssociate
   - Genera token JWE
   - Guarda sesión: auth_session:web:{email}
   ✅ Asociación y login exitosos
```

### Flujo Microsoft OAuth - WhatsApp

```
1. Usuario sin auth envía mensaje
   ↓
2. Bot genera token temporal (5min)
   - Incluye: phone_number, bot_phone_number
   - Envía link de autenticación
   ↓
3. GET /api/whatsapp/auth/page?token={token}
   - Valida token
   - Construye state (base64):
     {whatsapp_token, phone_number, bot_phone_number}
   - Redirige a Microsoft OAuth con state
   ↓
4. Usuario autentica en Microsoft
   ↓
5. GET /api/auth/microsoft/callback?code=xxx&state=yyy
   - Decodifica state → detecta flujo WhatsApp
   - Intercambia code por access_token
   - Consulta Microsoft Graph API
   - EXEC spLoginMicrosoftAddOrEdit
   ↓
6a. Si associationStatus = "associated":
    - Guarda sesión: auth_session:whatsapp:{phone}
    - Elimina token temporal
    - Muestra HTML de éxito con botón WhatsApp
    ✅ Login automático exitoso
    
6b. Si associationStatus = "needs_association":
    - Muestra HTML con formulario inline
    - Usuario ingresa su codeLogin
    ↓
7. POST /api/auth/microsoft/associate/whatsapp
   Body: {codeLogin, codeLoginMicrosoft, phoneNumber, whatsappToken}
   - Valida whatsappToken
   - EXEC spLoginLoginMicrosoftAssociate
   - Guarda sesión: auth_session:whatsapp:{phone}
   - Elimina token temporal
   - Retorna éxito
   ↓
8. JavaScript muestra éxito y botón WhatsApp
   ✅ Asociación y login exitosos
```

### Endpoints Microsoft OAuth

#### `GET /api/auth/microsoft/login`
Inicia flujo OAuth con Microsoft.

**Query Parameters:**
- `whatsapp_auth`: JSON con datos de WhatsApp (opcional)

**Comportamiento:**
- Web: State solo contiene session_id
- WhatsApp: State incluye whatsapp_token, phone_number, bot_phone_number

#### `GET /api/auth/microsoft/callback`
Recibe callback de Microsoft OAuth.

**Query Parameters:**
- `code`: Authorization code de Microsoft
- `state`: Estado codificado (base64)

**Proceso:**
1. Intercambia code por tokens
2. Obtiene datos de Microsoft Graph API
3. Ejecuta `spLoginMicrosoftAddOrEdit`
4. Si `associated`: Crea sesión y retorna token/página
5. Si `needs_association`: Solicita codeLogin

#### `POST /api/auth/microsoft/associate`
Asocia cuenta Microsoft con usuario (Web).

**Body:**
```json
{
  "codeLogin": "USR001",
  "codeLoginMicrosoft": "uuid-microsoft"
}
```

**Response:**
```json
{
  "accessToken": "jwe_token_here",
  "tokenType": "Bearer",
  "expiresIn": 86400,
  "user": {...}
}
```

#### `POST /api/auth/microsoft/associate/whatsapp`
Asocia cuenta Microsoft con usuario (WhatsApp).

**Body:**
```json
{
  "codeLogin": "USR001",
  "codeLoginMicrosoft": "uuid-microsoft",
  "phoneNumber": "5491112345678",
  "whatsappToken": "temp-token"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Cuenta asociada exitosamente",
  "user": {...}
}
```

### Estructura de Base de Datos

#### Tabla: `tbLoginMicrosoft`
```sql
idLoginMicrosoft        INT PRIMARY KEY
codeLoginMicrosoft      NVARCHAR(500)  -- UUID de Microsoft
nameLoginMicrosoft      NVARCHAR(255)  -- displayName
emailLoginMicrosoft     NVARCHAR(500)  -- email
userPrincipalName       NVARCHAR(500)
jobTitle                NVARCHAR(255)
department              NVARCHAR(255)
companyName             NVARCHAR(255)
microsoftTenantId       NVARCHAR(100)
accessToken             NVARCHAR(MAX)
refreshToken            NVARCHAR(MAX)
tokenExpiresAt          DATETIME2
lastLoginDate           DATETIME2
loginCount              INT
isActive                BIT
```

#### Tabla: `tbLoginLoginMicrosoft` (N:N)
```sql
idLoginLoginMicrosoft   INT PRIMARY KEY
idLogin                 INT → tbLogin
idLoginMicrosoft        INT → tbLoginMicrosoft
createdDate             DATETIME2
```

### Sesiones Microsoft en Redis

Una vez autenticado con Microsoft, el sistema crea sesiones exactamente iguales a las demás:

**Web:**
```
Key: auth_session:web:usuario@company.com
TTL: 86400 segundos
Data: {
  "codeLogin": "USR001",
  "name": "Usuario Ejemplo",
  "email": "usuario@company.com",
  "session_type": "web",
  "microsoft_id": "uuid-microsoft",
  ...
}
```

**WhatsApp:**
```
Key: auth_session:whatsapp:5491112345678
TTL: 86400 segundos
Data: {
  "codeLogin": "USR001",
  "name": "Usuario Ejemplo",
  "email": "usuario@company.com",
  "session_type": "whatsapp",
  "microsoft_id": "uuid-microsoft",
  ...
}
```

### Ventajas de la Unificación

1. **Mismo sistema de sesiones:** Microsoft usa Redis igual que login tradicional
2. **Logout funciona igual:** DELETE sesión de Redis invalida la autenticación
3. **Refresh funciona igual:** Extiende sesión sin re-autenticar
4. **Validación consistente:** `get_current_user()` valida todas las sesiones igual
5. **Código reutilizable:** SPs centralizan lógica de asociación

## 🎉 Resumen Final

**Sistema de autenticación ahora:**
- ✅ Unificado entre web y WhatsApp
- ✅ Soporta login tradicional y Microsoft OAuth
- ✅ Sesiones reales de 24 horas en Redis
- ✅ Logout funciona correctamente
- ✅ Código centralizado y mantenible
- ✅ Extensible a nuevos canales
- ✅ Seguridad mejorada
- ✅ Stored Procedures para datos Microsoft
- ✅ Asociación de cuentas con validación

**Próximos pasos sugeridos:**
1. Testear todos los flujos (web tradicional, web Microsoft, WhatsApp Microsoft)
2. Monitorear Redis para ver sesiones activas
3. Considerar agregar endpoints de administración de sesiones
4. Implementar refresh automático antes de expiración
5. Verificar que SPs manejen todos los casos edge
