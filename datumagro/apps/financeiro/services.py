# datumagro/apps/financeiro/services.py

from django.db.models import Sum, Q
from decimal import Decimal
from datetime import date
from .models import Transacao
from datumagro.apps.cadastros.models import Cliente


def get_fluxo_caixa(cliente: Cliente, data_inicio: date, data_fim: date) -> dict:
    """
    Calcula o fluxo de caixa (receitas, custos e saldo) para um cliente
    dentro de um período de datas específico.
    """

    transacoes = Transacao.objects.filter(
        cliente=cliente,
        data__range=(data_inicio, data_fim)
    )

    total_receitas = transacoes.filter(
        categoria__tipo='RECEITA'
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0.0')

    total_custos = transacoes.filter(
        categoria__tipo='CUSTO'
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0.0')

    saldo_periodo = total_receitas - total_custos

    return {
        'data_inicio': data_inicio.isoformat(),
        'data_fim': data_fim.isoformat(),
        'total_receitas': total_receitas,
        'total_custos': total_custos,
        'saldo_periodo': saldo_periodo,
        'transacoes': list(transacoes.values('id', 'descricao', 'valor', 'data', 'categoria__nome', 'categoria__tipo'))
    }