# datumagro/settings_test.py
"""
Configurações de teste - Sobrescreve configurações para usar em memória
"""
from .settings import *

# ✅ Use cache em memória para testes (não precisa de Redis)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "datumagro-cache",
    }
}

# ✅ Use sessão em banco de dados para testes (em vez de cache Redis)
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# ✅ Desabilite throttling para testes
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []

# ✅ Use uma senha simples para testes (não use em produção!)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

print("✅ Using TEST settings with in-memory cache and database sessions")
