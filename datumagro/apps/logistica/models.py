from django.db import models
from django.core.exceptions import ValidationError
from datumagro.apps.cadastros.models import Animal, Cliente


class Embarque(models.Model):
    """Modelo único e consolidado de embarque de logística"""
    TIPO_CHOICES = [
        ('EXP', 'Exportação (Saída)'),
        ('IMP', 'Importação (Entrada)'),
    ]
    STATUS_CHOICES = [
        ('PLA', 'Planejado'),
        ('PRE', 'Pré-Embarque / Quarentena'),
        ('NAV', 'Em Trânsito Marítimo'),
        ('POR', 'Chegada no Porto'),
        ('FIN', 'Finalizado / Desembaraçado'),
        ('CAN', 'Cancelado'),
    ]
    
    # Identificação
    numero_embarque = models.CharField(max_length=20, unique=True, verbose_name="Número do Embarque")
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='PLA')
    
    # Dados da Rota
    porto_origem = models.CharField(max_length=100, default="Porto do Açu")
    porto_destino = models.CharField(max_length=100)
    pais_parceiro = models.CharField(max_length=100, verbose_name="País Origem/Destino")
    navio = models.CharField(max_length=100, blank=True, null=True)
    viagem = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número da Viagem")
    
    # Datas importantes
    data_prevista_embarque = models.DateField(verbose_name="Data Prevista de Embarque")
    data_prevista_chegada = models.DateField(verbose_name="Data Prevista de Chegada")
    data_real_embarque = models.DateField(null=True, blank=True, verbose_name="Data Real de Embarque")
    data_real_chegada = models.DateField(null=True, blank=True, verbose_name="Data Real de Chegada")
    
    # Responsáveis
    responsavel = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='embarques')
    agente_carga = models.CharField(max_length=200, blank=True, verbose_name="Agente de Carga")
    
    # Documentação
    bl_numero = models.CharField(max_length=50, blank=True, verbose_name="Bill of Lading")
    conhecimento_carga = models.CharField(max_length=50, blank=True, verbose_name="Conhecimento de Carga")
    
    # Financeiro
    valor_frete = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Valor do Frete (USD)")
    valor_seguro = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Valor do Seguro (USD)")
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Valor Total (USD)")
    
    observacoes = models.TextField(blank=True)
    
    # Controle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Embarque"
        verbose_name_plural = "Embarques"
        ordering = ['-data_prevista_embarque']
        indexes = [
            models.Index(fields=['numero_embarque']),
            models.Index(fields=['tipo', 'status']),
            models.Index(fields=['data_prevista_embarque']),
            models.Index(fields=['responsavel']),
        ]

    def __str__(self):
        return f"{self.numero_embarque} - {self.get_tipo_display()} - {self.navio}"

    def clean(self):
        errors = {}
        
        # Validar datas
        if self.data_prevista_chegada and self.data_prevista_embarque:
            if self.data_prevista_chegada < self.data_prevista_embarque:
                errors['data_prevista_chegada'] = "Data de chegada não pode ser anterior ao embarque"
        
        if self.data_real_chegada and self.data_real_embarque:
            if self.data_real_chegada < self.data_real_embarque:
                errors['data_real_chegada'] = "Data real de chegada não pode ser anterior ao embarque real"
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        # Gerar número do embarque automaticamente se não existir
        if not self.numero_embarque:
            from django.utils import timezone
            year = timezone.now().year
            last_embarque = Embarque.objects.filter(
                created_at__year=year
            ).order_by('-id').first()
            
            if last_embarque and last_embarque.numero_embarque:
                last_number = int(last_embarque.numero_embarque.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
                
            self.numero_embarque = f"EMP-{year}-{new_number:04d}"
        
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def total_peso_kg(self):
        return sum(item.peso_total_kg for item in self.itens.all()) or 0
    
    @property
    def total_animais_vivos(self):
        return self.itens.filter(animal__isnull=False).count()


class ItemEmbarque(models.Model):
    """
    Representa o que está sendo transportado.
    Pode ser um Animal específico (Vivo) ou uma carga de carne (Morto).
    """
    TIPO_PRODUTO_CHOICES = [
        ('VIVO', 'Gado Vivo'),
        ('CARNE', 'Carne/Carcaça'),
        ('CORTES', 'Cortes Específicos'),
        ('SUB', 'Subprodutos'),
    ]
    
    embarque = models.ForeignKey(Embarque, on_delete=models.CASCADE, related_name='itens')
    tipo_produto = models.CharField(max_length=10, choices=TIPO_PRODUTO_CHOICES, default='VIVO')
    
    # Se for gado vivo (Exportação do seu rebanho)
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='historico_logistica')
    
    # Se for importação ou animal abatido (sem ID de brinco ativo no sistema)
    descricao_produto = models.CharField(max_length=200, blank=True, 
                                        help_text="Ex: Carcaça Nelore, Cortes Traseiros, Couro")
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=1, 
                                    help_text="Quantidade de unidades ou toneladas")
    peso_total_kg = models.DecimalField(max_digits=10, decimal_places=2, 
                                       verbose_name="Peso Total (kg)")
    
    # Especificações do produto
    categoria_carne = models.CharField(max_length=50, blank=True, 
                                      help_text="Ex: Prime Cut, Choice, Select")
    certificacao = models.CharField(max_length=100, blank=True, 
                                  help_text="Ex: Halal, Kosher, Organic")
    
    # Documentação Sanitária
    gta = models.CharField(max_length=50, blank=True, verbose_name="Número GTA")
    sif = models.CharField(max_length=50, blank=True, verbose_name="Número SIF")
    certificado_sanitario = models.FileField(upload_to='docs_logistica/certificados/', 
                                           null=True, blank=True)
    certificado_origem = models.FileField(upload_to='docs_logistica/origem/', 
                                        null=True, blank=True)
    
    # Financeiro
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                       verbose_name="Valor Unitário (USD)")
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                    verbose_name="Valor Total (USD)")
    
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Item de Embarque"
        verbose_name_plural = "Itens de Embarque"
        indexes = [
            models.Index(fields=['embarque', 'tipo_produto']),
            models.Index(fields=['animal']),
        ]

    def __str__(self):
        if self.animal:
            return f"Animal {self.animal.brinco} - {self.peso_total_kg}kg"
        return f"{self.descricao_produto} - {self.quantidade} un - {self.peso_total_kg}kg"

    def clean(self):
        errors = {}
        
        # Validar que tem animal OU descrição do produto
        if not self.animal and not self.descricao_produto:
            errors['animal'] = "Informe um animal ou a descrição do produto"
            errors['descricao_produto'] = "Informe um animal ou a descrição do produto"
        
        # Validar pesos
        if self.peso_total_kg <= 0:
            errors['peso_total_kg'] = "Peso deve ser maior que zero"
        
        if self.valor_unitario < 0:
            errors['valor_unitario'] = "Valor unitário não pode ser negativo"
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        # Calcular valor total
        if self.valor_unitario and self.quantidade:
            self.valor_total = self.valor_unitario * self.quantidade
        
        self.clean()
        super().save(*args, **kwargs)


class RastreamentoEmbarque(models.Model):
    """
    Histórico de atualizações do embarque
    """
    embarque = models.ForeignKey(Embarque, on_delete=models.CASCADE, related_name='rastreamento')
    status_anterior = models.CharField(max_length=3, choices=Embarque.STATUS_CHOICES)
    status_novo = models.CharField(max_length=3, choices=Embarque.STATUS_CHOICES)
    descricao = models.TextField()
    localizacao = models.CharField(max_length=100, blank=True, help_text="Localização atual")
    data_evento = models.DateTimeField(auto_now_add=True)
    
    # Arquivos anexos (fotos, documentos)
    arquivo = models.FileField(upload_to='docs_logistica/rastreamento/', null=True, blank=True)
    
    class Meta:
        verbose_name = "Rastreamento de Embarque"
        verbose_name_plural = "Rastreamento de Embarques"
        ordering = ['-data_evento']

    def __str__(self):
        return f"{self.embarque.numero_embarque} - {self.get_status_novo_display()}"
