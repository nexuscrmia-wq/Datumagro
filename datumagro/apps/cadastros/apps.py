# datumagro/apps/cadastros/apps.py

from django.apps import AppConfig

class CadastrosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datumagro.apps.cadastros'
    verbose_name = 'Cadastros Gerais'