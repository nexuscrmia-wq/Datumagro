# datumagro/apps/operacional/services.py

from datetime import date, timedelta
from .models import Lote, Piquete


def mover_lote_para_piquete(lote: Lote, novo_piquete: Piquete, dias_ocupacao: int = 7) -> Piquete:
    """
    Serviço para automatizar a movimentação de um lote entre piquetes.
    """
    hoje = date.today()

    # 1. Libera o piquete antigo, se houver
    if lote.piquete_atual:
        piquete_antigo = lote.piquete_atual
        piquete_antigo.status = 'DESCANSANDO'
        piquete_antigo.lote_atual = None
        piquete_antigo.save()

    # 2. Ocupa o novo piquete
    novo_piquete.status = 'EM_USO'
    novo_piquete.lote_atual = lote
    novo_piquete.data_entrada_lote = hoje
    novo_piquete.data_saida_prevista = hoje + timedelta(days=dias_ocupacao)
    novo_piquete.save()

    return novo_piquete


def recomendar_proximo_piquete(propriedade) -> Piquete | None:
    """
    IA Regra 3 (Manejo de Pasto): Encontra o melhor piquete 'Pronto' para
    receber o próximo lote. Por enquanto, a regra é simples: o que está
    'Pronto' há mais tempo.
    """
    piquetes_prontos = Piquete.objects.filter(
        propriedade=propriedade,
        status='PRONTO'
    ).order_by('data_saida_prevista')  # Ordena pelo que está pronto há mais tempo

    return piquetes_prontos.first()