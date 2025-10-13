# datumagro/apps/notificacoes/models.py

from django.db import models

class LogNotificacao(models.Model):
    """
    Registra cada tentativa de envio de notificação (Email, WhatsApp, Push)
    para um cliente, guardando o sucesso ou a falha da operação.
    """
    CANAL_CHOICES = [
        ('EMAIL', 'E-mail'),
        ('WHATSAPP', 'WhatsApp'),
        ('PUSH', 'Push Notification'),
    ]
    STATUS_CHOICES = [
        ('ENVIADO', 'Enviado com Sucesso'),
        ('FALHA', 'Falha no Envio'),
    ]

    alerta_origem = models.ForeignKey(
        'inteligencia.Alerta',
        on_delete=models.CASCADE,
        related_name='notificacoes_enviadas'
    )
    cliente = models.ForeignKey('cadastros.Cliente', on_delete=models.CASCADE)
    canal = models.CharField(max_length=10, choices=CANAL_CHOICES)
    destinatario = models.CharField(max_length=255, help_text="E-mail ou número de telefone para o qual a notificação foi enviada.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    detalhes_retorno = models.TextField(blank=True, help_text="Resposta da API externa (ex: Twilio SID ou erro SMTP).")

    class Meta:
        verbose_name = "Log de Notificação"
        verbose_name_plural = "Logs de Notificações"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Notificação via {self.canal} para {self.cliente} - {self.status}"