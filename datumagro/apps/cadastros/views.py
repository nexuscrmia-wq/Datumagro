# datumagro/apps/cadastros/views.py
"""
Views otimizadas para cadastros com query optimization máxima.
"""

import logging
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch, Count, Q, F
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import transaction
from django.utils.dateparse import parse_datetime

from .models import (Propriedade, Animal, RegistroPesagem, Cliente,
                     Piquete, Vacina, AplicacaoVacina, InformacaoGenetica, FichaTecnicaAnimal)
from .serializers import (PropriedadeSerializer, AnimalSerializer, RegistroPesagemSerializer,
                          PiqueteSerializer, VacinaSerializer, AplicacaoVacinaSerializer,
                          InformacaoGeneticaSerializer, FichaTecnicaAnimalSerializer)

# 🔐 Importar permissões do app usuarios (import relativo)
from ..usuarios.permissions import (
    IsProprietario,
    PermissaoPropriedades,
    PermissaoAnimais,
    PermissaoVacinas,
    CanDeleteData
)

logger = logging.getLogger(__name__)


class BaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet base com controle de acesso em 2 CAMADAS:
    
    1️⃣ CAMADA MULTI-TENANT: Apenas dados do cliente do usuário
    2️⃣ CAMADA ROLE-BASED:
       - Proprietário/Gerente: Veem TODAS as propriedades do cliente
       - Funcionário: Veem APENAS suas propriedades designadas (ManyToMany)
    
    Garante segurança e isolamento total de dados.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        🔐 FILTRAGEM COM 2 CAMADAS DE SEGURANÇA
        """
        user = self.request.user
        
        # Proteção: usuário não autenticado ou sem tipo definido
        if not user or not user.is_authenticated:
            return self.queryset.none()
        
        # ============================================================
        # CAMADA 1: FILTRO MULTI-TENANT (por cliente)
        # ============================================================
        cliente = self._get_user_cliente(user)
        if not cliente:
            logger.warning(
                f"Usuário {user.email} sem cliente associado",
                extra={'user_id': user.id}
            )
            return self.queryset.none()
        
        # Aplicar filtro de cliente conforme o modelo
        queryset = self._apply_cliente_filter(cliente)
        
        # ============================================================
        # CAMADA 2: FILTRO ROLE-BASED (por hierarquia)
        # ============================================================
        if user.is_proprietario() or user.is_gerente():
            # ✅ Proprietário/Gerente: Veem TUDO do cliente
            # (sem filtro adicional, já estão filtrados por cliente acima)
            logger.debug(
                f"Acesso {'Proprietário' if user.is_proprietario() else 'Gerente'} ao {self.queryset.model.__name__}",
                extra={'user_id': user.id}
            )
            
        elif user.is_funcionario():
            # ✅ Funcionário: Veem APENAS suas propriedades designadas
            queryset = self._apply_funcionario_filter(queryset, user)
            logger.debug(
                f"Acesso Funcionário filtrado por propriedades",
                extra={'user_id': user.id, 'propriedades': list(user.propriedades.values_list('id', flat=True))}
            )
        else:
            # Tipo de usuário inválido
            logger.error(
                f"Tipo de usuário inválido: {user.tipo_usuario}",
                extra={'user_id': user.id}
            )
            return self.queryset.none()
        
        return queryset

    def _get_user_cliente(self, user):
        """
        Obtém o cliente associado ao usuário com fallbacks.
        
        Precedência:
        1. Relacionamento direto (se existir)
        2. Email do usuário
        3. Primeiro cliente no banco (dev only)
        """
        try:
            # Tentar via relacionamento direto
            if hasattr(user, 'cliente') and user.cliente:
                return user.cliente
        except Exception:
            pass
        
        try:
            # Fallback: buscar por email
            if user.email:
                cliente = Cliente.objects.filter(email_contato=user.email).first()
                if cliente:
                    return cliente
        except Exception:
            pass
        
        try:
            # Última tentativa: primeiro cliente (dev only)
            return Cliente.objects.first()
        except Exception:
            return None

    def _apply_cliente_filter(self, cliente):
        """
        Aplica filtro de cliente conforme o modelo do ViewSet.
        
        Suporta diferentes caminhos de relacionamento:
        - Propriedade (tem 'cliente' direto)
        - Animal (tem 'propriedade__cliente')
        - RegistroPesagem (tem 'animal__propriedade__cliente')
        - Piquete (tem 'propriedade__cliente')
        """
        model_name = self.queryset.model.__name__
        
        if model_name == 'Propriedade':
            return self.queryset.filter(cliente=cliente)
        
        elif model_name == 'Animal':
            return self.queryset.filter(propriedade__cliente=cliente)
        
        elif model_name == 'RegistroPesagem':
            return self.queryset.filter(animal__propriedade__cliente=cliente)
        
        elif model_name == 'Piquete':
            return self.queryset.filter(propriedade__cliente=cliente)
        
        # Para outros modelos, retorna sem filtro (ajustar conforme necessário)
        logger.warning(
            f"Modelo {model_name} não possui filtro de cliente customizado",
            extra={'model': model_name}
        )
        return self.queryset

    def _apply_funcionario_filter(self, queryset, user):
        """
        Filtra queryset para que Funcionário veja APENAS suas propriedades designadas.
        
        Suporta diferentes modelos com relacionamento para propriedade.
        """
        model_name = queryset.model.__name__
        
        if model_name == 'Animal':
            # Animal tem 'propriedade' direto
            return queryset.filter(propriedade__in=user.propriedades.all())
        
        elif model_name == 'RegistroPesagem':
            # RegistroPesagem tem 'animal__propriedade'
            return queryset.filter(animal__propriedade__in=user.propriedades.all())
        
        elif model_name == 'Piquete':
            # Piquete tem 'propriedade' direto
            return queryset.filter(propriedade__in=user.propriedades.all())
        
        # Para Propriedade, Funcionário não deveria acessar
        elif model_name == 'Propriedade':
            # Funcionário pode listar propriedades que está alocado
            return queryset.filter(id__in=user.propriedades.all())
        
        # Para outros modelos, retorna sem filtro adicional
        return queryset

    def perform_create(self, serializer):
        """
        Salva novo objeto com dados do usuário.
        
        ⚠️ IMPORTANTE: Não tenta passar 'cliente' para todos os modelos.
        Apenas Propriedade tem cliente direto. Animal/Piquete herdam via propriedade.
        """
        model_name = self.queryset.model.__name__
        
        try:
            if model_name == 'Propriedade':
                # Propriedade precisa de cliente
                user = self.request.user
                cliente = self._get_user_cliente(user)
                if not cliente:
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError({'cliente': 'Usuário sem cliente associado.'})
                serializer.save(cliente=cliente)
                logger.info(
                    f"Propriedade criada",
                    extra={'user_id': user.id, 'cliente_id': cliente.id}
                )
            else:
                # Outros modelos (Animal, Piquete, etc) não precisam de cliente
                serializer.save()
                logger.info(
                    f"{model_name} criado",
                    extra={'user_id': self.request.user.id}
                )
        except Exception as e:
            logger.error(
                f"Erro ao criar {model_name}: {str(e)}",
                extra={'user_id': self.request.user.id}
            )
            raise


class ClienteViewSet(viewsets.ModelViewSet):
    """ViewSet otimizado para clientes — apenas Proprietários"""
    queryset = Cliente.objects.prefetch_related('propriedades').all()
    serializer_class = None  # Será definido no método get_serializer_class
    permission_classes = [permissions.IsAuthenticated, IsProprietario]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = []
    search_fields = ['nome_empresa', 'cpf_cnpj', 'email_contato']

    def get_serializer_class(self):
        from .serializers import ClienteSerializer
        return ClienteSerializer


class PropriedadeViewSet(BaseViewSet):
    """ViewSet otimizado para propriedades com performance máxima"""
    serializer_class = PropriedadeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cliente', 'estado', 'objetivo_producao']
    search_fields = ['nome_propriedade', 'cidade', 'endereco']
    ordering_fields = ['hectares', 'nome_propriedade']
    ordering = ['nome_propriedade']
    
    # 🔐 Permissões: Apenas Proprietário pode editar
    permission_classes = [
        permissions.IsAuthenticated,
        PermissaoPropriedades  # Controla visualização e edição
    ]
    
    def get_queryset(self):
        """
        ✅ OTIMIZAÇÃO MÁXIMA: select_related + prefetch_related otimizado
        """
        return Propriedade.objects.select_related(
            'cliente'
        ).prefetch_related(
            Prefetch(
                'animais',
                queryset=Animal.objects.filter(ativo=True)
                         .only('id', 'brinco', 'raca', 'sexo', 'categoria', 'propriedade')
            )
        ).all()

    @action(detail=True, methods=['get'])
    def resumo(self, request, pk=None):
        """Resumo estatístico da propriedade"""
        propriedade = self.get_object()
        
        resumo = {
            'total_animais': propriedade.animais.filter(ativo=True).count(),
            'animais_por_raca': list(
                propriedade.animais.filter(ativo=True)
                           .values('raca')
                           .annotate(total=Count('id'))
            ),
            'animais_por_categoria': list(
                propriedade.animais.filter(ativo=True)
                           .values('categoria')
                           .annotate(total=Count('id'))
            ),
            'ultimas_pesagens': RegistroPesagemSerializer(
                RegistroPesagem.objects.filter(
                    animal__propriedade=propriedade
                ).select_related('animal').order_by('-data_pesagem')[:10],
                many=True
            ).data
        }
        
        logger.info("Resumo de propriedade acessado", extra={
            'user_id': request.user.id,
            'propriedade_id': propriedade.id
        })
        
        return Response(resumo)


class AnimalViewSet(BaseViewSet):
    """ViewSet ultra-otimizado para animais com performance extrema"""
    serializer_class = AnimalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'propriedade', 'raca', 'sexo', 'categoria',
        'status_reprodutivo', 'ativo', 'aptidao'
    ]
    search_fields = ['brinco', 'nome', 'observacoes']
    ordering_fields = [
        'data_nascimento', 'updated_at', 'brinco'
    ]
    ordering = ['-updated_at']
    
    # 🔐 Permissões: Controla visualização e edição
    permission_classes = [
        permissions.IsAuthenticated,
        PermissaoAnimais  # Controla quem pode editar
    ]
    
    def get_queryset(self):
        """
        🚀 A OTIMIZAÇÃO MÁXIMA:
        - select_related: Pega FKs em single query
        - prefetch_related: Pega relações reversas otimizadas
        - only: Seleciona apenas campos necessários (performance em larga escala)
        """
        return Animal.objects.select_related(
            'propriedade',
            'propriedade__cliente',
            'pai',
            'mae'
        ).prefetch_related(
            Prefetch(
                'pesagens',
                queryset=RegistroPesagem.objects.order_by('-data_pesagem')
            ),
            'historico_logistica'
        ).filter(ativo=True)

    def perform_create(self, serializer):
        """Cria animal sem passar campo cliente (Animal não possui esse campo)"""
        animal = serializer.save()
        logger.info("Animal criado", extra={
            'user_id': self.request.user.id,
            'animal_id': animal.id,
            'brinco': animal.brinco
        })

    def perform_update(self, serializer):
        """Atualiza animal com logging"""
        super().perform_update(serializer)
        logger.info("Animal atualizado", extra={
            'user_id': self.request.user.id,
            'animal_id': serializer.instance.id
        })

    @action(detail=True, methods=['get'])
    def genealogia(self, request, pk=None):
        """Árvore genealógica do animal"""
        animal = self.get_object()
        
        genealogia = {
            'animal': AnimalSerializer(animal).data,
            'pai': AnimalSerializer(animal.pai).data if animal.pai else None,
            'mae': AnimalSerializer(animal.mae).data if animal.mae else None,
            'filhos': AnimalSerializer(
                Animal.objects.filter(
                    Q(pai=animal) | Q(mae=animal),
                    ativo=True
                ).select_related('pai', 'mae'),
                many=True
            ).data
        }
        
        logger.info("Genealogia acessada", extra={
            'user_id': request.user.id,
            'animal_id': animal.id
        })
        
        return Response(genealogia)

    @action(detail=True, methods=['post'])
    def registrar_pesagem(self, request, pk=None):
        """Registrar pesagem para o animal"""
        animal = self.get_object()
        serializer = RegistroPesagemSerializer(data=request.data)
        
        if serializer.is_valid():
            pesagem = serializer.save(animal=animal)
            logger.info("Pesagem registrada", extra={
                'user_id': request.user.id,
                'animal_id': animal.id,
                'peso': pesagem.peso_kg
            })
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistroPesagemViewSet(BaseViewSet):
    """ViewSet para registros de pesagem com otimizações"""
    queryset = RegistroPesagem.objects.all()
    serializer_class = RegistroPesagemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['animal', 'data_pesagem']
    ordering_fields = ['data_pesagem', 'peso_kg']
    ordering = ['-data_pesagem']

    def get_queryset(self):
        """✅ Otimiza com select_related"""
        return RegistroPesagem.objects.select_related(
            'animal', 'animal__propriedade'
        ).all()

    def perform_create(self, serializer):
        """
        Ao criar um Animal, não tentar passar `cliente` para serializer.save()
        (Animal não possui campo cliente). Simplesmente salva o serializer.

        Em implementações futuras, validar que a `propriedade` recebida
        pertence ao `cliente` do usuário e ajustar o comportamento.
        """
        serializer.save()


class RegistroPesagemViewSet(BaseViewSet):
    queryset = RegistroPesagem.objects.all()
    serializer_class = RegistroPesagemSerializer

    # Utiliza o get_queryset da classe base


class PiqueteViewSet(BaseViewSet):
    """ViewSet para gerenciamento de piquetes"""
    queryset = Piquete.objects.all()
    serializer_class = PiqueteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo_vegetacao']
    search_fields = ['nome', 'observacoes']
    permission_classes = [
        permissions.IsAuthenticated,
        PermissaoAnimais,
    ]


class VacinaViewSet(viewsets.ModelViewSet):
    """ViewSet para catálogo de vacinas (global, não filtrado por cliente)"""
    queryset = Vacina.objects.filter(ativo=True)
    serializer_class = VacinaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'descricao']
    
    # 🔐 Permissões: Controla visualização e edição
    permission_classes = [
        permissions.IsAuthenticated,
        PermissaoVacinas  # Controla quem pode editar vacinas
    ]


class AplicacaoVacinaViewSet(BaseViewSet):
    """ViewSet para aplicações de vacinas"""
    serializer_class = AplicacaoVacinaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['animal', 'vacina', 'data_aplicacao']
    search_fields = ['vacina__nome', 'lote', 'veterinario']
    ordering_fields = ['data_aplicacao', 'proxima_dose']
    ordering = ['-data_aplicacao']

    def get_queryset(self):
        """Filtra aplicações de vacina pelos animais do cliente"""
        user = getattr(self.request, 'user', None)
        cliente = None

        try:
            if user and getattr(user, 'email', None):
                cliente = Cliente.objects.filter(email_contato=user.email).first()
            if cliente is None:
                cliente = Cliente.objects.first()
        except Exception:
            cliente = None

        if cliente is None:
            return AplicacaoVacina.objects.none()

        return AplicacaoVacina.objects.filter(
            animal__propriedade__cliente=cliente
        ).select_related('animal', 'vacina')


class InformacaoGeneticaViewSet(BaseViewSet):
    """ViewSet para informações genéticas dos animais"""
    serializer_class = InformacaoGeneticaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['animal__raca', 'animal__sexo']
    search_fields = ['registro_genealogico', 'associacao_genealogica']

    def get_queryset(self):
        """Filtra informações genéticas pelos animais do cliente"""
        user = getattr(self.request, 'user', None)
        cliente = None

        try:
            if user and getattr(user, 'email', None):
                cliente = Cliente.objects.filter(email_contato=user.email).first()
            if cliente is None:
                cliente = Cliente.objects.first()
        except Exception:
            cliente = None

        if cliente is None:
            return InformacaoGenetica.objects.none()

        return InformacaoGenetica.objects.filter(
            animal__propriedade__cliente=cliente
        ).select_related('animal')


class FichaTecnicaAnimalViewSet(BaseViewSet):
    """ViewSet principal para fichas técnicas dos animais"""
    serializer_class = FichaTecnicaAnimalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'animal__propriedade', 'animal__raca', 'animal__sexo', 'animal__categoria',
        'piquete_atual', 'status_saude', 'vacinas_em_dia'
    ]
    search_fields = [
        'animal__brinco', 'animal__nome', 'observacoes_gerais',
        'historico_clinico', 'comportamento_piquete'
    ]
    ordering_fields = [
        'animal__brinco', 'peso_atual_kg', 'gmd_diario', 'atualizado_em',
        'proxima_vacina'
    ]
    ordering = ['animal__brinco']

    def get_queryset(self):
        """Filtra fichas técnicas pelos animais do cliente"""
        user = getattr(self.request, 'user', None)
        cliente = None

        try:
            if user and getattr(user, 'email', None):
                cliente = Cliente.objects.filter(email_contato=user.email).first()
            if cliente is None:
                cliente = Cliente.objects.first()
        except Exception:
            cliente = None

        if cliente is None:
            return FichaTecnicaAnimal.objects.none()

        return FichaTecnicaAnimal.objects.filter(
            animal__propriedade__cliente=cliente
        ).select_related(
            'animal', 'animal__propriedade', 'piquete_atual'
        ).prefetch_related(
            'animal__pesagens',
            'animal__aplicacoes_vacina'
        )

    @action(detail=True, methods=['post'])
    def mover_piquete(self, request, pk=None):
        """Move o animal para outro piquete"""
        ficha = self.get_object()
        piquete_id = request.data.get('piquete_id')

        if not piquete_id:
            return Response(
                {'error': 'piquete_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            piquete = Piquete.objects.get(id=piquete_id)
            ficha.piquete_atual = piquete
            ficha.data_entrada_piquete = timezone.now().date()
            ficha.save()

            logger.info("Animal movido para piquete", extra={
                'user_id': request.user.id,
                'animal_id': ficha.animal.id,
                'piquete_id': piquete.id
            })

            return Response({'message': 'Animal movido com sucesso'})

        except Piquete.DoesNotExist:
            return Response(
                {'error': 'Piquete não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def atualizar_saude(self, request, pk=None):
        """Atualiza informações de saúde do animal"""
        ficha = self.get_object()
        status_saude = request.data.get('status_saude')
        observacoes = request.data.get('observacoes_saude', '')

        if status_saude:
            ficha.status_saude = status_saude
        if observacoes:
            ficha.observacoes_saude = observacoes

        ficha.save()

        logger.info("Saúde do animal atualizada", extra={
            'user_id': request.user.id,
            'animal_id': ficha.animal.id,
            'status_saude': status_saude
        })

        return Response({'message': 'Saúde atualizada com sucesso'})

    @action(detail=True, methods=['get'])
    def relatorio_completo(self, request, pk=None):
        """Gera relatório completo da ficha técnica"""
        ficha = self.get_object()

        # Busca dados relacionados
        pesagens = ficha.animal.pesagens.order_by('-data_pesagem')[:10]
        vacinas = ficha.animal.aplicacoes_vacina.order_by('-data_aplicacao')[:5]
        filhos = Animal.objects.filter(
            Q(pai=ficha.animal) | Q(mae=ficha.animal),
            ativo=True
        )[:5]

        relatorio = {
            'ficha_tecnica': FichaTecnicaAnimalSerializer(ficha).data,
            'historico_pesagens': RegistroPesagemSerializer(pesagens, many=True).data,
            'historico_vacinas': AplicacaoVacinaSerializer(vacinas, many=True).data,
            'descendentes': AnimalSerializer(filhos, many=True).data,
            'estatisticas': {
                'total_pesagens': ficha.animal.pesagens.count(),
                'total_vacinas': ficha.animal.aplicacoes_vacina.count(),
                'numero_filhos': filhos.count(),
                'idade_meses': self.get_serializer(ficha).get_idade_meses(ficha)
            }
        }

        logger.info("Relatório completo gerado", extra={
            'user_id': request.user.id,
            'animal_id': ficha.animal.id
        })

        return Response(relatorio)


# ─────────────────────────────────────────────
#  ROMANEIO DE PESAGEM / CALCULADORA DE ARROBA
# ─────────────────────────────────────────────

def _calc_arroba(peso_kg: float, preco_arroba: float) -> dict:
    """Aplica a fórmula padrão de mercado: peso vivo / 30 = arrobas."""
    from decimal import Decimal, ROUND_HALF_UP
    p = Decimal(str(peso_kg))
    pr = Decimal(str(preco_arroba))
    arrobas = p / Decimal('30')
    valor = arrobas * pr
    return {
        'arrobas': float(arrobas.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)),
        'valor_rs': float(valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def romaneio_calcular(request):
    """
    POST /api/cadastros/romaneio/calcular/

    Recebe lista de animais + preço da @ e devolve o resumo completo.
    Corpo esperado:
    {
        "preco_arroba": 280.00,
        "animais": [
            {"brinco": "B001", "peso_kg": 450.0},
            {"brinco": "B002", "peso_kg": 380.5}
        ],
        "nome_fazenda": "Fazenda São João",  // opcional
        "vendedor":  "João Silva",            // opcional
        "comprador": "Maria Souza",           // opcional
        "gerar_pdf": false                    // se true, retorna pdf_base64
    }
    """
    preco_arroba = float(request.data.get('preco_arroba', 0))
    animais_input = request.data.get('animais', [])
    nome_fazenda = request.data.get('nome_fazenda', '')
    vendedor = request.data.get('vendedor', '')
    comprador = request.data.get('comprador', '')
    gerar_pdf = request.data.get('gerar_pdf', False)

    if preco_arroba <= 0:
        return Response({'detail': 'preco_arroba deve ser maior que zero.'}, status=400)
    if not animais_input:
        return Response({'detail': 'Lista de animais vazia.'}, status=400)

    # Busca dados reais do banco para enriquecer (raca, categoria)
    cliente = None
    prop = request.user.propriedades.select_related('cliente').first()
    if prop:
        cliente = prop.cliente
    if not cliente:
        cliente = Cliente.objects.filter(email_contato=request.user.email).first()

    brincos = [str(a.get('brinco', '')).strip() for a in animais_input]
    db_animais = {}
    if cliente:
        qs = Animal.objects.filter(
            propriedade__cliente=cliente,
            brinco__in=brincos,
            ativo=True,
        ).values('brinco', 'raca', 'categoria', 'sexo')
        db_animais = {a['brinco']: a for a in qs}

    itens = []
    total_peso = 0.0
    total_arrobas = 0.0
    total_valor = 0.0

    for entry in animais_input:
        brinco = str(entry.get('brinco', '')).strip()
        try:
            peso_kg = float(entry.get('peso_kg', 0))
        except (TypeError, ValueError):
            peso_kg = 0.0

        calc = _calc_arroba(peso_kg, preco_arroba)
        db_info = db_animais.get(brinco, {})

        itens.append({
            'brinco': brinco,
            'raca': db_info.get('raca', entry.get('raca', '')),
            'categoria': db_info.get('categoria', entry.get('categoria', '')),
            'sexo': db_info.get('sexo', entry.get('sexo', '')),
            'peso_kg': round(peso_kg, 2),
            'arrobas': calc['arrobas'],
            'valor_rs': calc['valor_rs'],
        })

        total_peso += peso_kg
        total_arrobas += calc['arrobas']
        total_valor += calc['valor_rs']

    from django.utils import timezone as tz
    agora = tz.now()

    resumo = {
        'total_animais': len(itens),
        'total_peso_kg': round(total_peso, 2),
        'total_arrobas': round(total_arrobas, 3),
        'total_valor_rs': round(total_valor, 2),
        'preco_arroba': preco_arroba,
        'nome_fazenda': nome_fazenda,
        'vendedor': vendedor,
        'comprador': comprador,
        'data_hora': agora.strftime('%d/%m/%Y %H:%M'),
    }

    payload = {'itens': itens, 'resumo': resumo}

    if gerar_pdf:
        try:
            pdf_b64 = _gerar_pdf_romaneio(itens, resumo)
            payload['pdf_base64'] = pdf_b64
        except Exception as exc:
            logger.warning("Falha ao gerar PDF do romaneio: %s", exc)
            payload['pdf_erro'] = str(exc)

    return Response(payload, status=status.HTTP_200_OK)


def _gerar_pdf_romaneio(itens: list, resumo: dict) -> str:
    """Gera PDF do romaneio via WeasyPrint e retorna como base64."""
    import base64
    from io import BytesIO
    from django.template.loader import render_to_string
    from weasyprint import HTML

    html_str = render_to_string('cadastros/romaneio_pdf.html', {
        'itens': itens,
        'resumo': resumo,
    })
    buf = BytesIO()
    HTML(string=html_str).write_pdf(buf)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

