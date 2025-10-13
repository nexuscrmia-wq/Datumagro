# datumagro/apps/integracoes/models.py

from django.db import models


class LogIntegracao(models.Model):
    """
    Registra cada requisição recebida de hardware externo (leitores RFID, balanças, etc.).
    Funciona como uma "caixa-preta" para auditoria e depuração.
    """
    STATUS_CHOICES = [
        ('PROCESSADO', 'Processado com Sucesso'),
        ('ERRO', 'Erro no Processamento'),
        ('PENDENTE', 'Pendente de Processamento'),
    ]
    TIPO_CHOICES = [
        ('RFID_PESAGEM', 'RFID + Pesagem em Balança'),
        ('RFID_MANEJO', 'RFID em Tronco de Manejo'),
        ('CAMERA_PESAGEM', 'Câmera de Pesagem (Futuro)'),
    ]

    cliente = models.ForeignKey('cadastros.Cliente', on_delete=models.CASCADE, related_name='logs_integracao')
    tipo_integracao = models.CharField(max_length=20, choices=TIPO_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    dados_recebidos = models.JSONField(help_text="O JSON bruto recebido do hardware.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    mensagem_retorno = models.TextField(blank=True, help_text="Mensagem de sucesso ou erro retornada.")

    class Meta:
        verbose_name = "Log de Integração"
        verbose_name_plural = "Logs de Integração"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Log de {self.cliente} em {self.timestamp} - {self.status}"