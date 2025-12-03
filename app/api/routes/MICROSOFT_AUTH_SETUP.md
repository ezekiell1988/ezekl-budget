# Configuración de Microsoft Authentication

## Problema: Redirect URI no coincide

Si ves este error:
```
AADSTS50011: The redirect URI 'http://localhost:8000/api/v1/auth/microsoft/callback' 
specified in the request does not match the redirect URIs configured for the application
```

## Solución

Debes registrar la URL de callback en el portal de Azure:

### 1. Ir al Portal de Azure
Visita: https://portal.azure.com

### 2. Navegar a Microsoft Entra ID (Azure Active Directory)
- Selecciona "Microsoft Entra ID" en el menú lateral
- Selecciona "App registrations"
- Busca tu aplicación: **budget-app-temp-ezequiel-dev**
- Client ID: `b5c4ceb3-9bf1-4a1f-8e4e-72b852d771e9`

### 3. Agregar Redirect URI
En la configuración de tu aplicación:

1. Ve a **Authentication** en el menú lateral
2. En la sección **Platform configurations**, busca **Web**
3. Haz clic en **Add URI**
4. Agrega las siguientes URIs de acuerdo a tu entorno:

#### Desarrollo (Puerto 8000):
```
http://localhost:8000/api/v1/auth/callback
http://127.0.0.1:8000/api/v1/auth/callback
```

#### Producción:
```
https://budget.ezekl.com/api/v1/auth/callback
```

5. Haz clic en **Save**

### 4. Verificar configuración del .env

Asegúrate de que tu archivo `.env` tenga el puerto correcto:

```env
PORT=8000
ENVIRONMENT=development
```

La aplicación automáticamente construirá la URL de callback correcta:
- **Desarrollo**: `http://localhost:8000/api/v1/auth/microsoft/callback`
- **Producción**: `https://budget.ezekl.com/api/v1/auth/microsoft/callback`

### 5. Reiniciar el servidor

Después de cambiar la configuración:
```bash
python3 ./start.py
```

## Content Security Policy (CSP)

La aplicación ahora incluye headers de CSP que permiten:
- Scripts de Microsoft Auth (*.msauth.net, *.microsoft.com, etc.)
- PDF.js desde CDN
- WebSockets locales
- Conexiones a Azure OpenAI y Dynamics 365

Si encuentras problemas con recursos bloqueados, revisa la consola del navegador.

## URLs Configuradas

### Microsoft Authorization Endpoint:
```
https://login.microsoftonline.com/2f80d4e1-da0e-4b6d-84da-30f67e280e4b/oauth2/v2.0/authorize
```

### Microsoft Token Endpoint:
```
https://login.microsoftonline.com/2f80d4e1-da0e-4b6d-84da-30f67e280e4b/oauth2/v2.0/token
```

### Redirect URI (Desarrollo):
```
http://localhost:8000/api/v1/auth/callback
```

## Troubleshooting

### Error: "redirect_uri mismatch"
- Verifica que el puerto en `.env` coincida con las URIs registradas en Azure
- Limpia la caché del navegador
- Reinicia el servidor

### Error: CSP violations
- Revisa la consola del navegador
- Los CSP warnings son normales en desarrollo
- En producción, ajusta el CSP según necesites

### WebSocket no conecta
- Verifica que el puerto sea el correcto
- En Windows, asegúrate de que se use 127.0.0.1 en lugar de localhost para WebSockets
- Revisa los logs del servidor
