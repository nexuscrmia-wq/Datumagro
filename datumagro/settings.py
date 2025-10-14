# datumagro/settings.py

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (só funciona no seu PC)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# A chave secreta agora é lida do ambiente, o que é mais seguro
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev-only')

# O modo Debug será False na produção (no Render) e True no seu computador
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Lista de endereços permitidos. O Render adicionará o seu endereço público aqui.
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# --- APLICAÇÕES INSTALADAS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Adicionado para WhiteNoise
    'django.contrib.staticfiles',
    
    # Bibliotecas de Terceiros
    'rest_framework',
    'rest_framework.authtoken',
    
    # Nossos 11 Apps
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Adicionado para WhiteNoise
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

# --- BANCO DE DADOS ---
# Usa dj-database-url para ser flexível entre o SQLite local e o PostgreSQL do Render
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
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

# --- ARQUIVOS ESTÁTICOS E DE MÍDIA ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- CONFIGURAÇÕES DO PROJETO ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# INFORMA AO DJANGO PARA USAR NOSSO MODELO DE USUÁRIO CUSTOMIZADO
AUTH_USER_MODEL = 'usuarios.Usuario'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# --- CHAVES DE API EXTERNAS (LIDAS DO AMBIENTE) ---
# E-mail (ex: Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
