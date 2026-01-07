"""
Utilidades para renderizar templates de email usando Jinja2.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any

# Directorio donde están los templates de emails
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "emails"

# Configurar entorno de Jinja2
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)


def render_email_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Renderiza un template de email con el contexto proporcionado.
    
    Args:
        template_name: Nombre del archivo de template (ej: 'request_token.html')
        context: Diccionario con variables para el template
        
    Returns:
        HTML renderizado como string
        
    Example:
        html = render_email_template('request_token.html', {
            'user_name': 'Juan Pérez',
            'token': '12345'
        })
    """
    template = jinja_env.get_template(template_name)
    return template.render(**context)


def render_request_token_email(user_name: str, token: str) -> tuple[str, str]:
    """
    Renderiza el email de solicitud de token en versiones HTML y texto plano.
    
    Args:
        user_name: Nombre del usuario
        token: Token generado
        
    Returns:
        Tuple con (html_content, text_content)
    """
    context = {
        'user_name': user_name,
        'token': token
    }
    
    html_content = render_email_template('request_token.html', context)
    text_content = render_email_template('request_token.txt', context)
    
    return html_content, text_content
