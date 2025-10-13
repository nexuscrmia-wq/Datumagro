# datumagro/apps/inteligencia/models.py

from django.db import models


class Alerta(models.Model):
    """
    Representa um alerta ou recomendação gerado pela IA para um cliente.
    """
    TIPO_ALERTA_CHOICES = [
        ('SANITARIO', 'Alerta Sanitário (Ex: Vacina Atrasada)'),
        ('REPRODUTIVO', 'Alerta Reprodutivo (Ex: Sugestão de Cobertura)'),
        ('DESEMPENHO', 'Alerta de Desempenho (Ex: Baixo GMD)'),
        ('MANEJO', 'Recomendação de Manejo (Ex: Troca de Piquete)'),
        ('GENETICO', 'Recomendação Genética (Ex: Sugestão de Acasalamento)'),
    ]
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('VISUALIZADO', 'Visualizado'),
        ('RESOLVIDO', 'Resolvido'),
    ]

    cliente = models.ForeignKey('cadastros.Cliente', on_delete=models.CASCADE, related_name='alertas')
    animal = models.ForeignKey('cadastros.Animal', on_delete=models.CASCADE, related_name='alertas', null=True,
                               blank=True)
    tipo_alerta = models.CharField(max_length=20, choices=TIPO_ALERTA_CHOICES)
    mensagem = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas da IA"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Alerta {self.tipo_alerta} para {self.cliente.nome_empresa}"