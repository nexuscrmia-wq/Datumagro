# datumagro/apps/financeiro/models.py

from django.db import models
from django.conf import settings


class Categoria(models.Model):
    """
    Categorias para organizar as transações financeiras.
    Ex: 'Nutrição', 'Sanidade', 'Venda de Animais', 'Manutenção'.
    """
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('CUSTO', 'Custo'),
    ]

    cliente = models.ForeignKey(
        'cadastros.Cliente',
        on_delete=models.CASCADE,
        related_name='categorias_financeiras'
    )
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)

    class Meta:
        verbose_name = "Categoria Financeira"
        verbose_name_plural = "Categorias Financeiras"
        unique_together = ('cliente', 'nome')

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class Transacao(models.Model):
    """
    Representa uma transação financeira individual, seja um custo ou uma receita.
    """
    cliente = models.ForeignKey(
        'cadastros.Cliente',
        on_delete=models.CASCADE,
        related_name='transacoes'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,  # Impede a exclusão de categoria com transações
        related_name='transacoes'
    )
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField()
    observacao = models.TextField(blank=True)

    # Vincula a transação a um animal específico, se aplicável
    animal = models.ForeignKey(
        'cadastros.Animal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacoes_financeiras'
    )

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ['-data']

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"