# Templates de Autenticación

Esta carpeta contiene los templates Jinja2 para las páginas HTML utilizadas en el flujo de autenticación de Microsoft y WhatsApp.

## Templates Disponibles

### Errores Generales

- **`whatsapp_error.html`**: Página de error genérica para flujos de WhatsApp
  - Variables: `error_title`, `error_message`

- **`microsoft_oauth_error.html`**: Error de autenticación OAuth de Microsoft
  - Variables: `error_description`

- **`microsoft_no_code.html`**: Error cuando no se recibe código de autorización

- **`microsoft_session_expired.html`**: Sesión de autenticación expirada

- **`microsoft_generic_error.html`**: Error genérico de Microsoft
  - Variables: `error_message`

### Asociación de Cuentas

- **`microsoft_needs_association.html`**: Cuenta Microsoft no asociada a cuenta del sistema
  - Variables: `user_email`

- **`whatsapp_association_form.html`**: Formulario para asociar cuenta Microsoft con usuario existente (WhatsApp)
  - Variables: `display_name`, `email`, `wa_number`, `code_login_microsoft`, `phone_number`, `whatsapp_token`

### Páginas de Éxito

- **`whatsapp_auth_success.html`**: Autenticación exitosa de WhatsApp
  - Variables: `user_name`, `user_email`, `phone_number`, `wa_number`

- **`whatsapp_unknown_error.html`**: Error desconocido en autenticación WhatsApp

## Uso

Los templates se utilizan en el módulo `app/api/auth/__init__.py` mediante Jinja2Templates:

```python
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Ejemplo de uso
html_content = templates.TemplateResponse(
    "auth/whatsapp_error.html",
    {
        "request": {},
        "error_title": "Error de Autenticación",
        "error_message": "No se pudo completar la autenticación.",
    },
).body.decode("utf-8")

return HTMLResponse(content=html_content, status_code=400)
```

## Beneficios

1. **Separación de responsabilidades**: El código Python está separado del HTML
2. **Mantenimiento más fácil**: Los cambios en diseño no requieren tocar el código Python
3. **Reutilización**: Los templates pueden ser reutilizados en diferentes flujos
4. **Consistencia**: Diseño consistente en todas las páginas de autenticación
5. **Testeo**: Más fácil probar la lógica sin preocuparse por el HTML

## Estilos

Todos los templates utilizan:
- Diseño responsivo con meta viewport
- Gradiente de fondo (#667eea a #764ba2)
- Tipografía: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
- Contenedor blanco centralizado con sombra
- Iconos emoji para mejor UX
