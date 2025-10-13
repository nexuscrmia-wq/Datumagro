# datumagro/apps/rastreabilidade/apps.py

from django.apps import AppConfig

class RastreabilidadeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datumagro.apps.rastreabilidade'
    verbose_name = 'Rastreabilidade e Selo de Origem'