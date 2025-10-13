# datumagro/apps/inteligencia/tasks.py

from celery import shared_task
from .services import analisar_desempenho_gmd, gerar_alerta_vacina_bezerro
from datumagro.apps.cadastros.models import Animal, Cliente

@shared_task
def analisar_desempenho_task(animal_id: int):
    """
    Tarefa Celery para ser chamada após uma nova pesagem ser registrada.
    """
    try:
        animal = Animal.objects.get(id=animal_id)
        analisar_desempenho_gmd(animal)
        return f"Análise de desempenho para o animal {animal_id} concluída."
    except Animal.DoesNotExist:
        return f"Erro: Animal com ID {animal_id} não encontrado."

@shared_task
def rodar_analise_sanitaria_cliente_task(cliente_id: int):
    """
    Tarefa Celery para rodar a análise de sanidade para um cliente específico.
    """
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        num_alertas = gerar_alerta_vacina_bezerro(cliente)
        return f"{num_alertas} alertas sanitários criados para o cliente {cliente_id}."
    except Cliente.DoesNotExist:
        return f"Erro: Cliente com ID {cliente_id} não encontrado."

@shared_task
def rodar_analises_diarias_globais():
    """
    Tarefa "mestra" para ser agendada para rodar toda noite.
    Ela busca todos os clientes ativos e dispara as tarefas de análise para cada um.
    """
    clientes_ativos = Cliente.objects.filter(assinatura__status='ATIVA')
    for cliente in clientes_ativos:
        rodar_analise_sanitaria_cliente_task.delay(cliente.id)
    return f"Análises diárias disparadas para {clientes_ativos.count()} clientes ativos."