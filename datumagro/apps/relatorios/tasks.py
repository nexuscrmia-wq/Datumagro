# datumagro/apps/relatorios/tasks.py

from celery import shared_task
from .services import gerar_relatorio_desempenho_lote_pdf, gerar_relatorio_animais_excel
# CORREÇÃO: Importando Lote de 'operacional'
from datumagro.apps.operacional.models import Lote
from datumagro.apps.cadastros.models import Propriedade

@shared_task
def gerar_pdf_lote_task(lote_id: int):
    try:
        lote = Lote.objects.get(id=lote_id)
        gerar_relatorio_desempenho_lote_pdf(lote)
        return f"Relatório PDF para o lote {lote_id} gerado com sucesso."
    except Lote.DoesNotExist:
        return f"Erro: Lote com ID {lote_id} não encontrado."

@shared_task
def gerar_excel_animais_task(propriedade_id: int):
    # (Esta função não usa Lote, então continua igual)
    try:
        propriedade = Propriedade.objects.get(id=propriedade_id)
        gerar_relatorio_animais_excel(propriedade)
        return f"Relatório Excel para a propriedade {propriedade_id} gerado com sucesso."
    except Propriedade.DoesNotExist:
        return f"Erro: Propriedade com ID {propriedade_id} não encontrada."