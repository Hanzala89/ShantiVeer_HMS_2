from pathlib import Path
import os

# Load .env file if python-dotenv is installed (development convenience)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'ShantiVeer-hms-dev-key-change-in-production')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# Development helper: allow demo password/admin reset workflows to run locally
# without requiring DJANGO_DEBUG=true in .env.
ALLOW_DEMO_SETUP = os.environ.get('ALLOW_DEMO_SETUP', 'true').lower() == 'true'

# FIXED: removed wildcard '*' from default — only safe for local dev
_raw_hosts = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(',') if h.strip()]

# Ensure local development works even if ALLOWED_HOSTS in .env is incomplete
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS + ['127.0.0.1', 'localhost']))

# Security headers (production only)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    X_FRAME_OPTIONS = 'SAMEORIGIN'

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 28800  # 8 hours

# ─── Check optional packages ─────────────────────────────────────────────────
try:
    import whitenoise
    _WHITENOISE = True
except ImportError:
    _WHITENOISE = False

# ─── Apps ────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'accounts',
    'core',
    'opd',
    'ipd',
    'lab',
    'pharmacy',
    'prescription',
    'uhid',
    'masterdata',
    'income',
]

# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]

if _WHITENOISE:
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

MIDDLEWARE += [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ShantiVeer_hms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.hospital_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'ShantiVeer_hms.wsgi.application'

# ─── Database (SQLite by default, MySQL optional) ───────────────────────────
USE_MYSQL = os.environ.get('USE_MYSQL', 'False').lower() == 'true'

if USE_MYSQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'ShantiVeer_db'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'CONN_MAX_AGE': 60,
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'database' / 'ShantiVeer_db.sqlite3',
        }
    }

# ─── Cache ───────────────────────────────────────────────────────────────────
# PRODUCTION NOTE: LocMemCache is per-process — brute-force counters and OTP
# tokens will NOT be shared across multiple Gunicorn workers.
# For production with 2+ workers, switch to Redis:
#
#   pip install django-redis
#
#   CACHES = {
#       'default': {
#           'BACKEND': 'django_redis.cache.RedisCache',
#           'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#           'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
#       }
#   }
#
# Set REDIS_URL in your .env to enable this.
_redis_url = os.environ.get('REDIS_URL', '')

if _redis_url:
    try:
        import django_redis  # noqa: F401
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': _redis_url,
                'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
            }
        }
    except ImportError:
        import warnings
        warnings.warn(
            'REDIS_URL is set but django-redis is not installed. '
            'Falling back to LocMemCache — brute-force/OTP state will not '
            'be shared across workers. Run: pip install django-redis',
            RuntimeWarning,
            stacklevel=1,
        )
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'shantiveer-hms-cache',
            }
        }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'shantiveer-hms-cache',
        }
    }

# ─── Password Validation ─────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalisation ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ─── Static & Media ──────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'statics']
STATIC_ROOT = BASE_DIR / 'staticfiles_collected'

if _WHITENOISE:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Authentication ───────────────────────────────────────────────────────────
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'accounts:login'

LOGIN_ATTEMPTS_LIMIT = int(os.environ.get('LOGIN_ATTEMPTS_LIMIT', '5'))
LOGIN_LOCKOUT_DURATION = int(os.environ.get('LOGIN_LOCKOUT_DURATION', '300'))

# ─── REST Framework ───────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '200/hour',
    },
}

# ─── Hospital Info ────────────────────────────────────────────────────────────
HOSPITAL_NAME = os.environ.get('HOSPITAL_NAME', 'ABC Hospital')
HOSPITAL_ADDRESS = os.environ.get('HOSPITAL_ADDRESS', 'Main Road, Thana Bhawan, Near Bus Stand')
HOSPITAL_PHONE = os.environ.get('HOSPITAL_PHONE', '9876543210')

# ─── Email ────────────────────────────────────────────────────────────────────
# FIXED: default is now smtp so OTP login works out of the box once
# EMAIL_HOST_USER / EMAIL_HOST_PASSWORD are set in .env.
# Falls back to console only in DEBUG mode so dev still works without SMTP.
_default_email_backend = (
    'django.core.mail.backends.console.EmailBackend'
    if DEBUG
    else 'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', _default_email_backend)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', '')
PASSWORD_RESET_TIMEOUT = 86400

# Warn loudly at startup if production email isn't configured
if not DEBUG and not EMAIL_HOST_USER:
    import warnings
    warnings.warn(
        'EMAIL_HOST_USER is not set. OTP-based login and password reset '
        'will not work in production. Set EMAIL_HOST_USER and '
        'EMAIL_HOST_PASSWORD in your environment.',
        RuntimeWarning,
        stacklevel=1,
    )

# ─── Logging ─────────────────────────────────────────────────────────────────
logs_dir = BASE_DIR / 'logs'
logs_dir.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logs_dir / 'hms.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'WARNING'),
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}