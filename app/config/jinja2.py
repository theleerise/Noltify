"""
Configuración auxiliar del entorno Jinja2 del proyecto.

Este módulo prepara el entorno de plantillas Jinja2 y registra los componentes adicionales utilizados por la interfaz.
"""
from jinja2 import Environment
from django.templatetags.static import static
from django.urls import reverse

def environment(**options):
    """
    Crea y configura el entorno Jinja2 utilizado por la aplicación.

    Registra en el entorno las utilidades globales necesarias para resolver
    recursos estáticos y URLs desde las plantillas.

    Args:
        **options: Parámetros de configuración que Django envía al inicializar
            el entorno de plantillas.

    Returns:
        Environment: Entorno Jinja2 listo para usarse en el renderizado de
        plantillas.
    """
    env = Environment(**options)
    env.globals.update({
        "static": static,
        "url": reverse,
    })
    return env
