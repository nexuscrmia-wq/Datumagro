# datumagro/settings.py
"""
Django settings for datumagro project.
Production-grade configuration with global performance improvements.
"""

import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv
import logging.config

load_dotenv()

# Optional: initialize Sentry if SENTRY_DSN is provided in the environment
try:
    import sentry_sdk  # type: ignore
    from sentry_sdk.integrations.django import DjangoIntegration  # type: ignore

    SENTRY_DSN = os.getenv('SENTRY_DSN')
    if SENTRY_DSN:
        try:
            traces_rate = float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.0'))
        except Exception:
            traces_rate = 0.0
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=traces_rate,
            send_default_pii=os.getenv('SENTRY_SEND_PII', 'False') == 'True'
        )
except ImportError:
    # If sentry-sdk is not installed or initialization fails, continue without Sentry
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# 🚀 SECURITY: Use environment variables for sensitive data
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev-only')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
IS_PRODUCTION = os.getenv('ENVIRONMENT', 'production') == 'production' or bool(os.getenv('RENDER'))

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,10.0.2.2').split(',')
# Render
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
# Railway — adiciona o domínio público e o host do health check interno
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
if os.getenv('RAILWAY_PROJECT_ID'):
    ALLOWED_HOSTS += ['healthcheck.railway.app', '.railway.app']
# Domínio personalizado
ALLOWED_HOSTS += ['datumagro.com.br', 'www.datumagro.com.br']

CSRF_TRUSTED_ORIGINS = []
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')
if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RAILWAY_PUBLIC_DOMAIN}')
extra_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if extra_origins:
    CSRF_TRUSTED_ORIGINS += [o.strip() for o in extra_origins.split(',') if o.strip()]
CSRF_TRUSTED_ORIGINS += ['https://datumagro.com.br', 'https://www.datumagro.com.br']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # 🚀 Libs de Terceiros
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'drf_spectacular_sidecar',

    # 🎯 Nossos Apps (Todos eles)
    'datumagro.apps.usuarios.apps.UsuariosConfig',
    'datumagro.apps.core.apps.CoreConfig',
    'datumagro.apps.assinaturas.apps.AssinaturasConfig',
    'datumagro.apps.cadastros.apps.CadastrosConfig',
    'datumagro.apps.financeiro.apps.FinanceiroConfig',
    'datumagro.apps.integracoes.apps.IntegracoesConfig',
    'datumagro.apps.inteligencia.apps.InteligenciaConfig',
    'datumagro.apps.notificacoes.apps.NotificacoesConfig',
    'datumagro.apps.operacional.apps.OperacionalConfig',
    'datumagro.apps.rastreabilidade.apps.RastreabilidadeConfig',
    'datumagro.apps.relatorios.apps.RelatoriosConfig',
    'datumagro.apps.logistica.apps.LogisticaConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 🚀 WhiteNoise para arquivos estáticos comprimidos
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # 🚀 CORS primeiro na chain
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'datumagro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'datumagro.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=int(os.getenv('CONN_MAX_AGE', '0'))
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'usuarios.Usuario'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# 🚀 MELHORIA DE PERFORMANCE: CACHE
# Em produção, use Redis. Em desenvolvimento, use cache em memória.
if IS_PRODUCTION and os.getenv('REDIS_URL'):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv('REDIS_URL'),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
            },
            "KEY_PREFIX": "datumagro",
            "TIMEOUT": 300,
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
else:
    # Desenvolvimento: Cache em memória
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "datumagro-cache",
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.db"

# 🚀 CONFIGURAÇÕES DRF (Segurança + Performance)
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # 🚀 RATE LIMITING (Proteção contra ataques)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',    # Visitantes: 100 requests/hora
        'user': '1000/hour'    # Usuários: 1000 requests/hora
    },
    
    # 🚀 VALIDAÇÃO E TRATAMENTO DE ERROS
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# 🚀 CONFIGURAÇÃO JWT (Autenticação)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# 🚀 LOGGING JSON PROFISSIONAL (Observabilidade)
LOGGING_CONFIG = None
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s %(filename)s %(funcName)s %(lineno)s %(module)s %(pathname)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json' if IS_PRODUCTION else 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'datumagro': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
})


# 🚀 CONFIGURAÇÕES DE EMAIL (Notificações)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'DatumAgro <contato@datumagro.com.br>')

# Se não houver credenciais de email, usar backend de console para dev
if not EMAIL_HOST_USER:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configurações do drf-spectacular (OpenAPI / Swagger)
SPECTACULAR_SETTINGS = {
    'TITLE': 'DatumAgro API',
    'DESCRIPTION': '''
API completa para gestão pecuária DatumAgro.

Características principais:
- Gestão de usuários e propriedades
- Cadastro completo de animais
- Controle de pesagens e métricas
- Autenticação JWT
- Integração com aplicativo Flutter
''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
        'tryItOutEnabled': True,
        'displayRequestDuration': True,
        'syntaxHighlight': True,
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}

# 🚀 CORS Configuration
if IS_PRODUCTION:
    # Apps mobile não enviam Origin header — CORS não se aplica a eles.
    # Liberar todas as origens é seguro aqui porque a autenticação é via JWT.
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = []
else:
    # Desenvolvimento: Permitir todos os origins
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://10.0.2.2:8000",  # Android emulator
        "http://10.0.2.2:8080",  # Android emulator
    ]

CORS_ALLOW_CREDENTIALS = True

# Credenciais Twilio (do .env)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

# FRONTEND URL usado nos e-mails de recuperação
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# ============================================================================
# SECURITY SETTINGS FOR PRODUCTION
# ============================================================================

if IS_PRODUCTION:
    # Railway/Render terminam TLS no edge e encaminham HTTP internamente.
    # SECURE_PROXY_SSL_HEADER garante que Django saiba que a conexão original era HTTPS.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Não redirecionar HTTP→HTTPS aqui — o proxy já faz isso.
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # Development mode - less strict
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False