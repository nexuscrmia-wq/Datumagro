# datumagro/apps/notificacoes/services.py

from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client as TwilioClient
from .models import LogNotificacao
from datumagro.apps.inteligencia.models import Alerta


def enviar_notificacao_por_email(alerta: Alerta):
    """ Tenta enviar um alerta por e-mail e registra o log. """
    destinatario = alerta.cliente.email_contato
    try:
        send_mail(
            subject=f"[DatumAgro] Novo Alerta: {alerta.get_tipo_alerta_display()}",
            message=alerta.mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False,
        )
        LogNotificacao.objects.create(
            alerta_origem=alerta, cliente=alerta.cliente, canal='EMAIL',
            destinatario=destinatario, status='ENVIADO', detalhes_retorno='E-mail enviado via SMTP.'
        )
    except Exception as e:
        LogNotificacao.objects.create(
            alerta_origem=alerta, cliente=alerta.cliente, canal='EMAIL',
            destinatario=destinatario, status='FALHA', detalhes_retorno=str(e)
        )


def enviar_notificacao_por_whatsapp(alerta: Alerta):
    """ Tenta enviar um alerta por WhatsApp usando Twilio e registra o log. """
    destinatario = f"whatsapp:{alerta.cliente.telefone}"  # Formato exigido pela Twilio
    try:
        # Verifica se as credenciais do Twilio estão configuradas
        if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_WHATSAPP_NUMBER]):
            raise ValueError("Credenciais do Twilio não configuradas no ambiente.")

        client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        mensagem_formatada = f"*[DatumAgro]*\n\n*Novo Alerta: {alerta.get_tipo_alerta_display()}*\n\n{alerta.mensagem}"

        message = client.messages.create(
            body=mensagem_formatada,
            from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
            to=destinatario
        )
        LogNotificacao.objects.create(
            alerta_origem=alerta, cliente=alerta.cliente, canal='WHATSAPP',
            destinatario=destinatario, status='ENVIADO', detalhes_retorno=f"Twilio SID: {message.sid}"
        )
    except Exception as e:
        LogNotificacao.objects.create(
            alerta_origem=alerta, cliente=alerta.cliente, canal='WHATSAPP',
            destinatario=destinatario, status='FALHA', detalhes_retorno=str(e)
        )


def disparar_notificacoes_para_alerta(alerta: Alerta):
    """
    Orquestrador: Decide para quais canais o alerta deve ser enviado.
    No futuro, isso pode ser baseado nas preferências do cliente.
    """
    # Por padrão, vamos tentar enviar para ambos
    enviar_notificacao_por_email(alerta)
    enviar_notificacao_por_whatsapp(alerta)