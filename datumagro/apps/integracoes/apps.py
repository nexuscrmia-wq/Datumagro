# datumagro/apps/integracoes/apps.py

from django.apps import AppConfig

class IntegracoesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datumagro.apps.integracoes'
    verbose_name = 'Integrações com Hardware'