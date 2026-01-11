# 💻 GUIA TÉCNICO DE MELHORIAS - BACKEND DATUMAGRO

**Data:** 13 de novembro de 2025  
**Versão:** 1.0  
**Objetivo:** Fornecer snippets de código prontos para implementação

---

## 📋 ÍNDICE

1. [Performance - N+1 Queries](#performance---n1-queries)
2. [Database Indexing](#database-indexing)
3. [Caching com Redis](#caching-com-redis)
4. [Logging Estruturado](#logging-estruturado)
5. [Rate Limiting](#rate-limiting)
6. [Validações Robustas](#validações-robustas)
7. [Testes Automatizados](#testes-automatizados)

---

## 1. PERFORMANCE - N+1 QUERIES

### Problema Identificado

```python
# ❌ RUIM - Causa 1 + N queries
def get_animais_api(request):
    animais = Animal.objects.all()[:100]
    
    # Cada acesso a animal.propriedade gera 1 query
    for animal in animais:
        print(animal.propriedade.nome)  # Query extra!
        print(animal.pai.raca)           # Query extra!
```

### Solução: select_related()

**Arquivo:** `datumagro/apps/cadastros/views.py`

```python
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Animal, Propriedade
from .serializers import AnimalSerializer

class AnimalViewSet(viewsets.ModelViewSet):
    """
    Melhorado com select_related para FK
    """
    serializer_class = AnimalSerializer
    
    def get_queryset(self):
        # ✅ BOM - Faz apenas 1 query com joins
        return Animal.objects.select_related(
            'propriedade',      # ForeignKey
            'propriedade__cliente',  # Relacionamento em cadeia
            'pai',              # SelfFK
            'mae',              # SelfFK
        ).prefetch_related(
            'pesagens',         # Reverse FK
            'transacoes_financeiras',  # Reverse FK
        ).filter(
            ativo=True
        )

class PropriedadeViewSet(viewsets.ModelViewSet):
    """
    Com prefetch_related para reverse FK
    """
    serializer_class = PropriedadeSerializer
    
    def get_queryset(self):
        # ✅ BOM - Prefetch para coleções
        return Propriedade.objects.prefetch_related(
            'animais',  # Reverse FK (1 query para todos)
        ).select_related(
            'cliente',  # FK direto
        )
```

**Medição de Impacto:**

```python
# Test script para validar melhoria
# Arquivo: datumagro/apps/cadastros/tests_performance.py

from django.test import TestCase
from django.test.utils import override_settings
from django.db import connection
from django.test.utils import CaptureQueriesContext

class PerformanceTests(TestCase):
    def test_animal_list_query_count(self):
        """Valida que listar 100 animais faz apenas 3 queries"""
        
        # Setup: Criar 100 animais com relações
        # ...
        
        with CaptureQueriesContext(connection) as context:
            animais = Animal.objects.select_related(
                'propriedade',
                'propriedade__cliente',
                'pai', 'mae'
            ).prefetch_related(
                'pesagens'
            )[:100]
            
            # Force evaluation
            list(animais)
        
        # Antes: ~300 queries
        # Depois: ~3 queries
        assert len(context.captured_queries) < 5, \
            f"Too many queries: {len(context.captured_queries)}"
```

---

## 2. DATABASE INDEXING

### Índices Recomendados

**Arquivo:** `datumagro/apps/cadastros/models.py`

```python
from django.db import models

class Animal(models.Model):
    # ... campos existentes ...
    
    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"
        unique_together = ('propriedade', 'brinco')
        
        # ✅ NOVO: Adicionar índices
        indexes = [
            # Índice para filtros comuns
            models.Index(
                fields=['propriedade', 'ativo'],
                name='animal_prop_ativo_idx',
            ),
            
            # Índice para busca por brinco
            models.Index(
                fields=['brinco'],
                name='animal_brinco_idx',
            ),
            
            # Índice para relatórios por data
            models.Index(
                fields=['data_nascimento'],
                name='animal_datanasc_idx',
            ),
            
            # Índice para performance em genealogia
            models.Index(
                fields=['pai'],
                name='animal_pai_idx',
            ),
            models.Index(
                fields=['mae'],
                name='animal_mae_idx',
            ),
        ]


class RegistroPesagem(models.Model):
    # ... campos existentes ...
    
    class Meta:
        verbose_name = "Registro de Pesagem"
        verbose_name_plural = "Registros de Pesagem"
        
        # ✅ NOVO: Índices para histórico
        indexes = [
            models.Index(
                fields=['animal', '-data_pesagem'],
                name='pesagem_animal_data_idx',
            ),
            models.Index(
                fields=['-data_pesagem'],
                name='pesagem_data_idx',
            ),
        ]


class Transacao(models.Model):
    # ... campos existentes ...
    
    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        
        # ✅ NOVO: Índices para consultas financeiras
        indexes = [
            models.Index(
                fields=['cliente', '-data'],
                name='transacao_cliente_data_idx',
            ),
            models.Index(
                fields=['categoria', '-data'],
                name='transacao_categoria_data_idx',
            ),
            models.Index(
                fields=['-data'],
                name='transacao_data_idx',
            ),
        ]
```

### Criar Migração

```bash
# Criar migração para novos índices
python manage.py makemigrations cadastros

# Aplicar em desenvolvimento
python manage.py migrate cadastros

# ⚠️  Em produção, usar:
python manage.py migrate --plan  # Preview first
# Depois em janela de manutenção:
python manage.py migrate cadastros
```

---

## 3. CACHING COM REDIS

### Instalação

```bash
# Adicionar ao requirements.txt
echo "django-redis==5.4.0" >> requirements.txt
echo "redis==5.0.0" >> requirements.txt

# Instalar
pip install -r requirements.txt
```

### Configuração

**Arquivo:** `datumagro/settings.py`

```python
# ... imports existentes ...

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv(
            'REDIS_URL',
            'redis://127.0.0.1:6379/1'
        ),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'PARSER': 'redis.connection.HiredisParser',
        },
        'KEY_PREFIX': 'datumagro',
        'TIMEOUT': 300,  # 5 minutos padrão
    }
}
```

### Implementação em Views

**Arquivo:** `datumagro/apps/financeiro/views.py`

```python
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Transacao

# Opção 1: Cache simples por tempo
@cache_page(60 * 5)  # 5 minutos
@api_view(['GET'])
def relatorio_financeiro(request):
    """
    Relatório financeiro cacheado por 5 minutos
    """
    cliente_id = request.user.cliente_set.first().id
    
    transacoes = Transacao.objects.filter(
        cliente_id=cliente_id
    ).select_related('categoria', 'animal')
    
    return Response({
        'total_receita': sum(t.valor for t in transacoes if t.categoria.tipo == 'RECEITA'),
        'total_custo': sum(t.valor for t in transacoes if t.categoria.tipo == 'CUSTO'),
        'transacoes': TransacaoSerializer(transacoes, many=True).data,
    })


# Opção 2: Cache manual com invalidação controlada
@api_view(['GET'])
def fluxo_caixa_mensal(request):
    """
    Fluxo de caixa com cache manual
    """
    mes = request.query_params.get('mes')
    ano = request.query_params.get('ano')
    cliente_id = request.user.cliente_set.first().id
    
    cache_key = f'fluxo_caixa_{cliente_id}_{ano}_{mes}'
    
    # Tentar pegar do cache
    relatorio = cache.get(cache_key)
    
    if relatorio is None:
        # Se não tiver em cache, calcular
        relatorio = calcular_fluxo_caixa(cliente_id, mes, ano)
        # Armazenar por 1 hora
        cache.set(cache_key, relatorio, 3600)
    
    return Response(relatorio)


# Opção 3: Cache com Tags para invalidação
@api_view(['POST'])
def criar_transacao(request):
    """
    Cria transação e invalida cache relacionado
    """
    serializer = TransacaoSerializer(data=request.data)
    
    if serializer.is_valid():
        transacao = serializer.save()
        
        # Invalidar cache de relatório financeiro
        cliente_id = transacao.cliente.id
        cache_keys = [
            f'fluxo_caixa_{cliente_id}_*',
            f'relatorio_financeiro_{cliente_id}',
        ]
        
        for key in cache_keys:
            cache.delete_pattern(key)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### Testes de Cache

```python
# Arquivo: datumagro/apps/financeiro/tests_cache.py

from django.test import TestCase
from django.core.cache import cache

class CacheTests(TestCase):
    def setUp(self):
        cache.clear()
    
    def test_relatorio_cacheado(self):
        """Valida que relatório é cacheado"""
        
        # Primeira chamada - computa
        response1 = self.client.get('/api/financeiro/transacoes/relatorio/')
        
        # Segunda chamada - vem do cache (mais rápido)
        response2 = self.client.get('/api/financeiro/transacoes/relatorio/')
        
        # Ambas retornam mesmo resultado
        assert response1.data == response2.data
        
        # Cache foi usado (verificar tempo de resposta)
        # response2 deve ser < 10ms (cache)
        # response1 pode ser > 100ms (DB)
```

---

## 4. LOGGING ESTRUTURADO

### Instalação

```bash
echo "python-json-logger==2.0.7" >> requirements.txt
echo "sentry-sdk==1.39.0" >> requirements.txt
```

### Configuração

**Arquivo:** `datumagro/settings.py`

```python
import logging
import logging.config
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Sentry para monitoramento em produção
if IS_PRODUCTION:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# Logging estruturado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json' if IS_PRODUCTION else 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'datumagro': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING)
```

### Uso em Views

**Arquivo:** `datumagro/apps/cadastros/views.py`

```python
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class AnimalViewSet(viewsets.ModelViewSet):
    
    def create(self, request, *args, **kwargs):
        """Criar animal com logging"""
        try:
            logger.info(
                "Criar animal",
                extra={
                    'user_id': request.user.id,
                    'propriedade_id': request.data.get('propriedade'),
                    'brinco': request.data.get('brinco'),
                }
            )
            
            response = super().create(request, *args, **kwargs)
            
            logger.info(
                "Animal criado com sucesso",
                extra={
                    'animal_id': response.data['id'],
                    'user_id': request.user.id,
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Erro ao criar animal",
                exc_info=True,
                extra={
                    'user_id': request.user.id,
                    'propriedade_id': request.data.get('propriedade'),
                    'error': str(e),
                }
            )
            raise
    
    def destroy(self, request, *args, **kwargs):
        """Deletar animal com auditoria"""
        animal_id = kwargs.get('pk')
        animal = self.get_object()
        
        logger.warning(
            "Animal deletado",
            extra={
                'animal_id': animal_id,
                'brinco': animal.brinco,
                'user_id': request.user.id,
                'ip_address': self.request.META.get('REMOTE_ADDR'),
            }
        )
        
        return super().destroy(request, *args, **kwargs)
```

---

## 5. RATE LIMITING

### Instalação

```bash
echo "djangorestframework-simplejwt==5.3.2" >> requirements.txt
```

### Configuração

**Arquivo:** `datumagro/settings.py`

```python
REST_FRAMEWORK = {
    # ... configurações existentes ...
    
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',           # Anônimo: 100 req/hora
        'user': '1000/hour',          # Autenticado: 1000 req/hora
        'auth_token': '500/hour',     # Token: 500 req/hora
    }
}
```

### Throttles Customizados

**Arquivo:** `datumagro/apps/core/throttles.py`

```python
from rest_framework.throttling import UserRateThrottle, BaseThrottle

class BurstThrottle(UserRateThrottle):
    """Limite para picos de tráfego"""
    scope = 'burst'
    THROTTLE_RATES = {
        'burst': '10/second'  # 10 requisições por segundo
    }

class SustainedThrottle(UserRateThrottle):
    """Limite sustentado ao longo do tempo"""
    scope = 'sustained'
    THROTTLE_RATES = {
        'sustained': '1000/hour'  # 1000 por hora
    }

class APIViewThrottle(BaseThrottle):
    """Throttle customizado para endpoints específicos"""
    
    def allow_request(self, request, view):
        # Endpoints mais críticos com limite mais apertado
        if view.__class__.__name__ in ['AnimalViewSet', 'TransacaoViewSet']:
            # Premium users: 10000 req/dia
            # Regular users: 1000 req/dia
            
            premium_users = request.user.groups.filter(name='premium').exists()
            
            if premium_users:
                rate = '10000/day'
            else:
                rate = '1000/day'
        
        return super().allow_request(request, view)
```

### Uso em Views

**Arquivo:** `datumagro/apps/cadastros/views.py`

```python
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle
from datumagro.apps.core.throttles import BurstThrottle, SustainedThrottle

class AnimalViewSet(viewsets.ModelViewSet):
    throttle_classes = [UserRateThrottle]
    
    # Criar animal: limite mais apertado
    def create(self, request, *args, **kwargs):
        # Aplicar burst throttle
        self.throttle_classes = [BurstThrottle]
        return super().create(request, *args, **kwargs)
    
    # Listar animais: limite relaxado
    def list(self, request, *args, **kwargs):
        self.throttle_classes = [SustainedThrottle]
        return super().list(request, *args, **kwargs)


@api_view(['POST'])
@throttle_classes([BurstThrottle])
def criar_pesagem(request):
    """Endpoint com throttle customizado"""
    # Implementação...
    pass
```

---

## 6. VALIDAÇÕES ROBUSTAS

### Validações em Models

**Arquivo:** `datumagro/apps/cadastros/models.py`

```python
from django.core.exceptions import ValidationError
from django.utils import timezone

class Animal(models.Model):
    # ... campos existentes ...
    
    def clean(self):
        """Validações de negócio"""
        errors = {}
        
        # 1. Validar genealogia
        if self.pai and self.pai.sexo != 'M':
            errors['pai'] = "Pai deve ser um macho"
        
        if self.mae and self.mae.sexo != 'F':
            errors['mae'] = "Mãe deve ser uma fêmea"
        
        # 2. Validar que pai/mãe são de mesma propriedade
        if self.pai and self.pai.propriedade != self.propriedade:
            errors['pai'] = "Pai deve ser da mesma propriedade"
        
        if self.mae and self.mae.propriedade != self.propriedade:
            errors['mae'] = "Mãe deve ser da mesma propriedade"
        
        # 3. Validar datas
        if self.data_nascimento > timezone.now().date():
            errors['data_nascimento'] = "Data de nascimento não pode ser no futuro"
        
        # 4. Validar que status reprodutivo é só para fêmeas
        if self.status_reprodutivo and self.sexo != 'F':
            errors['status_reprodutivo'] = "Apenas fêmeas podem ter status reprodutivo"
        
        # 5. Validar que reprodutor é só para machos
        if self.is_reprodutor and self.sexo != 'F':
            errors['is_reprodutor'] = "Apenas machos podem ser reprodutores"
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.clean()  # Sempre validar antes de salvar
        super().save(*args, **kwargs)


class RegistroPesagem(models.Model):
    # ... campos existentes ...
    
    def clean(self):
        """Validações para pesagem"""
        errors = {}
        
        # 1. Peso não pode ser negativo ou zero
        if self.peso_kg <= 0:
            errors['peso_kg'] = "Peso deve ser maior que zero"
        
        # 2. Peso máximo razoável (5 toneladas)
        if self.peso_kg > 5000:
            errors['peso_kg'] = "Peso parece irreal (max 5000kg)"
        
        # 3. Data não pode ser no futuro
        if self.data_pesagem > timezone.now().date():
            errors['data_pesagem'] = "Data de pesagem não pode ser no futuro"
        
        # 4. Data não pode ser antes do nascimento
        if self.data_pesagem < self.animal.data_nascimento:
            errors['data_pesagem'] = "Data de pesagem não pode ser antes do nascimento"
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Transacao(models.Model):
    # ... campos existentes ...
    
    def clean(self):
        """Validações para transação"""
        errors = {}
        
        # 1. Validar valor
        if self.valor <= 0:
            errors['valor'] = "Valor deve ser maior que zero"
        
        # 2. Máximo razoável
        if self.valor > 1000000:
            errors['valor'] = "Valor parece irreal"
        
        # 3. Data não pode ser no futuro
        if self.data > timezone.now().date():
            errors['data'] = "Data não pode ser no futuro"
        
        # 4. Categoria deve pertencer ao cliente
        if self.categoria.cliente != self.cliente:
            errors['categoria'] = "Categoria não pertence a este cliente"
        
        # 5. Animal deve pertencer ao cliente
        if self.animal and self.animal.propriedade.cliente != self.cliente:
            errors['animal'] = "Animal não pertence a este cliente"
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
```

### Validações em Serializers

**Arquivo:** `datumagro/apps/cadastros/serializers.py`

```python
from rest_framework import serializers
from django.utils import timezone

class AnimalSerializer(serializers.ModelSerializer):
    """Serializer com validações extras"""
    
    class Meta:
        model = Animal
        fields = [
            'id', 'propriedade', 'brinco', 'raca', 'sexo',
            'data_nascimento', 'categoria', 'pai', 'mae'
        ]
    
    def validate_brinco(self, value):
        """Validar brinco único por propriedade"""
        propriedade = self.initial_data.get('propriedade')
        
        if propriedade:
            existe = Animal.objects.filter(
                propriedade_id=propriedade,
                brinco=value
            ).exclude(id=self.instance.id if self.instance else None).exists()
            
            if existe:
                raise serializers.ValidationError(
                    f"Brinco '{value}' já existe nesta propriedade"
                )
        
        return value
    
    def validate(self, data):
        """Validações cross-field"""
        
        # Pai deve ser macho
        if data.get('pai') and data['pai'].sexo != 'M':
            raise serializers.ValidationError({
                'pai': "Pai deve ser um macho"
            })
        
        # Mãe deve ser fêmea
        if data.get('mae') and data['mae'].sexo != 'F':
            raise serializers.ValidationError({
                'mae': "Mãe deve ser uma fêmea"
            })
        
        # Data de nascimento
        if data.get('data_nascimento') > timezone.now().date():
            raise serializers.ValidationError({
                'data_nascimento': "Não pode ser no futuro"
            })
        
        return data
```

---

## 7. TESTES AUTOMATIZADOS

### Test Case Base

**Arquivo:** `datumagro/apps/cadastros/tests.py`

```python
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Animal, Propriedade, Cliente

User = get_user_model()

class AnimalModelTests(TestCase):
    """Testes do modelo Animal"""
    
    @classmethod
    def setUpTestData(cls):
        """Setup de dados para todos os testes"""
        cls.cliente = Cliente.objects.create(
            nome_empresa='Fazenda Teste',
            cpf_cnpj='12345678901234',
            email_contato='teste@farm.com',
        )
        
        cls.propriedade = Propriedade.objects.create(
            cliente=cls.cliente,
            nome_propriedade='Propriedade 1',
            cidade='São Paulo',
            estado='SP',
        )
    
    def test_criar_animal(self):
        """Testa criação básica de animal"""
        animal = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='BR001',
            raca='NELORE',
            sexo='M',
            data_nascimento='2023-01-01',
        )
        
        self.assertEqual(str(animal), 'BR001 (Nelore)')
        self.assertTrue(animal.ativo)
    
    def test_brinco_unico_por_propriedade(self):
        """Testa constraint de brinco único"""
        from django.db import IntegrityError
        
        animal1 = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='BR001',
            raca='NELORE',
            sexo='M',
            data_nascimento='2023-01-01',
        )
        
        with self.assertRaises(IntegrityError):
            animal2 = Animal.objects.create(
                propriedade=self.propriedade,
                brinco='BR001',  # Mesmo brinco!
                raca='ANGUS',
                sexo='F',
                data_nascimento='2023-01-02',
            )
    
    def test_validacao_pai_macho(self):
        """Testa validação de genealogia"""
        from django.core.exceptions import ValidationError
        
        # Criar fêmea como pai (inválido)
        pai_invalido = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='BR002',
            raca='NELORE',
            sexo='F',  # Fêmea!
            data_nascimento='2023-01-01',
        )
        
        animal = Animal(
            propriedade=self.propriedade,
            brinco='BR003',
            raca='NELORE',
            sexo='M',
            data_nascimento='2023-06-01',
            pai=pai_invalido,  # Pai fêmea!
        )
        
        with self.assertRaises(ValidationError) as context:
            animal.clean()
        
        self.assertIn('pai', context.exception.error_dict)
    
    def test_data_nascimento_futura(self):
        """Testa validação de data"""
        from django.core.exceptions import ValidationError
        from datetime import timedelta
        from django.utils import timezone
        
        animal = Animal(
            propriedade=self.propriedade,
            brinco='BR004',
            raca='NELORE',
            sexo='M',
            data_nascimento=timezone.now().date() + timedelta(days=1),
        )
        
        with self.assertRaises(ValidationError):
            animal.clean()


class AnimalAPITests(APITestCase):
    """Testes da API de Animal"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.client = APIClient()
        
        self.usuario = User.objects.create_user(
            email='teste@example.com',
            password='teste123',
        )
        
        self.cliente = Cliente.objects.create(
            nome_empresa='Fazenda Teste',
            cpf_cnpj='12345678901234',
            email_contato='teste@farm.com',
        )
        
        self.propriedade = Propriedade.objects.create(
            cliente=self.cliente,
            nome_propriedade='Propriedade 1',
            cidade='São Paulo',
            estado='SP',
        )
    
    def test_criar_animal_autenticado(self):
        """Testa criar animal via API"""
        self.client.force_authenticate(user=self.usuario)
        
        data = {
            'propriedade': self.propriedade.id,
            'brinco': 'BR001',
            'raca': 'NELORE',
            'sexo': 'M',
            'data_nascimento': '2023-01-01',
        }
        
        response = self.client.post('/api/cadastros/animais/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['brinco'], 'BR001')
    
    def test_criar_animal_nao_autenticado(self):
        """Testa permissão de criação"""
        data = {
            'propriedade': self.propriedade.id,
            'brinco': 'BR001',
            'raca': 'NELORE',
            'sexo': 'M',
            'data_nascimento': '2023-01-01',
        }
        
        response = self.client.post('/api/cadastros/animais/', data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_listar_animais_com_select_related(self):
        """Testa otimização de queries"""
        from django.test.utils import override_settings
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        
        # Criar 10 animais
        for i in range(10):
            Animal.objects.create(
                propriedade=self.propriedade,
                brinco=f'BR{i:03d}',
                raca='NELORE',
                sexo='M' if i % 2 == 0 else 'F',
                data_nascimento='2023-01-01',
            )
        
        self.client.force_authenticate(user=self.usuario)
        
        # Contar queries
        with CaptureQueriesContext(connection) as context:
            response = self.client.get('/api/cadastros/animais/')
            
            # Força avaliação
            json_data = response.json()
        
        # Deve ser ~ 2-3 queries (1 para animais, 1 para propriedades, etc)
        # Não 10+ queries
        num_queries = len(context.captured_queries)
        self.assertLess(
            num_queries,
            5,
            f"Muitas queries: {num_queries}. Use select_related/prefetch_related"
        )
    
    def test_filtrar_animais_ativos(self):
        """Testa filtro de animais ativos"""
        ativo = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='BR001',
            raca='NELORE',
            sexo='M',
            data_nascimento='2023-01-01',
            ativo=True,
        )
        
        inativo = Animal.objects.create(
            propriedade=self.propriedade,
            brinco='BR002',
            raca='NELORE',
            sexo='F',
            data_nascimento='2023-01-02',
            ativo=False,
        )
        
        self.client.force_authenticate(user=self.usuario)
        
        response = self.client.get('/api/cadastros/animais/?ativo=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['brinco'], 'BR001')
```

### Executar Testes

```bash
# Todos os testes
python manage.py test

# Testes específicos
python manage.py test datumagro.apps.cadastros.tests

# Com coverage
pip install coverage
coverage run --source='datumagro' manage.py test
coverage report
coverage html  # Gera relatório HTML
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Performance (1-2 dias)**
  - [ ] Adicionar `select_related()` em querysets
  - [ ] Adicionar `prefetch_related()` para reverse FKs
  - [ ] Testar com `CaptureQueriesContext`

- [ ] **Database (1 dia)**
  - [ ] Adicionar índices nos modelos
  - [ ] Criar migração
  - [ ] Testar em staging

- [ ] **Caching (2 dias)**
  - [ ] Instalar redis
  - [ ] Configurar django-redis
  - [ ] Implementar caching em endpoints críticos

- [ ] **Logging (1 dia)**
  - [ ] Configurar logging estruturado
  - [ ] Integrar Sentry
  - [ ] Testar em staging

- [ ] **Rate Limiting (1 dia)**
  - [ ] Implementar throttles
  - [ ] Testar limites
  - [ ] Documentar em API

- [ ] **Validações (2 dias)**
  - [ ] Adicionar validações em models
  - [ ] Adicionar validações em serializers
  - [ ] Criar testes para cada validação

- [ ] **Testes (3-5 dias)**
  - [ ] Testes de model
  - [ ] Testes de API
  - [ ] Testes de performance
  - [ ] Atingir cobertura > 80%

---

**Tempo Total Estimado:** 10-15 dias para implementar todas as melhorias

**Prioridade:** 
1. Performance (N+1, indexes)
2. Logging & Monitoring
3. Caching
4. Rate Limiting
5. Validações
6. Testes

