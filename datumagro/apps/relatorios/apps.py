# datumagro/apps/relatorios/apps.py

from django.apps import AppConfig

class RelatoriosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datumagro.apps.relatorios'
    verbose_name = 'Geração de Relatórios'