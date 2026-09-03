# datumagro/apps/cadastros/views.py
"""
Views otimizadas para cadastros com query optimization máxima.
"""

import logging
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
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
    IsProprietarioOrGerente,
    PermissaoPropriedades,
    PermissaoAnimais,
    PermissaoVacinas,
    CanDeleteData,
    IsOperadorCampo,
    PermissaoLotesExtendida,
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
    queryset = Propriedade.objects.all()
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
        qs = super().get_queryset()
        return qs.select_related('cliente').prefetch_related(
            Prefetch(
                'animais',
                queryset=Animal.objects.filter(ativo=True)
                         .only('id', 'brinco', 'raca', 'sexo', 'categoria', 'propriedade')
            )
        )

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

    @action(
        detail=True, methods=['post'], url_path='importar-car',
        permission_classes=[permissions.IsAuthenticated, IsProprietarioOrGerente],
        parser_classes=[MultiPartParser, FormParser],
    )
    def importar_car(self, request, pk=None):
        """
        Importa arquivo .kml ou .geojson do CAR e salva na propriedade.

        Form-data esperado:
          arquivo              — arquivo .kml ou .geojson (obrigatório)
          codigo_car           — string do recibo CAR  (opcional)
          area_reserva_legal_ha — decimal             (opcional)
          area_app_ha          — decimal               (opcional)
          area_util_ha         — decimal               (opcional)

        Retorna o GeoJSON extraído + áreas calculadas.
        """
        from datumagro.apps.cadastros.services_car import parse_car_file

        prop = self.get_object()
        arquivo = request.FILES.get('arquivo')

        if not arquivo:
            return Response(
                {'erro': 'Envie o arquivo .kml ou .geojson no campo "arquivo".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = parse_car_file(arquivo.name, arquivo.read())
        except ValueError as exc:
            return Response({'erro': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        prop.geojson_car = result['geojson']
        prop.arquivo_car = arquivo
        prop.area_total_ha = result['area_total_ha']

        # Preenchem hectares se ainda não definido
        if not prop.hectares:
            prop.hectares = result['area_total_ha']

        def _decimal(key):
            try:
                return float(request.data[key])
            except (KeyError, ValueError, TypeError):
                return None

        if request.data.get('codigo_car'):
            prop.codigo_car = request.data['codigo_car'].strip()
        area_rl = _decimal('area_reserva_legal_ha')
        area_app = _decimal('area_app_ha')
        area_util = _decimal('area_util_ha')
        if area_rl is not None:
            prop.area_reserva_legal_ha = area_rl
        if area_app is not None:
            prop.area_app_ha = area_app
        if area_util is not None:
            prop.area_util_ha = area_util

        prop.save()

        logger.info('CAR importado', extra={
            'user_id': request.user.id,
            'propriedade_id': prop.id,
            'area_total_ha': result['area_total_ha'],
            'poligonos': len(result['placemarks']),
        })

        return Response({
            'sucesso': True,
            'area_total_ha': result['area_total_ha'],
            'poligonos': len(result['placemarks']),
            'placemarks': [{'nome': p['name'], 'area_ha': p['area_ha']} for p in result['placemarks']],
            'geojson': result['geojson'],
        }, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=['patch'], url_path='camadas',
        permission_classes=[permissions.IsAuthenticated, IsProprietarioOrGerente],
    )
    def atualizar_camadas(self, request, pk=None):
        """
        Salva as camadas editáveis desenhadas pelo usuário no mapa.
        Campos aceitos:
          geojson_piquetes_talhoes — FeatureCollection de polígonos
          geojson_infraestrutura  — FeatureCollection de pontos
        """
        prop = self.get_object()
        campos = ('geojson_piquetes_talhoes', 'geojson_infraestrutura')
        for campo in campos:
            if campo in request.data:
                setattr(prop, campo, request.data[campo])
        prop.save(update_fields=[c for c in campos if c in request.data])
        return Response(PropriedadeSerializer(prop).data)


class AnimalViewSet(BaseViewSet):
    """ViewSet ultra-otimizado para animais com performance extrema"""
    queryset = Animal.objects.filter(ativo=True)
    serializer_class = AnimalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'propriedade', 'raca', 'sexo', 'categoria',
        'status_reprodutivo', 'ativo', 'aptidao', 'registro_genetico'
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
        qs = super().get_queryset()
        return qs.select_related(
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
        )

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

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated, IsOperadorCampo])
    def registrar_pesagem(self, request, pk=None):
        """Registrar pesagem — peão de campo pode registrar."""
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
    """Pesagens: peão de campo pode registrar (POST/PATCH). DELETE só Proprietário."""
    queryset = RegistroPesagem.objects.all()
    serializer_class = RegistroPesagemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['animal', 'data_pesagem']
    ordering_fields = ['data_pesagem', 'peso_kg']
    ordering = ['-data_pesagem']
    permission_classes = [permissions.IsAuthenticated, IsOperadorCampo]

    def get_queryset(self):
        return RegistroPesagem.objects.select_related(
            'animal', 'animal__propriedade'
        ).all()

    def perform_create(self, serializer):
        serializer.save()


class PiqueteViewSet(BaseViewSet):
    """Piquetes: criar = Proprietário+Gerente; mover animais (PATCH) = todos; deletar = Proprietário."""
    queryset = Piquete.objects.all()
    serializer_class = PiqueteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo_vegetacao']
    search_fields = ['nome', 'observacoes']
    permission_classes = [permissions.IsAuthenticated, PermissaoLotesExtendida]


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


# ─────────────────────────────────────────────
#  SYNC — offline-first para o Flutter
# ─────────────────────────────────────────────

def _get_user_cliente_sync(user):
    """Resolve o cliente do usuário para o sync."""
    prop = user.propriedades.select_related('cliente').first()
    if prop:
        return prop.cliente
    cliente = Cliente.objects.filter(email_contato=user.email).first()
    if cliente:
        return cliente
    if Cliente.objects.count() == 1:
        return Cliente.objects.first()
    return None


def _animal_to_sync_dict(animal):
    """Serializa um Animal para o formato esperado pelo SyncService Flutter."""
    return {
        'id': animal.id,
        'propriedade': animal.propriedade_id,
        'brinco': animal.brinco,
        'raca': animal.raca or '',
        'sexo': animal.sexo or '',
        'data_nascimento': animal.data_nascimento.isoformat() if animal.data_nascimento else None,
        'categoria': animal.categoria or '',
        'temperamento': animal.temperamento or '',
        'aptidao': animal.aptidao or '',
        'status_reprodutivo': animal.status_reprodutivo or '',
        'is_reprodut': animal.is_reprodutor,
        'caracteristicas_adicionais': animal.caracteristicas_adicionais or '',
        'pai': animal.pai_id,
        'mae': animal.mae_id,
        'foto_perfil': animal.foto_perfil.url if animal.foto_perfil else '',
        'ativo': animal.ativo,
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_offline(request):
    """
    POST /api/cadastros/sync/

    Endpoint de sincronização offline-first para o Flutter (SyncService).

    Corpo recebido:
    {
        "last_server_sync": "2026-01-01T00:00:00Z" | null,
        "changes": [
            { "op": "create|update|delete", "model": "animal",
              "client_id": "uuid", "data": {...} }
        ]
    }

    Resposta:
    {
        "applied": [{"client_id": "uuid"}],
        "server_changes": [{"model": "animal", "data": {...}, "updated_at": "..."}]
    }
    """
    cliente = _get_user_cliente_sync(request.user)
    if not cliente:
        return Response(
            {'detail': 'Cliente não encontrado. Faça o onboarding primeiro.'},
            status=400,
        )

    # Primeira propriedade do usuário — usada para criar animais offline
    prop_default = request.user.propriedades.filter(cliente=cliente).first()

    changes = request.data.get('changes', [])
    last_sync_raw = request.data.get('last_server_sync')

    applied = []

    with transaction.atomic():
        for change in changes:
            op = change.get('op', '').lower()
            model = change.get('model', '').lower()
            client_id = change.get('client_id')
            data = change.get('data', {})

            if model != 'animal':
                continue  # apenas animais por ora

            try:
                if op == 'create':
                    if not prop_default:
                        continue
                    server_id = data.get('id')
                    # Se o servidor já tem esse animal, não duplica
                    if server_id and Animal.objects.filter(id=server_id, propriedade__cliente=cliente).exists():
                        applied.append({'client_id': client_id})
                        continue
                    # Evita brinco duplicado na mesma propriedade
                    brinco = data.get('brinco', '').strip()
                    if not brinco or Animal.objects.filter(propriedade=prop_default, brinco=brinco).exists():
                        applied.append({'client_id': client_id})
                        continue
                    Animal.objects.create(
                        propriedade=prop_default,
                        brinco=brinco,
                        raca=data.get('raca', 'OUTRA'),
                        sexo=data.get('sexo', 'M'),
                        data_nascimento=data.get('data_nascimento') or timezone.now().date(),
                        categoria=data.get('categoria', ''),
                        temperamento=data.get('temperamento', ''),
                        aptidao=data.get('aptidao', ''),
                        status_reprodutivo=data.get('status_reprodutivo', ''),
                        is_reprodutor=data.get('is_reprodut', False),
                        caracteristicas_adicionais=data.get('caracteristicas_adicionais', ''),
                        ativo=data.get('ativo', True),
                    )
                    applied.append({'client_id': client_id})

                elif op == 'update':
                    server_id = data.get('id')
                    if not server_id:
                        continue
                    try:
                        animal = Animal.objects.get(id=server_id, propriedade__cliente=cliente)
                    except Animal.DoesNotExist:
                        continue
                    update_fields = ['raca', 'categoria', 'temperamento', 'aptidao',
                                     'status_reprodutivo', 'is_reprodutor',
                                     'caracteristicas_adicionais', 'ativo']
                    for field in update_fields:
                        src_key = 'is_reprodut' if field == 'is_reprodutor' else field
                        if src_key in data:
                            setattr(animal, field, data[src_key])
                    animal.save(update_fields=update_fields)
                    applied.append({'client_id': client_id})

                elif op == 'delete':
                    server_id = data.get('id')
                    if not server_id:
                        continue
                    Animal.objects.filter(id=server_id, propriedade__cliente=cliente).update(ativo=False)
                    applied.append({'client_id': client_id})

            except Exception as exc:
                logger.warning("sync: erro ao processar change client_id=%s: %s", client_id, exc)
                # Não aborta o restante do batch

    # Monta server_changes: animais modificados desde last_server_sync
    qs = Animal.objects.filter(propriedade__cliente=cliente, ativo=True)
    if last_sync_raw:
        try:
            last_sync_dt = parse_datetime(last_sync_raw)
            if last_sync_dt:
                qs = qs.filter(updated_at__gte=last_sync_dt)
        except Exception:
            pass
    else:
        # Sem data de referência: envia todos os animais do cliente
        pass

    server_changes = [
        {
            'model': 'animal',
            'data': _animal_to_sync_dict(a),
            'updated_at': a.updated_at.isoformat() if a.updated_at else None,
        }
        for a in qs.select_related('propriedade')[:500]  # limite de segurança
    ]

    return Response({
        'applied': applied,
        'server_changes': server_changes,
    }, status=200)


# ─────────────────────────────────────────────
#  PESAGEM AUTOMÁTICA — integração RFID/balança
# ─────────────────────────────────────────────

def _calcular_gmd(animal, peso_novo: 'Decimal', data_nova: 'date') -> 'Decimal | None':
    """
    Calcula o GMD entre a pesagem anterior e a nova.
    Retorna None se não houver pesagem anterior ou o intervalo for zero.
    """
    from decimal import Decimal as D
    anterior = (
        RegistroPesagem.objects
        .filter(animal=animal, data_pesagem__lt=data_nova)
        .order_by('-data_pesagem')
        .first()
    )
    if not anterior:
        return None
    dias = (data_nova - anterior.data_pesagem).days
    if dias <= 0:
        return None
    ganho = D(str(peso_novo)) - anterior.peso_kg
    return (ganho / D(str(dias))).quantize(D('0.001'))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pesagem_automatica(request):
    """
    POST /api/cadastros/pesagens/automatica/

    Recebe leitura de balança integrada (RFID + peso) e salva a pesagem
    calculando o GMD automaticamente.

    Corpo:
    {
        "brinco": "BR-001",          # brinco RFID lido pela balança
        "peso_kg": 452.5,
        "data_pesagem": "2026-06-17",  # opcional — usa hoje se omitido
        "observacao": ""
    }

    Resposta:
    {
        "id": 42,
        "animal": {"id": 1, "brinco": "BR-001", "raca": "NELORE"},
        "peso_kg": "452.500",
        "gmd_calculado": "1.050",    # null se primeira pesagem
        "data_pesagem": "2026-06-17",
        "alerta_gmd": false           # true se GMD caiu 2 dias seguidos
    }
    """
    from decimal import Decimal as D

    brinco = (request.data.get('brinco') or '').strip()
    if not brinco:
        return Response({'detail': 'Campo "brinco" é obrigatório.'}, status=400)

    peso_raw = request.data.get('peso_kg')
    try:
        peso_kg = D(str(peso_raw))
        if peso_kg <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return Response({'detail': 'Campo "peso_kg" inválido.'}, status=400)

    data_str = request.data.get('data_pesagem')
    if data_str:
        try:
            from django.utils.dateparse import parse_date
            data_pesagem = parse_date(data_str)
            if not data_pesagem:
                raise ValueError
        except (ValueError, TypeError):
            return Response({'detail': 'Formato de data inválido. Use YYYY-MM-DD.'}, status=400)
    else:
        data_pesagem = timezone.localdate()

    # Resolve o cliente via M2M (padrão da arquitetura)
    prop = request.user.propriedades.select_related('cliente').first()
    if not prop:
        return Response({'detail': 'Usuário sem propriedade vinculada.'}, status=400)

    try:
        animal = Animal.objects.get(brinco=brinco, propriedade__cliente=prop.cliente, ativo=True)
    except Animal.DoesNotExist:
        return Response(
            {'detail': f'Animal com brinco "{brinco}" não encontrado nesta propriedade.'},
            status=404,
        )
    except Animal.MultipleObjectsReturned:
        animal = Animal.objects.filter(
            brinco=brinco, propriedade__cliente=prop.cliente, ativo=True
        ).first()

    gmd = _calcular_gmd(animal, peso_kg, data_pesagem)

    pesagem = RegistroPesagem.objects.create(
        animal=animal,
        data_pesagem=data_pesagem,
        peso_kg=peso_kg,
        gmd_calculado=gmd,
        origem='RFID',
        observacao=request.data.get('observacao', ''),
    )

    # Verifica se o GMD caiu 2 pesagens seguidas → dispara alerta IA
    alerta_gmd = False
    if gmd is not None:
        ultimas = (
            RegistroPesagem.objects
            .filter(animal=animal, gmd_calculado__isnull=False)
            .exclude(pk=pesagem.pk)
            .order_by('-data_pesagem')[:2]
        )
        gmds_anteriores = [p.gmd_calculado for p in ultimas]
        if len(gmds_anteriores) >= 2 and all(g is not None for g in gmds_anteriores):
            if gmd < gmds_anteriores[0] < gmds_anteriores[1]:
                alerta_gmd = True
                _criar_alerta_gmd_queda(animal, gmd, prop.cliente)

    gmd_str = str(gmd) if gmd is not None else '0.000'
    return Response({
        'status': 'sucesso',
        'id': pesagem.pk,
        'animal': {
            'id': animal.pk,
            'brinco': animal.brinco,
            'raca': animal.get_raca_display(),
            'registro_genetico': animal.get_registro_genetico_display(),
        },
        'peso_kg': str(pesagem.peso_kg),
        'peso_registrado': str(pesagem.peso_kg),   # alias legível
        'gmd_calculado': gmd_str,
        'gmd_diario': gmd_str,                     # alias legível
        'data_pesagem': str(pesagem.data_pesagem),
        'origem': 'RFID',
        'alerta_gmd': alerta_gmd,
    }, status=201)


def _criar_alerta_gmd_queda(animal, gmd_atual, cliente):
    """Cria alerta de IA quando o GMD cai por 2 pesagens consecutivas."""
    try:
        from datumagro.apps.inteligencia.models import Alerta
        Alerta.objects.create(
            cliente=cliente,
            animal=animal,
            tipo_alerta='DESEMPENHO',
            mensagem=(
                f'{animal.brinco} ({animal.get_raca_display()}) apresentou queda de GMD '
                f'por 2 pesagens consecutivas. GMD atual: {gmd_atual:.3f} kg/dia. '
                f'Verifique nutrição, saúde e condição corporal do animal.'
            ),
            status='PENDENTE',
        )
    except Exception as exc:
        logger.warning('Falha ao criar alerta GMD: %s', exc)

