# datumagro/apps/rastreabilidade/views.py

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PerfilPublicoAnimal
from .serializers import PerfilPublicoManagementSerializer, DadosRastreabilidadeSerializer
from .services import gerar_qr_code_para_perfil
from datumagro.apps.usuarios.permissions import IsProprietarioOrGerente

# --- View para a API (Gerenciamento do Produtor) ---
class PerfilPublicoAPIViewSet(viewsets.ModelViewSet):
    """
    Gerenciamento dos perfis de rastreabilidade (QR Code / passaporte).
    Restrito a Proprietário e Gerente — peão não emite documentos sanitários.
    """
    serializer_class = PerfilPublicoManagementSerializer
    permission_classes = [permissions.IsAuthenticated, IsProprietarioOrGerente]

    def get_queryset(self):
        from datumagro.apps.cadastros.models import Cliente
        user = self.request.user
        perfil = getattr(user, 'perfilusuario', None)
        cliente = getattr(perfil, 'cliente', None) if perfil else None
        if not cliente:
            cliente = Cliente.objects.filter(email_contato=user.email).first()
        if not cliente:
            return PerfilPublicoAnimal.objects.none()
        return PerfilPublicoAnimal.objects.filter(animal__propriedade__cliente=cliente)

    @action(detail=True, methods=['post'])
    def gerar_qrcode(self, request, pk=None):
        """
        Ação para gerar (ou regenerar) a imagem do QR Code para um perfil.
        URL: /api/rastreabilidade/gerenciar-perfis/{id}/gerar_qrcode/
        """
        perfil = self.get_object()
        qr_code_file = gerar_qr_code_para_perfil(perfil)
        return Response({'status': 'QR Code gerado com sucesso', 'qr_code_url': request.build_absolute_uri(qr_code_file.url)})

# --- View para a Página Pública (Visão do Consumidor) ---
class PublicPerfilDetailView(DetailView):
    """
    View que renderiza a página HTML pública do animal.
    Esta view não requer autenticação.
    """
    model = PerfilPublicoAnimal
    template_name = 'rastreabilidade/perfil_publico.html' # Precisaremos criar este template
    context_object_name = 'perfil'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # Mostra apenas perfis que estão marcados como públicos
        return PerfilPublicoAnimal.objects.filter(is_publico=True)