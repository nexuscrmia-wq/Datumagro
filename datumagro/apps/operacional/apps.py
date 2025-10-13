# datumagro/apps/operacional/apps.py

from django.apps import AppConfig

class OperacionalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datumagro.apps.operacional'
    verbose_name = 'Operacional da Fazenda'