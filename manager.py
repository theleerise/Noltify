import os
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent
    app_path = project_root / "app"

    sys.path.insert(0, str(app_path))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
