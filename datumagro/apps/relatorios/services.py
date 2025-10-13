# datumagro/apps/relatorios/services.py

from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from weasyprint import HTML
import pandas as pd
from io import BytesIO
from .models import Relatorio
# CORREÇÃO: Importando Lote de 'operacional'
from datumagro.apps.operacional.models import Lote
from datumagro.apps.cadastros.models import Propriedade, Animal


def gerar_relatorio_desempenho_lote_pdf(lote: Lote) -> Relatorio:
    """
    Gera um relatório em PDF, salva no modelo Relatorio e retorna a instância.
    """
    relatorio = Relatorio.objects.create(
        cliente=lote.propriedade.cliente,
        tipo_relatorio='PDF_DESEMPENHO_LOTE',
        parametros={'lote_id': lote.id}
    )

    try:
        animais = lote.animais.all().prefetch_related('pesagens')
        contexto = {'lote': lote, 'animais': animais, 'propriedade': lote.propriedade}
        html_string = render_to_string('relatorios/desempenho_lote.html', contexto)
        pdf_bytes = HTML(string=html_string).write_pdf()

        nome_arquivo = f"rel_lote_{lote.nome}_{relatorio.id}.pdf"
        relatorio.arquivo.save(nome_arquivo, ContentFile(pdf_bytes))

        relatorio.status = 'CONCLUIDO'
        relatorio.save()
    except Exception as e:
        relatorio.status = 'ERRO'
        relatorio.save()

    return relatorio


def gerar_relatorio_animais_excel(propriedade: Propriedade) -> Relatorio:
    # (Esta função não usa Lote, então continua igual)
    # ... código continua o mesmo ...
    relatorio = Relatorio.objects.create(
        cliente=propriedade.cliente,
        tipo_relatorio='EXCEL_LISTA_ANIMAIS',
        parametros={'propriedade_id': propriedade.id}
    )

    try:
        animais = Animal.objects.filter(propriedade=propriedade, ativo=True)
        dados = {"Brinco": [a.brinco for a in animais], "Raça": [a.raca for a in animais],
                 "Sexo": [a.get_sexo_display() for a in animais]}
        df = pd.DataFrame(dados)

        buffer = BytesIO()
        df.to_excel(buffer, index=False, sheet_name='Animais')
        buffer.seek(0)

        nome_arquivo = f"rel_animais_{propriedade.nome_propriedade}_{relatorio.id}.xlsx"
        relatorio.arquivo.save(nome_arquivo, ContentFile(buffer.getvalue()))

        relatorio.status = 'CONCLUIDO'
        relatorio.save()
    except Exception as e:
        relatorio.status = 'ERRO'
        relatorio.save()

    return relatorio