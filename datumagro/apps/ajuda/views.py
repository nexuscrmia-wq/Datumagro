from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GuiaModulo
from .serializers import GuiaModuloSerializer


def _especie_do_usuario(user):
    """Resolve a espécie do cliente vinculado ao usuário usando a mesma
    lógica de 3 níveis do _resolver_cliente (email → M2M → PerfilUsuario)."""
    from datumagro.apps.cadastros.models import Cliente

    cliente = Cliente.objects.filter(email_contato=user.email).first()
    if not cliente:
        prop = user.propriedades.select_related("cliente").first()
        if prop:
            cliente = prop.cliente
    if not cliente:
        perfil = getattr(user, "perfilusuario", None)
        cliente = getattr(perfil, "cliente", None) if perfil else None

    if cliente and cliente.tipo_especie:
        # tipo_especie no Cliente usa os mesmos valores que GuiaModulo.Especie
        return cliente.tipo_especie

    return GuiaModulo.Especie.GLOBAL


class GuiaModuloDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, modulo_slug):
        especie = _especie_do_usuario(request.user)

        guia = (
            GuiaModulo.objects.filter(
                modulo_slug=modulo_slug, especie=especie, ativo=True
            ).first()
            or GuiaModulo.objects.filter(
                modulo_slug=modulo_slug,
                especie=GuiaModulo.Especie.GLOBAL,
                ativo=True,
            ).first()
        )

        if not guia:
            return Response(
                {"detail": "Nenhum guia cadastrado para este módulo ainda."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(GuiaModuloSerializer(guia).data)
