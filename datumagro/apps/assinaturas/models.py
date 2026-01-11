# datumagro/apps/assinaturas/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Plano(models.Model):
    """
    Representa os planos de assinatura do DatumAgro.
    Estes planos são a base do nosso modelo de negócio, projetados para
    serem mais completos e inovadores que os concorrentes.
    """
    PLANO_CHOICES = [
        ('Digital', 'Digital'),
        ('Conectado', 'Conectado'),
        ('Elite', 'Elite'),
    ]

    nome = models.CharField(max_length=100, unique=True, choices=PLANO_CHOICES)
    descricao = models.TextField(help_text="Descrição comercial do plano para o site.")
    valor_base_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    limite_animais = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Limite de animais monitorados neste plano. Null significa sem limite (ilimitado)."
    )

    # Diferencial de Negócio: HaaS (Hardware as a Service)
    hardware_incluso = models.BooleanField(
        default=False,
        help_text="Nosso modelo inovador HaaS: Vexus fornece os brincos, eliminando a barreira de entrada."
    )

    # Diferencial de Negócio: Gestão Assistida
    suporte_especialista = models.BooleanField(
        default=False,
        help_text="Diferencial do Plano Elite: Acesso a veterinários e zootecnistas parceiros."
    )

    # Controle de usuários por assinatura
    max_funcionarios = models.PositiveIntegerField(
        default=0,
        help_text="Número máximo de usuários do tipo 'funcionário' permitidos além do usuário master. 0 significa nenhum funcionário permitido."
    )

    # Acesso a módulo especial de importação internacional (disponível apenas no plano superior)
    acesso_importacao_internacional = models.BooleanField(
        default=False,
        help_text="Habilita o módulo de importação internacional para o cliente (ex.: Planos Enterprise/Elite)."
    )

    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Plano"
        verbose_name_plural = "Planos"
        ordering = ['valor_base_mensal']

    def __str__(self):
        return self.nome


class Assinatura(models.Model):
    """
    Vincula um Cliente a um Plano, representando a relação comercial ativa.
    É a materialização da estratégia de monetização do DatumAgro.
    """
    STATUS_CHOICES = [
        ('ATIVA', 'Ativa'),
        ('INADIMPLENTE', 'Inadimplente'),
        ('CANCELADA', 'Cancelada'),
    ]

    cliente = models.OneToOneField(
        'cadastros.Cliente',
        on_delete=models.CASCADE,
        related_name='assinatura'
    )
    plano = models.ForeignKey(Plano, on_delete=models.PROTECT, related_name='assinaturas')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVA')
    data_inicio = models.DateTimeField(default=timezone.now)
    data_vencimento = models.DateTimeField()
    data_cancelamento = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"

    def __str__(self):
        return f"Assinatura de {self.cliente.nome_empresa} - Plano {self.plano.nome}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.data_vencimento = self.data_inicio + timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def is_ativa(self):
        return self.status == 'ATIVA' and self.data_vencimento >= timezone.now()