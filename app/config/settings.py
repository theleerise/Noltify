import os
from pathlib import Path


# ---------------------------------------------------------
# RUTAS BASE
# ---------------------------------------------------------

CONFIG_DIR = Path(__file__).resolve().parent
APP_DIR = CONFIG_DIR.parent
PROJECT_DIR = APP_DIR.parent
BASE_DIR = APP_DIR

FRONTEND_DIR = APP_DIR / "frontend"
PAGE_DIR = FRONTEND_DIR / "page"
MACRO_DIR = FRONTEND_DIR / "macro"
STATIC_DIR = FRONTEND_DIR / "static"
STATIC_ROOT_DIR = PROJECT_DIR / "staticfiles"
MEDIA_ROOT_DIR = PROJECT_DIR / "media"


# ---------------------------------------------------------
# ENTORNO LOCAL
# ---------------------------------------------------------

def load_local_env(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        os.environ.setdefault(key, value)


load_local_env(PROJECT_DIR / ".env")

STATIC_ROOT_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_ROOT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# SEGURIDAD
# ---------------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-this-key")

DEBUG = os.getenv("DEBUG", "0") == "1"

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["https://*.railway.app"]

# ---------------------------------------------------------
# APLICACIONES INSTALADAS
# ---------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]


# ---------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ---------------------------------------------------------
# URLS / ENTRADA PRINCIPAL
# ---------------------------------------------------------

ROOT_URLCONF = "config.urls"


# ---------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [
            FRONTEND_DIR,
            PAGE_DIR,
            MACRO_DIR,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "config.jinja2.environment",
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            FRONTEND_DIR,
            PAGE_DIR,
            MACRO_DIR,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ---------------------------------------------------------
# APLICACIONES WSGI / ASGI
# ---------------------------------------------------------

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ---------------------------------------------------------
# BASE DE DATOS
# ---------------------------------------------------------


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "noltify"),
        "USER": os.getenv("DB_USER", "noltify_app_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "88908890"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# ---------------------------------------------------------
# VALIDADORES DE CONTRASEÑA
# ---------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ---------------------------------------------------------
# INTERNACIONALIZACIÓN
# ---------------------------------------------------------

LANGUAGE_CODE = "es-es"

TIME_ZONE = "Europe/Madrid"

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------
# ARCHIVOS ESTÁTICOS
# ---------------------------------------------------------

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    STATIC_DIR,
]

STATIC_ROOT = STATIC_ROOT_DIR
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------
# CLAVE PRIMARIA POR DEFECTO
# ---------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
