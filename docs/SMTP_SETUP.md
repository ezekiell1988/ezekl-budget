# Guía: Configurar SMTP para Office 365

## Problema
El error `5.7.139 Authentication unsuccessful` indica que Office 365 está bloqueando la autenticación básica SMTP.

## Solución 1: Usar App Password (Recomendado)

### Pasos:
1. Ir a https://account.microsoft.com/security
2. Iniciar sesión con la cuenta: `adminsp@itqscr.onmicrosoft.com`
3. Ir a **Security** > **Advanced security options**
4. En **Additional security**, seleccionar **App passwords**
5. Click en **Create a new app password**
6. Copiar el password generado (formato: xxxx-xxxx-xxxx-xxxx)
7. Actualizar el archivo `.env`:
   ```
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ```

## Solución 2: Habilitar Autenticación Básica (No Recomendado)

### Para administradores de Office 365:
1. Ir al Centro de administración de Microsoft 365
2. **Settings** > **Org settings** > **Modern authentication**
3. Habilitar **SMTP AUTH** para el buzón específico

### Comando PowerShell (requiere permisos admin):
```powershell
Set-CASMailbox -Identity adminsp@itqscr.onmicrosoft.com -SmtpClientAuthenticationDisabled $false
```

## Solución 3: Usar otro proveedor SMTP

### Gmail:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
SMTP_FROM=tu-email@gmail.com
```

### SendGrid (Recomendado para producción):
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=tu-api-key-de-sendgrid
SMTP_FROM=tu-email-verificado@dominio.com
```

## Verificar configuración

Después de actualizar las credenciales:
```bash
python tests/test_smtp.py
```

## Referencias
- [Microsoft: Autenticación básica y Exchange Online](https://docs.microsoft.com/en-us/exchange/clients-and-mobile-in-exchange-online/authenticated-client-smtp-submission)
- [Crear App Password de Microsoft](https://support.microsoft.com/en-us/account-billing/using-app-passwords-with-apps-that-don-t-support-two-step-verification-5896ed9b-4263-e681-128a-a6f2979a7944)
