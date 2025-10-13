# datumagro/apps/financeiro/apps.py

from django.apps import AppConfig

class FinanceiroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datumagro.apps.financeiro'
    verbose_name = 'Controle Financeiro'