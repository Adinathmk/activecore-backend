from pathlib import Path
from datetime import timedelta
import environ
import stripe

# --------------------------------------------------
# BASE DIRECTORY
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --------------------------------------------------
# ENVIRONMENT VARIABLES
# --------------------------------------------------

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# --------------------------------------------------
# SECURITY
# --------------------------------------------------

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# --------------------------------------------------
# DJANGO CORE
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

INSTALLED_APPS = [

    # ASGI / WebSocket
    "daphne",
    "channels",

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third party
    "drf_spectacular",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "cloudinary",
    "cloudinary_storage",

    # Local apps
    "apps.notifications",
    "apps.accounts",
    "apps.products",
    "apps.wishlist",
    "apps.cart",
    "apps.orders",
    "apps.reports",
]

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",
    
    "corsheaders.middleware.CorsMiddleware",


    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------------------
# URL / ASGI
# --------------------------------------------------

ROOT_URLCONF = "core.urls"

WSGI_APPLICATION = "core.wsgi.application"

ASGI_APPLICATION = "core.asgi.application"

# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

DATABASES = {
    "default": env.db()
}

DATABASES["default"]["CONN_MAX_AGE"] = 60

# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [

    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},

    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},

    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},

    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# --------------------------------------------------
# CLOUDINARY STORAGE
# --------------------------------------------------

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": env("CLOUDINARY_API_KEY"),
    "API_SECRET": env("CLOUDINARY_API_SECRET"),
}

# --------------------------------------------------
# DJANGO REST FRAMEWORK
# --------------------------------------------------

REST_FRAMEWORK = {

    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.StandardResultsPagination",

    "PAGE_SIZE": 12,

    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.accounts.authentication.CookieJWTAuthentication",
    ),

    "DEFAULT_THROTTLE_RATES": {
        "anon": "5/minute"
    }
}

# --------------------------------------------------
# JWT SETTINGS
# --------------------------------------------------

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,

    "BLACKLIST_AFTER_ROTATION": True,

    "AUTH_HEADER_TYPES": ("Bearer",),

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),

    "UPDATE_LAST_LOGIN": True,
}

# --------------------------------------------------
# API DOCS
# --------------------------------------------------

SPECTACULAR_SETTINGS = {

    "TITLE": "Ecommerce API",

    "DESCRIPTION": "Backend API",

    "VERSION": "1.0.0",

    "SERVE_INCLUDE_SCHEMA": False,

    "SECURITY": [{"BearerAuth": []}],

    "COMPONENT_SPLIT_REQUEST": True,
}

# --------------------------------------------------
# CORS / CSRF
# --------------------------------------------------

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# --------------------------------------------------
# EMAIL
# --------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = env("EMAIL_HOST")

EMAIL_PORT = env.int("EMAIL_PORT", default=587)

EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)

EMAIL_HOST_USER = env("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# --------------------------------------------------
# STRIPE
# --------------------------------------------------

STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")

STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET")

STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY")

stripe.api_key = STRIPE_SECRET_KEY

# --------------------------------------------------
# TWILIO
# --------------------------------------------------

TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID")

TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN")

TWILIO_WHATSAPP_NUMBER = env("TWILIO_WHATSAPP_NUMBER")

# --------------------------------------------------
# GOOGLE AUTH
# --------------------------------------------------

GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")

# --------------------------------------------------
# CHANNELS
# --------------------------------------------------

CHANNEL_LAYERS = {

    "default": {

        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

LOGS_DIR = BASE_DIR / "logs"

LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {

    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {

        "verbose": {

            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",

            "style": "{",
        },

        "simple": {

            "format": "{levelname} {message}",

            "style": "{",
        },
    },

    "handlers": {

        "console": {

            "class": "logging.StreamHandler",

            "formatter": "simple",
        },

        "file": {

            "class": "logging.handlers.RotatingFileHandler",

            "filename": LOGS_DIR / "django.log",

            "maxBytes": 1024 * 1024 * 5,

            "backupCount": 5,

            "formatter": "verbose",
        },
    },

    "root": {

        "handlers": ["console", "file"],

        "level": "INFO",
    },
}