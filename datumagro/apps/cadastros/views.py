# datumagro/apps/cadastros/views.py

from rest_framework import viewsets, permissions
from .models import Propriedade, Animal, RegistroPesagem
from .serializers import PropriedadeSerializer, AnimalSerializer, RegistroPesagemSerializer


class BaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet base que filtra os objetos para pertencerem apenas ao cliente do usuário logado.
    Garante a segurança e o isolamento dos dados.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cliente = self.request.user.perfilusuario.cliente
        # Filtra o queryset original pelo cliente do usuário logado
        return self.queryset.filter(cliente=cliente)

    def perform_create(self, serializer):
        # Associa o novo objeto ao cliente do usuário logado
        serializer.save(cliente=self.request.user.perfilusuario.cliente)


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


class RegistroPesagemViewSet(BaseViewSet):
    serializer_class = RegistroPesagemSerializer

    # Sobrescreve o get_queryset para filtrar pela pesagem de animal que pertence ao cliente
    def get_queryset(self):
        cliente = self.request.user.perfilusuario.cliente
        return RegistroPesagem.objects.filter(animal__propriedade__cliente=cliente)