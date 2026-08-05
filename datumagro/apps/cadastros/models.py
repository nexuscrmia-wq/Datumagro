from django.db import models
from django.core.exceptions import ValidationError


class Cliente(models.Model):
    """
    Representa o cliente pagante do sistema, a "conta" principal.
    A conexão com o usuário de login é feita a partir do modelo PerfilUsuario.
    """
    FAIXA_REBANHO_CHOICES = [
        ('1-50', '1 a 50'), ('51-200', '51 a 200'), ('201-500', '201 a 500'),
        ('501-1000', '501 a 1000'), ('1000+', 'Acima de 1000'),
    ]

    TIPO_ESPECIE_CHOICES = [
        ('BOVINOS_CORTE', 'Pecuária de Corte (Bovinos)'),
        ('BOVINOS_LEITE', 'Pecuária de Leite (Bovinos)'),
        ('SUINOS', 'Suinocultura (Porcos)'),
        ('EQUINOS', 'Equinocultura (Cavalos)'),
        ('OVINOS_CAPRINOS', 'Ovinos e Caprinos (Ovelhas/Cabras)'),
    ]

    nome_empresa = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=18, unique=True)
    tipo_documento = models.CharField(max_length=4, choices=[('CPF', 'CPF'), ('CNPJ', 'CNPJ')], default='CPF')
    telefone = models.CharField(max_length=20, blank=True)
    email_contato = models.EmailField(unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    emite_nota_fiscal = models.BooleanField(default=False)
    inscricao_estadual = models.CharField(max_length=20, blank=True)
    faixa_rebanho = models.CharField(max_length=20, choices=FAIXA_REBANHO_CHOICES, blank=True)
    num_funcionarios = models.IntegerField(default=0)
    sistema_anterior = models.CharField(max_length=50, blank=True)
    principal_desafio = models.CharField(max_length=50, blank=True)
    onboarding_completo = models.BooleanField(default=False)
    onboarding_etapa = models.IntegerField(default=1)
    tipo_especie = models.CharField(
        max_length=20,
        choices=TIPO_ESPECIE_CHOICES,
        default='BOVINOS_CORTE',
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nome_empresa


class Propriedade(models.Model):
    """
    Representa uma fazenda ou propriedade rural de um Cliente.
    Um cliente pode ter várias propriedades.
    """
    OBJETIVO_CHOICES = [('CRIA', 'Cria'), ('RECRIA', 'Recria'), ('ENGORDA', 'Engorda')]
    TIPO_SOLO_CHOICES = [('ARENOSO', 'Arenoso'), ('ARGILOSO', 'Argiloso'), ('MISTO', 'Misto')]
    TOPOGRAFIA_CHOICES = [('PLANO', 'Plano'), ('ONDULADO', 'Ondulado'), ('MONTANHOSO', 'Montanhoso')]
    TIPO_OPERACAO_CHOICES = [('CORTE', 'Corte'), ('LEITE', 'Leite'), ('MISTO', 'Misto')]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='propriedades')
    nome_propriedade = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255, blank=True)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)  # UF
    cep = models.CharField(max_length=9, blank=True)
    hectares = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo_operacao = models.CharField(max_length=20, choices=TIPO_OPERACAO_CHOICES, default='CORTE')

    objetivo_producao = models.CharField(max_length=10, choices=OBJETIVO_CHOICES, null=True, blank=True)
    tipo_solo = models.CharField(max_length=10, choices=TIPO_SOLO_CHOICES, null=True, blank=True)
    topografia = models.CharField(max_length=15, choices=TOPOGRAFIA_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = "Propriedade"
        verbose_name_plural = "Propriedades"
        unique_together = ('cliente', 'nome_propriedade')
        
        # ✅ ÍNDICES PARA PERFORMANCE
        indexes = [
            models.Index(fields=['cliente'], name='propriedade_cliente_idx'),
            models.Index(fields=['estado', 'cidade'], name='propriedade_estado_cidade_idx'),
            models.Index(fields=['objetivo_producao'], name='propriedade_objetivo_idx'),
        ]

    def __str__(self):
        return self.nome_propriedade


class Animal(models.Model):
    """
    O modelo central do sistema, representando um animal individual com todas as suas características.
    """
    # --- LISTAS DE ESCOLHA PARA OS CAMPOS ---
    SEXO_CHOICES = [('M', 'Macho'), ('F', 'Fêmea')]
    RACA_CHOICES = [('NELORE', 'Nelore'), ('ANGUS', 'Angus'), ('BRAHMAN', 'Brahman'), ('BRANGUS', 'Brangus'),
                    ('SENEPOL', 'Senepol'), ('GUZERA', 'Guzerá'), ('TABAPUA', 'Tabapuã'), ('GIR', 'Gir Leiteiro'),
                    ('GIROLANDO', 'Girolando'), ('HEREFORD', 'Hereford'), ('BRAFORD', 'Braford'), ('CARACU', 'Caracu'),
                    ('OUTRA', 'Outra/Mestiço')]
    TEMPERAMENTO_CHOICES = [('MANSO', 'Manso'), ('NORMAL', 'Normal'), ('BRABO', 'Brabo'), ('AGRESSIVO', 'Agressivo')]
    CATEGORIA_CHOICES = [('BEZERRO', 'Bezerro(a)'), ('NOVILHA', 'Novilha'), ('GARROTE', 'Garrote'), ('TOURO', 'Touro'),
                         ('MATRIZ', 'Matriz (Vaca)'), ('BOI', 'Boi (Engorda)')]
    APTIDAO_CHOICES = [('CORTE', 'Corte'), ('LEITE', 'Leite'), ('DUPLA', 'Dupla Aptidão')]
    STATUS_REPRODUTIVO_CHOICES = [('VAZIA', 'Vazia'), ('PRENHA', 'Prenha'), ('LACTANTE', 'Em Lactação'),
                                  ('SECA', 'Seca')]
    REGISTRO_GENETICO_CHOICES = [
        ('PO', 'Puro de Origem (PO)'),
        ('PC', 'Puro por Cruza (PC)'),
        ('PA', 'Puro por Absorção (PA)'),
        ('COM', 'Comercial (sem registro)'),
    ]

    # --- DEFINIÇÃO DOS CAMPOS ---
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='animais')
    brinco = models.CharField(max_length=50, help_text="Identificação única do animal.")
    raca = models.CharField(max_length=100, choices=RACA_CHOICES)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField(null=True, blank=True)

    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, blank=True)
    temperamento = models.CharField(max_length=20, choices=TEMPERAMENTO_CHOICES, blank=True)
    aptidao = models.CharField(max_length=10, choices=APTIDAO_CHOICES, blank=True)
    status_reprodutivo = models.CharField(max_length=10, choices=STATUS_REPRODUTIVO_CHOICES, blank=True,
                                          help_text="Apenas para fêmeas em idade reprodutiva.")
    is_reprodutor = models.BooleanField(default=False, help_text="Marque se este macho é um reprodutor (touro).")
    registro_genetico = models.CharField(
        max_length=3, choices=REGISTRO_GENETICO_CHOICES, default='COM', blank=True,
        help_text="Classificação genética do animal conforme associação de raça."
    )

    caracteristicas_adicionais = models.TextField(blank=True,
                                                  help_text="Descreva outros comportamentos ou características físicas.")
    foto_perfil = models.ImageField(upload_to='animais_fotos/', null=True, blank=True,
                                    help_text="Foto opcional do animal.")

    pai = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='descendentes_pai',
                            limit_choices_to={'sexo': 'M'})
    mae = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='descendentes_mae',
                            limit_choices_to={'sexo': 'F'})
    ativo = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"
        unique_together = ('propriedade', 'brinco')
        ordering = ['-data_nascimento']
        
        # ✅ ÍNDICES DE PERFORMANCE - Essenciais para 100.000+ registros
        indexes = [
            # Índices para buscas rápidas
            models.Index(fields=['brinco'], name='animal_brinco_idx'),
            models.Index(fields=['propriedade', 'ativo'], name='animal_prop_ativo_idx'),
            models.Index(fields=['raca', 'sexo'], name='animal_raca_sexo_idx'),
            models.Index(fields=['categoria'], name='animal_categoria_idx'),
            models.Index(fields=['status_reprodutivo'], name='animal_status_reprod_idx'),
            models.Index(fields=['data_nascimento'], name='animal_data_nasc_idx'),
            
            # Índices para genealogia
            models.Index(fields=['pai'], name='animal_pai_idx'),
            models.Index(fields=['mae'], name='animal_mae_idx'),
            
            # Índices compostos para consultas complexas
            models.Index(fields=['propriedade', 'raca', 'sexo'], name='animal_prop_raca_sexo_idx'),
            models.Index(fields=['propriedade', 'data_nascimento'], name='animal_prop_data_nasc_idx'),
        ]

    def __str__(self):
        return f"{self.brinco} ({self.get_raca_display()})"

    @property
    def numero_de_crias(self):
        """ Calcula e retorna o número de partos registrados para esta fêmea. """
        if self.sexo == 'F':
            # Usa a relação reversa 'registros_reprodutivos' definida no modelo RegistroReprodutivo
            return self.registros_reprodutivos.filter(tipo_evento='PARTO').count()
        return 0

    def clean(self):
        """
        Validação do modelo para garantir que o cliente não ultrapasse
        o limite de animais definido no plano de assinatura.
        """
        # Obter o cliente a partir da propriedade relacionada
        cliente = getattr(self.propriedade, 'cliente', None)
        if not cliente:
            return

        # Verifica se o cliente tem assinatura e plano configurados
        assinatura = getattr(cliente, 'assinatura', None)
        if not assinatura:
            return

        plano = getattr(assinatura, 'plano', None)
        if not plano:
            return

        limite = getattr(plano, 'limite_animais', None)
        # None (NULL) significa ilimitado
        if limite is None:
            return

        # Conta animais ativos do cliente (através das propriedades)
        from django.db.models import Q
        total_animais = Animal.objects.filter(
            propriedade__cliente=cliente,
            ativo=True
        ).exclude(pk=self.pk if self.pk else None).count()

        if total_animais >= limite:
            raise ValidationError(
                f"Limite de animais atingido para o plano atual ({limite})."
            )

    def save(self, *args, **kwargs):
        # Executa validação do modelo antes de salvar para garantir a regra
        try:
            self.full_clean()
        except ValidationError:
            # Propague a exceção para que a camada chamadora possa tratar
            raise
        super().save(*args, **kwargs)


class RegistroPesagem(models.Model):
    """ Registra o peso de um animal em uma data específica. """
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='pesagens')
    data_pesagem = models.DateField()
    peso_kg = models.DecimalField(max_digits=7, decimal_places=2)
    gmd_calculado = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        help_text="GMD calculado automaticamente em relação à pesagem anterior (kg/dia)."
    )
    origem = models.CharField(
        max_length=10,
        choices=[('MANUAL', 'Manual'), ('RFID', 'Balança RFID')],
        default='MANUAL',
    )
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Registro de Pesagem"
        verbose_name_plural = "Registros de Pesagem"
        ordering = ['-data_pesagem']
        
        # ✅ ÍNDICES PARA HISTÓRICO DE PESAGEM
        indexes = [
            models.Index(fields=['animal', '-data_pesagem'], name='pesagem_animal_data_idx'),
            models.Index(fields=['-data_pesagem'], name='pesagem_data_idx'),
            models.Index(fields=['animal', 'peso_kg'], name='pesagem_animal_peso_idx'),
        ]

    def __str__(self):
        return f"Pesagem de {self.animal.brinco} - {self.peso_kg}kg em {self.data_pesagem}"


class Piquete(models.Model):
    """Representa um piquete ou pasto na propriedade"""
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='piquetes_cadastro')
    nome = models.CharField(max_length=100)
    area_hectares = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tipo_vegetacao = models.CharField(max_length=100, blank=True, help_text="Tipo de vegetação/pasto")
    capacidade_maxima = models.PositiveIntegerField(null=True, blank=True, help_text="Capacidade máxima de animais")
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Piquete"
        verbose_name_plural = "Piquetes"
        unique_together = ('propriedade', 'nome')

    def __str__(self):
        return f"{self.nome} - {self.propriedade.nome_propriedade}"


class Vacina(models.Model):
    """Catálogo de vacinas disponíveis"""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    periodo_dose_dias = models.PositiveIntegerField(null=True, blank=True, help_text="Período entre doses em dias")
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Vacina"
        verbose_name_plural = "Vacinas"

    def __str__(self):
        return self.nome


class AplicacaoVacina(models.Model):
    """Registro de aplicação de vacinas em animais"""
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='aplicacoes_vacina')
    vacina = models.ForeignKey(Vacina, on_delete=models.CASCADE)
    data_aplicacao = models.DateField()
    dose = models.CharField(max_length=50, blank=True, help_text="Número da dose ou reforço")
    lote = models.CharField(max_length=50, blank=True, help_text="Lote da vacina")
    veterinario = models.CharField(max_length=100, blank=True)
    observacoes = models.TextField(blank=True)
    proxima_dose = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Aplicação de Vacina"
        verbose_name_plural = "Aplicações de Vacinas"
        ordering = ['-data_aplicacao']

    def __str__(self):
        return f"{self.vacina.nome} - {self.animal.brinco} ({self.data_aplicacao})"


class InformacaoGenetica(models.Model):
    """Informações genéticas detalhadas do animal"""
    animal = models.OneToOneField(Animal, on_delete=models.CASCADE, related_name='informacao_genetica')

    # Informações de pedigree
    registro_genealogico = models.CharField(max_length=100, blank=True, help_text="Número do registro genealógico")
    associacao_genealogica = models.CharField(max_length=100, blank=True, help_text="Associação responsável")

    # Características genéticas
    frame_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    cebvs = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="CEBVs - Expected Breeding Values")
    peso_205_dias = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Peso esperado aos 205 dias")
    peso_365_dias = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Peso esperado aos 365 dias")
    peso_550_dias = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Peso esperado aos 550 dias")

    # Composição corporal
    marmoreio = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="Grau de marmoreio (1-5)")
    area_olho_lombo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Área do olho do lombo (cm²)")

    # Outras características
    fertilidade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Índice de fertilidade")
    temperamento_genetico = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    eficiencia_alimentar = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # DNA e marcadores
    dna_coleta = models.BooleanField(default=False)
    data_coleta_dna = models.DateField(null=True, blank=True)
    marcadores_moleculares = models.TextField(blank=True, help_text="Resultados de marcadores moleculares")

    observacoes_geneticas = models.TextField(blank=True)

    class Meta:
        verbose_name = "Informação Genética"
        verbose_name_plural = "Informações Genéticas"

    def __str__(self):
        return f"Genética - {self.animal.brinco}"


class FichaTecnicaAnimal(models.Model):
    """Ficha técnica completa do animal com todas as informações relevantes"""

    # Relacionamento principal
    animal = models.OneToOneField(Animal, on_delete=models.CASCADE, related_name='ficha_tecnica')

    # === LOCALIZAÇÃO E STATUS ATUAL ===
    piquete_atual = models.ForeignKey(Piquete, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='animais_atuais', help_text="Piquete onde o animal está atualmente")
    data_entrada_piquete = models.DateField(null=True, blank=True)

    # === PESO E GMD (GANHO MÉDIO DIÁRIO) ===
    peso_atual_kg = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    data_ultima_pesagem = models.DateField(null=True, blank=True)

    # GMD calculado automaticamente
    gmd_diario = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text="Ganho Médio Diário (kg/dia)")
    gmd_semanal = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text="Ganho Médio Semanal (kg/semana)")
    gmd_quinzenal = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text="Ganho Médio Quinzenal (kg/quinzena)")
    gmd_mensal = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text="Ganho Médio Mensal (kg/mês)")
    gmd_anual = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text="Ganho Médio Anual (kg/ano)")

    # === INFORMAÇÕES DE SAÚDE ===
    status_saude = models.CharField(max_length=50, choices=[
        ('SAUDAVEL', 'Saudável'),
        ('DOENTE', 'Doente'),
        ('RECUPERANDO', 'Em Recuperação'),
        ('CRONICO', 'Problema Crônico')
    ], default='SAUDAVEL')

    # Vacinas - será populado automaticamente das aplicações
    vacinas_em_dia = models.BooleanField(default=True)
    proxima_vacina = models.DateField(null=True, blank=True)
    observacoes_saude = models.TextField(blank=True)

    # === INFORMAÇÕES DE ALIMENTAÇÃO ===
    racao_diaria_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    suplementacao = models.TextField(blank=True, help_text="Suplementos minerais, vitamínicos, etc.")
    consumo_pasto = models.BooleanField(default=True, help_text="Se consome pasto ou só ração")

    # === INFORMAÇÕES DE PRODUÇÃO ===
    producao_leite_diaria = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                               help_text="Para fêmeas leiteiras")
    ultima_ordemha = models.DateTimeField(null=True, blank=True)

    # === INFORMAÇÕES ECONÔMICAS ===
    custo_diario = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                      help_text="Custo diário de manutenção")
    valor_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                        help_text="Valor de mercado estimado")

    # === INFORMAÇÕES DE COMPORTAMENTO ===
    comportamento_piquete = models.TextField(blank=True, help_text="Como se comporta no piquete")
    hierarquia_social = models.CharField(max_length=50, blank=True, help_text="Posição na hierarquia do grupo")

    # === INFORMAÇÕES DE REPRODUÇÃO (para machos) ===
    numero_cobricoes = models.PositiveIntegerField(default=0, help_text="Número de cobrições realizadas")
    taxa_concepcao = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                        help_text="Taxa de concepção (%)")

    # === HISTÓRICO E OBSERVAÇÕES ===
    historico_clinico = models.TextField(blank=True, help_text="Histórico de doenças, tratamentos, etc.")
    observacoes_gerais = models.TextField(blank=True)

    # === METADADOS ===
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    responsavel_atualizacao = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Ficha Técnica do Animal"
        verbose_name_plural = "Fichas Técnicas dos Animais"

    def __str__(self):
        return f"Ficha Técnica - {self.animal.brinco}"

    def calcular_gmd(self):
        """Calcula o GMD baseado nas pesagens do animal"""
        from django.db.models import Avg, Count
        from django.utils import timezone
        from datetime import timedelta

        # Busca as últimas pesagens (últimos 6 meses)
        seis_meses_atras = timezone.now().date() - timedelta(days=180)
        pesagens = self.animal.pesagens.filter(data_pesagem__gte=seis_meses_atras).order_by('data_pesagem')

        if pesagens.count() < 2:
            return  # Não há dados suficientes

        # Calcula diferenças de peso e tempo
        pesos = list(pesagens.values_list('peso_kg', 'data_pesagem'))
        if len(pesos) < 2:
            return

        # Calcula GMD diário baseado na diferença entre primeira e última pesagem
        primeira_pesagem = pesos[0]
        ultima_pesagem = pesos[-1]

        dias_diferenca = (ultima_pesagem[1] - primeira_pesagem[1]).days
        if dias_diferenca <= 0:
            return

        ganho_total = ultima_pesagem[0] - primeira_pesagem[0]
        self.gmd_diario = ganho_total / dias_diferenca

        # Calcula os outros períodos
        self.gmd_semanal = self.gmd_diario * 7
        self.gmd_quinzenal = self.gmd_diario * 15
        self.gmd_mensal = self.gmd_diario * 30
        self.gmd_anual = self.gmd_diario * 365

    def atualizar_peso_atual(self):
        """Atualiza o peso atual baseado na última pesagem"""
        ultima_pesagem = self.animal.pesagens.order_by('-data_pesagem').first()
        if ultima_pesagem:
            self.peso_atual_kg = ultima_pesagem.peso_kg
            self.data_ultima_pesagem = ultima_pesagem.data_pesagem

    def verificar_vacinas(self):
        """Verifica se as vacinas estão em dia"""
        from django.utils import timezone

        hoje = timezone.now().date()
        aplicacoes_recentes = self.animal.aplicacoes_vacina.filter(
            proxima_dose__isnull=False,
            proxima_dose__gte=hoje
        )

        self.vacinas_em_dia = aplicacoes_recentes.exists()

        # Próxima vacina
        proxima = self.animal.aplicacoes_vacina.filter(
            proxima_dose__isnull=False
        ).order_by('proxima_dose').first()

        if proxima:
            self.proxima_vacina = proxima.proxima_dose

    def save(self, *args, **kwargs):
        # Atualiza informações calculadas antes de salvar
        self.atualizar_peso_atual()
        self.calcular_gmd()
        self.verificar_vacinas()

        super().save(*args, **kwargs)

