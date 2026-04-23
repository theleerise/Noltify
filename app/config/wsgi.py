"""
Punto de entrada WSGI del proyecto.

Este módulo expone la aplicación WSGI utilizada por servidores compatibles para desplegar el proyecto.
"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()