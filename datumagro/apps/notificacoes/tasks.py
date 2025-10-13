# datumagro/apps/notificacoes/tasks.py

from celery import shared_task
from .services import disparar_notificacoes_para_alerta
from datumagro.apps.inteligencia.models import Alerta

@shared_task
def notificar_cliente_task(alerta_id: int):
    """
    Tarefa Celery que busca um alerta e dispara as notificações.
    Esta tarefa será acionada por um "sinal" do Django sempre que um novo
    alerta for salvo no banco de dados.
    """
    try:
        alerta = Alerta.objects.get(id=alerta_id)
        disparar_notificacoes_para_alerta(alerta)
        return f"Notificações para o alerta {alerta_id} foram processadas."
    except Alerta.DoesNotExist:
        return f"Erro: Alerta com ID {alerta_id} não foi encontrado para notificar."