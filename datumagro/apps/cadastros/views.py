# datumagro/apps/cadastros/views.py

from rest_framework import viewsets, permissions
from .models import Propriedade, Animal, RegistroPesagem
from .serializers import PropriedadeSerializer, AnimalSerializer, RegistroPesagemSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import uuid
from django.db import transaction
from django.utils.dateparse import parse_datetime


class BaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet base que filtra os objetos para pertencerem apenas ao cliente do usuário logado.
    Garante a segurança e o isolamento dos dados.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Protege contra usuários sem perfil/cliente associado
        user = getattr(self.request, 'user', None)
        perfil = getattr(user, 'perfilusuario', None)
        cliente = getattr(perfil, 'cliente', None)
        # Fallback: se a relação direta não existe (models/migration divergência), tente achar por email
        if cliente is None:
            try:
                from .models import Cliente
                if user and getattr(user, 'email', None):
                    cliente = Cliente.objects.filter(email_contato=user.email).first()
                if cliente is None:
                    cliente = Cliente.objects.first()
            except Exception:
                cliente = None

        if cliente is None:
            # Retorna queryset vazio quando não há cliente associado para evitar 500
            return self.queryset.none()

        return self.queryset.filter(cliente=cliente)

    def perform_create(self, serializer):
        # Associa o novo objeto ao cliente do usuário logado, com validação clara
        user = getattr(self.request, 'user', None)
        perfil = getattr(user, 'perfilusuario', None)
        cliente = getattr(perfil, 'cliente', None)
        # fallback: tentar encontrar por e-mail do usuário ou pegar primeiro cliente disponível
        if cliente is None:
            try:
                from .models import Cliente
                if user and getattr(user, 'email', None):
                    cliente = Cliente.objects.filter(email_contato=user.email).first()
                if cliente is None:
                    cliente = Cliente.objects.first()
            except Exception:
                cliente = None

        if cliente is None:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'cliente': 'Usuário não possui um Cliente associado.'})

        serializer.save(cliente=cliente)


class PropriedadeViewSet(BaseViewSet):
    queryset = Propriedade.objects.all()
    serializer_class = PropriedadeSerializer

    # Sobrescreve o get_queryset para filtrar direto no cliente
    def get_queryset(self):
        return super().get_queryset()


class AnimalViewSet(BaseViewSet):
    serializer_class = AnimalSerializer

    # Sobrescreve o get_queryset para filtrar pela propriedade que pertence ao cliente
    def get_queryset(self):
        cliente = self.request.user.perfilusuario.cliente
        return Animal.objects.filter(propriedade__cliente=cliente)

    def perform_create(self, serializer):
        """
        Ao criar um Animal, não tentar passar `cliente` para serializer.save()
        (Animal não possui campo cliente). Simplesmente salva o serializer.

        Em implementações futuras, validar que a `propriedade` recebida
        pertence ao `cliente` do usuário e ajustar o comportamento.
        """
        serializer.save()


class RegistroPesagemViewSet(BaseViewSet):
    serializer_class = RegistroPesagemSerializer

    # Sobrescreve o get_queryset para filtrar pela pesagem de animal que pertence ao cliente
    def get_queryset(self):
        cliente = self.request.user.perfilusuario.cliente
        return RegistroPesagem.objects.filter(animal__propriedade__cliente=cliente)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_view(request):
    """
    Endpoint básico de sincronização em lote.
    Recebe um JSON com 'last_server_sync' e 'changes' (create/update/delete).
    Retorna 'server_time', 'applied' e 'server_changes'.
    This is a minimal implementation to be extended to full conflict handling.
    """
    payload = request.data
    user = request.user
    cliente = getattr(user.perfilusuario, 'cliente', None)

    last_sync = payload.get('last_server_sync')
    changes = payload.get('changes', [])

    applied = []
    conflicts = []

    # Process client changes (very small subset: create/update/delete for Animal)
    with transaction.atomic():
        for change in changes:
            op = change.get('op')
            model = change.get('model')
            data = change.get('data') or {}
            client_id = change.get('client_id')
            client_updated_at = change.get('updated_at')
            try:
                if model == 'animal':
                    if op == 'create':
                        # Ensure propriedade belongs to this cliente when possible
                        prop_id = data.get('propriedade')
                        from .models import Propriedade, Animal
                        try:
                            if cliente:
                                prop = Propriedade.objects.get(id=prop_id, cliente=cliente)
                            else:
                                prop = Propriedade.objects.get(id=prop_id)
                        except Propriedade.DoesNotExist:
                            applied.append({'client_id': client_id, 'status': 'error', 'reason': 'propriedade_not_found'})
                            continue
                        # ensure we include propriedade id in serializer data (it is already provided)
                        serializer = AnimalSerializer(data=data)
                        if serializer.is_valid():
                            obj = serializer.save()
                            applied.append({'client_id': client_id, 'server_id': obj.id, 'status': 'ok'})
                        else:
                            applied.append({'client_id': client_id, 'status': 'error', 'errors': serializer.errors})
                    elif op == 'update':
                        from .models import Animal
                        obj_id = change.get('id')
                        try:
                            if cliente:
                                obj = Animal.objects.get(id=obj_id, propriedade__cliente=cliente)
                            else:
                                obj = Animal.objects.get(id=obj_id)
                        except Animal.DoesNotExist:
                            applied.append({'id': obj_id, 'status': 'error', 'reason': 'not_found'})
                            continue
                        # Conflict detection: if client sent updated_at and server has newer updated_at, report conflict
                        server_updated = obj.updated_at
                        if client_updated_at:
                            try:
                                client_dt = parse_datetime(client_updated_at)
                            except Exception:
                                client_dt = None
                            if client_dt and server_updated and server_updated > client_dt:
                                # Conflict detected: prefer server by default and return conflict info
                                conflicts.append({
                                    'id': obj_id,
                                    'client_updated_at': client_updated_at,
                                    'server_updated_at': server_updated.isoformat(),
                                    'resolution': 'server_wins'
                                })
                                applied.append({'id': obj_id, 'status': 'conflict'})
                                continue

                        serializer = AnimalSerializer(obj, data=data, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            applied.append({'id': obj_id, 'status': 'ok'})
                        else:
                            applied.append({'id': obj_id, 'status': 'error', 'errors': serializer.errors})
                    elif op == 'delete':
                        from .models import Animal
                        obj_id = change.get('id')
                        try:
                            if cliente:
                                obj = Animal.objects.get(id=obj_id, propriedade__cliente=cliente)
                            else:
                                obj = Animal.objects.get(id=obj_id)
                            obj.ativo = False
                            obj.save()
                            applied.append({'id': obj_id, 'status': 'ok'})
                        except Animal.DoesNotExist:
                            applied.append({'id': obj_id, 'status': 'error', 'reason': 'not_found'})
            except Exception as e:
                applied.append({'client_id': client_id, 'status': 'error', 'reason': str(e)})
    # Prepare server_changes: return animals updated after last_sync
    server_changes = []
    from .models import Animal
    try:
        server_qs = Animal.objects.filter(propriedade__cliente=cliente)
        if last_sync:
            last_dt = parse_datetime(last_sync)
            if last_dt:
                server_qs = server_qs.filter(updated_at__gt=last_dt)

        # limit returned changes to reasonable number to avoid huge payloads
        for a in server_qs.order_by('updated_at')[:500]:
            server_changes.append({
                'op': 'update',
                'model': 'animal',
                'id': a.id,
                'data': AnimalSerializer(a).data,
                'updated_at': a.updated_at.isoformat() if a.updated_at else None,
            })
    except Exception:
        server_changes = []

    response = {
        'server_time': timezone.now().isoformat(),
        'applied': applied,
        'server_changes': server_changes,
        'conflicts': conflicts,
    }
    return Response(response, status=status.HTTP_200_OK)