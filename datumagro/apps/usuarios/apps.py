# datumagro/apps/usuarios/apps.py

from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datumagro.apps.usuarios'
    verbose_name = 'Gestão de Usuários e Perfis'

    def ready(self):
        # Importa os signals quando o app estiver pronto
        import datumagro.apps.usuarios.signals