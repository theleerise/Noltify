"""
Punto de entrada para comandos de gestión del proyecto.

Este módulo configura el entorno de Django y delega la ejecución en la utilidad de lnea de comandos correspondiente.
"""
import os
import sys
from pathlib import Path


def main() -> None:
    """
    Inicia la ejecución del comando principal del proyecto.

    Configura el entorno necesario y delega la ejecución al mecanismo de gestión correspondiente.

    Returns:
        _type_: None: El método ejecuta el comando solicitado dentro del entorno configurado.
    """
    project_root = Path(__file__).resolve().parent
    app_path = project_root / "app"

    sys.path.insert(0, str(app_path))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
