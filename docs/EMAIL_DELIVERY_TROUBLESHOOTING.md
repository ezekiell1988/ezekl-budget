"""
Guía para resolver problemas de entrega de emails
"""

# PROBLEMA: El email no llega a la bandeja de entrada

## ✅ Confirmado: El email se envió correctamente al servidor SMTP
```
reply: b'250 2.0.0 Ok: queued as 17EBBA8022F\r\n'
```

Esto significa que el servidor SMTP de Mailhostbox aceptó y puso en cola el email.

## ❓ Posibles causas de no entrega:

### 1. Email en carpeta de SPAM/Correo no deseado (MÁS PROBABLE)
**Solución:**
- Revisa la carpeta de **Spam/Correo no deseado** en `ezekiell1988@hotmail.com`
- Si está ahí, márcalo como "No es spam" para futuros emails

### 2. Hotmail/Outlook bloqueando el dominio `ezekl.com`
**Razón:** El dominio `ezekl.com` puede no tener registros SPF/DKIM configurados
**Solución:**
- Configurar registros DNS SPF y DKIM para `ezekl.com`
- O usar un servicio de email transaccional (SendGrid, Mailgun, etc.)

### 3. Retraso en la entrega
**Solución:**
- Esperar 5-10 minutos (a veces hay retrasos)

### 4. Filtros de Outlook muy estrictos
**Solución temporal:**
- Agregar `info@ezekl.com` a contactos seguros
- Revisar configuración de filtros en Outlook

## 🔧 Verificaciones adicionales:

### Ver el contenido del email que se envió:
El email contiene:
```
De: info@ezekl.com
Para: ezekiell1988@hotmail.com
Asunto: Código de acceso - Ezekl Budget
Token: 43621
```

### Probar con otro email:
```bash
python tests/test_request_token.py
```

Luego revisa un email diferente (Gmail, etc.) para verificar si es problema específico de Hotmail.

## 🚀 Solución recomendada: SendGrid

Para producción, usar un servicio profesional de emails transaccionales:

### SendGrid (Gratis hasta 100 emails/día):
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=TU_API_KEY_DE_SENDGRID
SMTP_FROM=noreply@ezekl.com
```

Ventajas:
- ✅ Alta tasa de entrega
- ✅ No cae en spam
- ✅ Reportes de entrega
- ✅ Gratis para desarrollo

## 📝 Siguientes pasos:

1. **PRIMERO:** Revisa la carpeta de SPAM en Hotmail
2. **Si está en spam:** Márcalo como seguro
3. **Si no aparece:** Espera 5-10 minutos
4. **Si sigue sin llegar:** Prueba con un email de Gmail
5. **Para producción:** Configura SendGrid o similar
