# datumagro/apps/relatorios/models.py

from django.db import models

class Relatorio(models.Model):
    """
    Armazena um registro de cada relatório gerado pelo sistema,
    criando um histórico para o cliente.
    """
    TIPO_CHOICES = [
        ('PDF_DESEMPENHO_LOTE', 'PDF - Desempenho de Lote'),
        ('EXCEL_LISTA_ANIMAIS', 'Excel - Lista de Animais'),
    ]
    STATUS_CHOICES = [
        ('GERANDO', 'Gerando'),
        ('CONCLUIDO', 'Concluído'),
        ('ERRO', 'Erro na Geração'),
    ]

    cliente = models.ForeignKey('cadastros.Cliente', on_delete=models.CASCADE, related_name='relatorios')
    tipo_relatorio = models.CharField(max_length=50, choices=TIPO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='GERANDO')
    data_geracao = models.DateTimeField(auto_now_add=True)
    arquivo = models.FileField(upload_to='relatorios/%Y/%m/%d/', blank=True, null=True)
    parametros = models.JSONField(help_text="Parâmetros usados na geração (ex: ID do Lote)", blank=True, null=True)

    class Meta:
        verbose_name = "Relatório Gerado"
        verbose_name_plural = "Histórico de Relatórios"
        ordering = ['-data_geracao']

    def __str__(self):
        return f"{self.get_tipo_relatorio_display()} para {self.cliente} em {self.data_geracao.strftime('%d/%m/%Y')}"