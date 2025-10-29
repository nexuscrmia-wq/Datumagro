from django.db import models


class Cliente(models.Model):
    """
    Representa o cliente pagante do sistema, a "conta" principal.
    A conexão com o usuário de login é feita a partir do modelo PerfilUsuario.
    """
    nome_empresa = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    email_contato = models.EmailField(unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

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

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='propriedades')
    nome_propriedade = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255, blank=True)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)  # UF
    cep = models.CharField(max_length=9, blank=True)
    hectares = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    objetivo_producao = models.CharField(max_length=10, choices=OBJETIVO_CHOICES, null=True, blank=True)
    tipo_solo = models.CharField(max_length=10, choices=TIPO_SOLO_CHOICES, null=True, blank=True)
    topografia = models.CharField(max_length=15, choices=TOPOGRAFIA_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = "Propriedade"
        verbose_name_plural = "Propriedades"
        unique_together = ('cliente', 'nome_propriedade')

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

    # --- DEFINIÇÃO DOS CAMPOS ---
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='animais')
    brinco = models.CharField(max_length=50, help_text="Identificação única do animal.")
    raca = models.CharField(max_length=100, choices=RACA_CHOICES)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField()

    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, blank=True)
    temperamento = models.CharField(max_length=20, choices=TEMPERAMENTO_CHOICES, blank=True)
    aptidao = models.CharField(max_length=10, choices=APTIDAO_CHOICES, blank=True)
    status_reprodutivo = models.CharField(max_length=10, choices=STATUS_REPRODUTIVO_CHOICES, blank=True,
                                          help_text="Apenas para fêmeas em idade reprodutiva.")
    is_reprodutor = models.BooleanField(default=False, help_text="Marque se este macho é um reprodutor (touro).")

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

    def __str__(self):
        return f"{self.brinco} ({self.get_raca_display()})"

    @property
    def numero_de_crias(self):
        """ Calcula e retorna o número de partos registrados para esta fêmea. """
        if self.sexo == 'F':
            # Usa a relação reversa 'registros_reprodutivos' definida no modelo RegistroReprodutivo
            return self.registros_reprodutivos.filter(tipo_evento='PARTO').count()
        return 0


class RegistroPesagem(models.Model):
    """ Registra o peso de um animal em uma data específica. """
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='pesagens')
    data_pesagem = models.DateField()
    peso_kg = models.DecimalField(max_digits=7, decimal_places=2)
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Registro de Pesagem"
        verbose_name_plural = "Registros de Pesagem"
        ordering = ['-data_pesagem']

    def __str__(self):
        return f"Pesagem de {self.animal.brinco} - {self.peso_kg}kg em {self.data_pesagem}"