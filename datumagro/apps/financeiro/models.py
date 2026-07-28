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
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    ]
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey(
        'cadastros.Cliente',
        on_delete=models.CASCADE,
        related_name='transacoes'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='DESPESA')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacoes'
    )
    categoria_nome = models.CharField(max_length=100, blank=True, default='')
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


class FormaPagamento(models.Model):
    class TipoCartao(models.TextChoices):
        CREDITO = 'CC', 'Cartão de Crédito'
        DEBITO = 'CD', 'Cartão de Débito'
        BOLETO = 'BL', 'Boleto'
        PIX = 'PX', 'PIX'

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='formas_pagamento')
    tipo = models.CharField(max_length=2, choices=TipoCartao.choices)
    titular = models.CharField(max_length=255)
    numero_cartao = models.CharField(max_length=20, blank=True, null=True)
    validade = models.CharField(max_length=7, blank=True, null=True)  # MM/YYYY
    bandeira = models.CharField(max_length=50, blank=True, null=True)
    chave_pix = models.CharField(max_length=255, blank=True, null=True)
    principal = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Forma de Pagamento'
        verbose_name_plural = 'Formas de Pagamento'
        ordering = ['-principal', '-data_cadastro']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titular}"

    def save(self, *args, **kwargs):
        # Se marcar como principal, desmarca as demais do usuário
        if self.principal:
            FormaPagamento.objects.filter(usuario=self.usuario, principal=True).exclude(id=self.id).update(principal=False)

        # Limpeza de campos conforme tipo
        if self.tipo == self.TipoCartao.PIX:
            self.numero_cartao = None
            self.validade = None
            self.bandeira = None
        elif self.tipo in (self.TipoCartao.CREDITO, self.TipoCartao.DEBITO):
            self.chave_pix = None
        elif self.tipo == self.TipoCartao.BOLETO:
            self.numero_cartao = None
            self.validade = None
            self.bandeira = None
            self.chave_pix = None

        super().save(*args, **kwargs)