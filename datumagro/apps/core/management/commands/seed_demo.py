"""
python manage.py seed_demo

Cria um ambiente de demonstração completo e realista para:
  - Screenshots para as lojas (App Store / Google Play)
  - Ambiente funcional para o revisor da Apple/Google testarem o app

Totalmente idempotente: pode ser executado múltiplas vezes sem duplicar dados.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

User = get_user_model()


DEMO_PASSWORD = 'demo123'


class Command(BaseCommand):
    help = 'Popula o banco com dados de demonstração realistas (idempotente)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove todos os dados demo antes de recriar (cuidado em produção)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self._reset()

        with transaction.atomic():
            cliente, prop = self._seed_cliente_e_propriedade()
            owner = self._seed_usuarios(prop)
            animais = self._seed_animais(prop)
            self._seed_pesagens(animais)
            self._seed_financeiro(cliente, animais)
            self._seed_embarques(cliente)
            self._seed_alertas(cliente, animais)

        self.stdout.write(self.style.SUCCESS(
            '\n✅  Seed de demonstração concluído com sucesso!\n'
            '   Proprietário : demo@datumagro.com.br  /  demo123\n'
            '   Gerente      : gerente@datumagro.com.br  /  demo123\n'
            '   Peão         : peao@datumagro.com.br  /  demo123\n'
        ))

    # ─────────────────────────────────────────────────────────
    #  RESET
    # ─────────────────────────────────────────────────────────

    def _reset(self):
        from datumagro.apps.cadastros.models import Cliente
        self.stdout.write('  🗑  Removendo dados demo anteriores...')
        for email in ('demo@datumagro.com.br', 'gerente@datumagro.com.br', 'peao@datumagro.com.br'):
            User.objects.filter(email=email).delete()
        Cliente.objects.filter(email_contato='demo@datumagro.com.br').delete()
        self.stdout.write('  ✓  Dados anteriores removidos.')

    # ─────────────────────────────────────────────────────────
    #  CLIENTE + PROPRIEDADE
    # ─────────────────────────────────────────────────────────

    def _seed_cliente_e_propriedade(self):
        from datumagro.apps.cadastros.models import Cliente, Propriedade

        self.stdout.write('  → Cliente e propriedade...')

        cliente, _ = Cliente.objects.get_or_create(
            email_contato='demo@datumagro.com.br',
            defaults={
                'nome_empresa': 'Fazenda Demo Ltda',
                'cpf_cnpj': '12.345.678/0001-90',
                'telefone': '(34) 98888-1234',
            },
        )

        prop, _ = Propriedade.objects.get_or_create(
            cliente=cliente,
            nome_propriedade='Fazenda Demo',
            defaults={
                'cidade': 'Uberaba',
                'estado': 'MG',
                'cep': '38001-000',
                'endereco': 'Rodovia BR-050, km 120',
                'hectares': Decimal('520.00'),
                'objetivo_producao': 'ENGORDA',
                'tipo_solo': 'ARGILOSO',
                'topografia': 'PLANO',
            },
        )

        self.stdout.write('  ✓  Cliente e propriedade OK')
        return cliente, prop

    # ─────────────────────────────────────────────────────────
    #  USUÁRIOS
    # ─────────────────────────────────────────────────────────

    def _seed_usuarios(self, prop):
        self.stdout.write('  → Usuários...')

        from datumagro.apps.usuarios.models import TipoUsuario

        owner = self._get_or_create_user(
            email='demo@datumagro.com.br',
            nome='João Silva Demo',
            tipo=TipoUsuario.PROPRIETARIO,
        )
        gerente = self._get_or_create_user(
            email='gerente@datumagro.com.br',
            nome='Maria Gerente Demo',
            tipo=TipoUsuario.GERENTE,
        )
        peao = self._get_or_create_user(
            email='peao@datumagro.com.br',
            nome='Pedro Peão Demo',
            tipo=TipoUsuario.FUNCIONARIO,
        )

        # Vincula todos à propriedade demo
        for u in (owner, gerente, peao):
            u.propriedades.add(prop)

        self.stdout.write('  ✓  Usuários OK')
        return owner

    def _get_or_create_user(self, email, nome, tipo):
        from datumagro.apps.usuarios.models import TipoUsuario

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': nome.split()[0],
                'last_name': ' '.join(nome.split()[1:]),
                'tipo_usuario': tipo,
                'is_active': True,
            },
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=['password'])
        return user

    # ─────────────────────────────────────────────────────────
    #  ANIMAIS
    # ─────────────────────────────────────────────────────────

    def _seed_animais(self, prop):
        from datumagro.apps.cadastros.models import Animal

        self.stdout.write('  → Animais...')

        specs = [
            # brinco, raca, sexo, nasc, categoria, aptidao, temperamento, reprodutor
            ('BR-001', 'NELORE',  'M', date(2020, 3, 15),  'GARROTE', 'CORTE',  'MANSO',  False),
            ('BR-002', 'NELORE',  'F', date(2021, 6, 20),  'NOVILHA', 'CORTE',  'MANSO',  False),
            ('BR-003', 'ANGUS',   'M', date(2019, 8, 10),  'TOURO',   'CORTE',  'NORMAL', True),
            ('BR-004', 'ANGUS',   'F', date(2022, 1,  5),  'NOVILHA', 'CORTE',  'MANSO',  False),
            ('BR-005', 'NELORE',  'M', date(2020, 11, 30), 'GARROTE', 'CORTE',  'NORMAL', False),
            ('BR-006', 'NELORE',  'F', date(2021, 4, 15),  'NOVILHA', 'CORTE',  'MANSO',  False),
            ('BR-007', 'BRANGUS', 'M', date(2023, 2, 28),  'BEZERRO', 'CORTE',  'MANSO',  False),
            ('BR-008', 'ANGUS',   'F', date(2022, 7, 14),  'NOVILHA', 'DUPLA',  'MANSO',  False),
            ('BR-009', 'SENEPOL', 'M', date(2021, 9,  1),  'GARROTE', 'CORTE',  'BRABO',  False),
            ('BR-010', 'NELORE',  'F', date(2023, 5, 10),  'BEZERRO', 'CORTE',  'MANSO',  False),
        ]

        animais = []
        for brinco, raca, sexo, nasc, cat, apt, temp, reprod in specs:
            animal, _ = Animal.objects.get_or_create(
                propriedade=prop,
                brinco=brinco,
                defaults={
                    'raca': raca,
                    'sexo': sexo,
                    'data_nascimento': nasc,
                    'categoria': cat,
                    'aptidao': apt,
                    'temperamento': temp,
                    'is_reprodutor': reprod,
                    'ativo': True,
                },
            )
            animais.append(animal)

        self.stdout.write(f'  ✓  {len(animais)} animais OK')
        return animais

    # ─────────────────────────────────────────────────────────
    #  PESAGENS
    # ─────────────────────────────────────────────────────────

    def _seed_pesagens(self, animais):
        from datumagro.apps.cadastros.models import RegistroPesagem

        self.stdout.write('  → Pesagens...')

        hoje = date.today()

        # Peso inicial e GMD por animal (kg/dia)
        pesos_iniciais = [320, 210, 480, 195, 310, 205, 120, 190, 295, 95]
        gmds =           [1.0, 0.9, 0.7, 0.85, 0.95, 0.88, 0.75, 0.82, 0.90, 0.70]

        total = 0
        for animal, peso0, gmd in zip(animais, pesos_iniciais, gmds):
            # 4 pesagens espaçadas 60 dias, a partir de 240 dias atrás
            for i in range(4):
                dias_atras = 240 - (i * 60)
                data_pesagem = hoje - timedelta(days=dias_atras)
                peso = round(peso0 + gmd * (240 - dias_atras), 2)

                _, created = RegistroPesagem.objects.get_or_create(
                    animal=animal,
                    data_pesagem=data_pesagem,
                    defaults={'peso_kg': Decimal(str(peso))},
                )
                if created:
                    total += 1

        self.stdout.write(f'  ✓  {total} novas pesagens criadas')

    # ─────────────────────────────────────────────────────────
    #  FINANCEIRO
    # ─────────────────────────────────────────────────────────

    def _seed_financeiro(self, cliente, animais):
        from datumagro.apps.financeiro.models import Categoria, Transacao

        self.stdout.write('  → Financeiro...')

        hoje = date.today()

        # Categorias
        cat_venda, _ = Categoria.objects.get_or_create(
            cliente=cliente, nome='Venda de Animais',
            defaults={'tipo': 'RECEITA'},
        )
        cat_arrend, _ = Categoria.objects.get_or_create(
            cliente=cliente, nome='Arrendamento de Pasto',
            defaults={'tipo': 'RECEITA'},
        )
        cat_racao, _ = Categoria.objects.get_or_create(
            cliente=cliente, nome='Ração e Suplementação',
            defaults={'tipo': 'CUSTO'},
        )
        cat_saude, _ = Categoria.objects.get_or_create(
            cliente=cliente, nome='Medicamentos e Vacinas',
            defaults={'tipo': 'CUSTO'},
        )
        cat_mao, _ = Categoria.objects.get_or_create(
            cliente=cliente, nome='Mão de Obra',
            defaults={'tipo': 'CUSTO'},
        )

        transacoes = [
            (cat_venda,  'Venda de 3 garrotes Nelore — lote MAR/26',      Decimal('15000.00'), hoje - timedelta(days=45)),
            (cat_venda,  'Venda de bezerros desmamados — ABR/26',          Decimal('8500.00'),  hoje - timedelta(days=15)),
            (cat_arrend, 'Arrendamento pasto sul — Maio/26',               Decimal('4500.00'),  hoje - timedelta(days=5)),
            (cat_racao,  'Compra ração mineral 500kg — Abril/26',          Decimal('2300.00'),  hoje - timedelta(days=20)),
            (cat_saude,  'Vacinação aftosa + brucelose — lote completo',   Decimal('850.00'),   hoje - timedelta(days=30)),
            (cat_mao,    'Pagamento funcionários — Maio/26',               Decimal('3200.00'),  hoje - timedelta(days=7)),
        ]

        total = 0
        for cat, desc, valor, dt in transacoes:
            _, created = Transacao.objects.get_or_create(
                cliente=cliente,
                descricao=desc,
                defaults={'categoria': cat, 'valor': valor, 'data': dt},
            )
            if created:
                total += 1

        self.stdout.write(f'  ✓  {total} novas transações criadas')

    # ─────────────────────────────────────────────────────────
    #  EMBARQUES
    # ─────────────────────────────────────────────────────────

    def _seed_embarques(self, cliente):
        from datumagro.apps.logistica.models import Embarque

        self.stdout.write('  → Embarques...')

        hoje = date.today()

        embarques = [
            {
                'numero_embarque': 'DEMO-2026-0001',
                'tipo': 'EXP',
                'status': 'NAV',
                'porto_origem': 'Porto do Açu',
                'porto_destino': 'Porto de Mersin',
                'pais_parceiro': 'Turquia',
                'navio': 'MV Bosphorus Star',
                'viagem': 'BST-0042',
                'data_prevista_embarque': hoje - timedelta(days=12),
                'data_prevista_chegada': hoje + timedelta(days=18),
                'data_real_embarque': hoje - timedelta(days=12),
                'valor_frete': Decimal('45000.00'),
                'valor_seguro': Decimal('8500.00'),
                'valor_total': Decimal('53500.00'),
                'agente_carga': 'Agro Export Brasil Ltda',
                'bl_numero': 'BST2026042001',
                'observacoes': 'Carga de 45 cabeças Nelore, GTA emitida, SIF liberado.',
                'responsavel': cliente,
            },
            {
                'numero_embarque': 'DEMO-2026-0002',
                'tipo': 'EXP',
                'status': 'PLA',
                'porto_origem': 'Porto do Açu',
                'porto_destino': 'Porto de Jeddah',
                'pais_parceiro': 'Arábia Saudita',
                'navio': None,
                'viagem': None,
                'data_prevista_embarque': hoje + timedelta(days=45),
                'data_prevista_chegada': hoje + timedelta(days=75),
                'data_real_embarque': None,
                'valor_frete': Decimal('38000.00'),
                'valor_seguro': Decimal('7200.00'),
                'valor_total': Decimal('45200.00'),
                'agente_carga': 'Agro Export Brasil Ltda',
                'bl_numero': '',
                'observacoes': 'Embarque planejado — aguardando liberação sanitária do MAPA.',
                'responsavel': cliente,
            },
        ]

        total = 0
        for dados in embarques:
            numero = dados.pop('numero_embarque')
            _, created = Embarque.objects.get_or_create(
                numero_embarque=numero,
                defaults=dados,
            )
            if created:
                total += 1

        self.stdout.write(f'  ✓  {total} novos embarques criados')

    # ─────────────────────────────────────────────────────────
    #  ALERTAS DE IA
    # ─────────────────────────────────────────────────────────

    def _seed_alertas(self, cliente, animais):
        from datumagro.apps.inteligencia.models import Alerta

        self.stdout.write('  → Alertas de IA...')

        # Mapeia brinco → animal para referência
        por_brinco = {a.brinco: a for a in animais}

        alertas = [
            {
                'tipo_alerta': 'DESEMPENHO',
                'animal': por_brinco.get('BR-009'),
                'mensagem': (
                    'BR-009 (Senepol, Macho) não registra pesagem há mais de 30 dias. '
                    'O último peso registrado foi de 355 kg. Recomendamos uma nova pesagem '
                    'para avaliar o GMD e ajustar a dieta se necessário.'
                ),
                'status': 'PENDENTE',
            },
            {
                'tipo_alerta': 'SANITARIO',
                'animal': None,
                'mensagem': (
                    'Vencimento da vacina Febre Aftosa para os animais BR-001, BR-002 e BR-005 '
                    'em 15 dias (previsão: próximo mês). Programe a vacinação para manter '
                    'a certificação sanitária do lote de exportação.'
                ),
                'status': 'PENDENTE',
            },
            {
                'tipo_alerta': 'REPRODUTIVO',
                'animal': por_brinco.get('BR-006'),
                'mensagem': (
                    'BR-006 (Nelore, Fêmea, 5 anos) está em período fértil estimado com base '
                    'no histórico reprodutivo. Considere agendar a cobertura com o reprodutor '
                    'BR-003 (Angus) para produção de bezerros cruzados de alto valor.'
                ),
                'status': 'PENDENTE',
            },
        ]

        total = 0
        for dados in alertas:
            # Idempotência por mensagem truncada (evita duplicar ao re-rodar)
            mensagem_key = dados['mensagem'][:80]
            existe = Alerta.objects.filter(
                cliente=cliente,
                mensagem__startswith=mensagem_key,
            ).exists()
            if not existe:
                Alerta.objects.create(cliente=cliente, **dados)
                total += 1

        self.stdout.write(f'  ✓  {total} novos alertas criados')
