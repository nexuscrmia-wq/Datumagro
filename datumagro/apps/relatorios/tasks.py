from celery import shared_task


@shared_task
def gerar_relatorio_task(relatorio_id: int):
    """Task genérica que processa um Relatorio pelo ID."""
    from .models import Relatorio
    try:
        relatorio = Relatorio.objects.get(id=relatorio_id)
        relatorio.status = 'CONCLUIDO'
        relatorio.save(update_fields=['status'])
        return f"Relatorio {relatorio_id} concluido."
    except Relatorio.DoesNotExist:
        return f"Relatorio {relatorio_id} nao encontrado."


@shared_task
def gerar_pdf_lote_task(lote_id: int):
    from .services import gerar_relatorio_desempenho_lote_pdf
    from datumagro.apps.operacional.models import Lote
    try:
        lote = Lote.objects.get(id=lote_id)
        gerar_relatorio_desempenho_lote_pdf(lote)
        return f"Relatorio PDF para o lote {lote_id} gerado com sucesso."
    except Lote.DoesNotExist:
        return f"Erro: Lote com ID {lote_id} nao encontrado."


@shared_task
def gerar_excel_animais_task(propriedade_id: int):
    from .services import gerar_relatorio_animais_excel
    from datumagro.apps.cadastros.models import Propriedade
    try:
        propriedade = Propriedade.objects.get(id=propriedade_id)
        gerar_relatorio_animais_excel(propriedade)
        return f"Relatorio Excel para a propriedade {propriedade_id} gerado com sucesso."
    except Propriedade.DoesNotExist:
        return f"Erro: Propriedade com ID {propriedade_id} nao encontrada."
