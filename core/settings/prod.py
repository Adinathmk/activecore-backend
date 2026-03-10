from .base import *

# ==================================================
# PRODUCTION SAFETY
# ==================================================

if DEBUG:
    raise Exception("DEBUG must be False in production")

# ==================================================
# HTTPS / SSL
# ==================================================

SECURE_SSL_REDIRECT = True

# When behind nginx / reverse proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ==================================================
# COOKIE SECURITY (CRITICAL FOR VERCEL FRONTEND)
# ==================================================

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
JWT_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
JWT_COOKIE_HTTPONLY = True

# Cross-site cookies required for Vercel → AWS
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"
JWT_COOKIE_SAMESITE = "None"

# Cookie domain (backend domain)
SESSION_COOKIE_DOMAIN = "activecore.duckdns.org"
CSRF_COOKIE_DOMAIN = "activecore.duckdns.org"
JWT_COOKIE_DOMAIN = "activecore.duckdns.org"

# ==================================================
# HSTS SECURITY
# ==================================================

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ==================================================
# BROWSER SECURITY HEADERS
# ==================================================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

SECURE_REFERRER_POLICY = "same-origin"

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_RESOURCE_POLICY = "same-origin"

# ==================================================
# CORS (FRONTEND → BACKEND)
# ==================================================

CORS_ALLOW_CREDENTIALS = True

# loaded from .env
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

# ==================================================
# SESSION SETTINGS
# ==================================================

SESSION_ENGINE = "django.contrib.sessions.backends.db"

SESSION_COOKIE_AGE = 1209600  # 2 weeks

SESSION_SAVE_EVERY_REQUEST = False

# ==================================================
# STATIC FILES (NGINX SERVED)
# ==================================================

STATIC_ROOT = BASE_DIR / "staticfiles"

# ==================================================
# LOGGING (Production)
# ==================================================

LOGGING["root"]["level"] = "INFO"
