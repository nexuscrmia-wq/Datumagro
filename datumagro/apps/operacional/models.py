# datumagro/apps/operacional/models.py

from django.db import models

class ProdutoSanitario(models.Model):
    TIPO_CHOICES = [('VACINA', 'Vacina'), ('VERMIFUGO', 'Vermífugo'), ('ANTIBIOTICO', 'Antibiótico'), ('OUTRO', 'Outro')]
    cliente = models.ForeignKey('cadastros.Cliente', on_delete=models.CASCADE, related_name='produtos_sanitarios')
    nome = models.CharField(max_length=100)
    fabricante = models.CharField(max_length=100, blank=True)
    tipo_produto = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nome

class ManejoSanitario(models.Model):
    TIPO_CHOICES = [
        ('VACINACAO', 'Vacinação'),
        ('VERMIFUGACAO', 'Vermifugação'),
        ('CARRAPATICIDA', 'Carrapaticida'),
        ('SUPLEMENTACAO', 'Suplementação'),
        ('OUTRO', 'Outro'),
    ]
    animal = models.ForeignKey('cadastros.Animal', on_delete=models.CASCADE, related_name='manejos_sanitarios')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='VACINACAO')
    data = models.DateField()
    descricao = models.CharField(max_length=200, blank=True)
    produto = models.CharField(max_length=100, blank=True)
    dosagem = models.CharField(max_length=50, blank=True)
    via_aplicacao = models.CharField(max_length=50, blank=True)
    profissional = models.CharField(max_length=100, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.get_tipo_display()} em {self.animal.brinco} ({self.data})"

class RegistroReprodutivo(models.Model):
    TIPO_EVENTO = [('COBERTURA', 'Cobertura Natural'), ('INSEMINACAO', 'Inseminação Artificial'), ('DIAGNOSTICO', 'Diagnóstico de Gestação'), ('PARTO', 'Parto')]
    RESULTADO_DG = [('PRENHA', 'Prenha'), ('VAZIA', 'Vazia')]
    matriz = models.ForeignKey('cadastros.Animal', on_delete=models.CASCADE, related_name='registros_reprodutivos', limit_choices_to={'sexo': 'F'})
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO)
    data_evento = models.DateField()
    touro = models.ForeignKey('cadastros.Animal', on_delete=models.SET_NULL, null=True, blank=True, related_name='coberturas', limit_choices_to={'sexo': 'M'})
    resultado_dg = models.CharField(max_length=10, choices=RESULTADO_DG, null=True, blank=True)
    ordem_parto = models.PositiveIntegerField(null=True, blank=True, editable=False, help_text="Calculado automaticamente. Ex: 1 para a primeira cria.")
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ['-data_evento']

    def __str__(self):
        return f"{self.get_tipo_evento_display()} de {self.matriz.brinco} em {self.data_evento}"

    def save(self, *args, **kwargs):
        if self.tipo_evento == 'PARTO' and not self.pk:
            partos_anteriores = RegistroReprodutivo.objects.filter(matriz=self.matriz, tipo_evento='PARTO').count()
            self.ordem_parto = partos_anteriores + 1
        super().save(*args, **kwargs)

class Lote(models.Model):
    nome = models.CharField(max_length=100)
    propriedade = models.ForeignKey('cadastros.Propriedade', on_delete=models.CASCADE, related_name='lotes')
    animais = models.ManyToManyField('cadastros.Animal', related_name='lotes', blank=True)

    def __str__(self):
        return self.nome

class Piquete(models.Model):
    STATUS_CHOICES = [('DESCANSANDO', 'Descansando'), ('EM_USO', 'Em Uso'), ('PRONTO', 'Pronto para Uso')]
    CAPIM_CHOICES = [('MOMBASSA', 'Mombaça'), ('PIATA', 'BRS Piatã'), ('ZURI', 'BRS Zuri'), ('MARANDU', 'Marandu')]
    propriedade = models.ForeignKey('cadastros.Propriedade', on_delete=models.CASCADE, related_name='piquetes')
    nome = models.CharField(max_length=100)
    tamanho_hectares = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo_capim = models.CharField(max_length=20, choices=CAPIM_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DESCANSANDO')
    lote_atual = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True, related_name='piquete_atual')
    data_entrada_lote = models.DateField(null=True, blank=True)
    data_saida_prevista = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nome} ({self.propriedade.nome_propriedade})"