# datumagro/apps/assinaturas/services.py

from django.utils import timezone
from datetime import timedelta
from .models import Assinatura, Plano
from datumagro.apps.cadastros.models import Cliente


def criar_ou_atualizar_assinatura(cliente: Cliente, plano: Plano) -> Assinatura:
    """
    Serviço central para gerenciar o ciclo de vida da assinatura.
    Responsável por iniciar a jornada do cliente em um de nossos planos
    inovadores, materializando a venda.
    """
    agora = timezone.now()
    proximo_vencimento = agora + timedelta(days=30)

    assinatura, criada = Assinatura.objects.update_or_create(
        cliente=cliente,
        defaults={
            'plano': plano,
            'status': 'ATIVA',
            'data_inicio': agora,
            'data_vencimento': proximo_vencimento,
            'data_cancelamento': None
        }
    )
    return assinatura


def cancelar_assinatura(cliente: Cliente) -> Assinatura:
    """
    Serviço para formalizar o encerramento da relação com o cliente,
    marcando sua assinatura como cancelada.
    """
    try:
        assinatura = cliente.assinatura
        assinatura.status = 'CANCELADA'
        assinatura.data_cancelamento = timezone.now()
        assinatura.save()
        return assinatura
    except Assinatura.DoesNotExist:
        return None


def verificar_e_atualizar_status_assinaturas():
    """
    Rotina de sistema para garantir a saúde financeira da plataforma,
    identificando e marcando assinaturas vencidas como inadimplentes.
    Essencial para a automação da gestão de pagamentos.
    """
    hoje = timezone.now()
    assinaturas_vencidas = Assinatura.objects.filter(
        status='ATIVA',
        data_vencimento__lt=hoje
    )

    return assinaturas_vencidas.update(status='INADIMPLENTE')