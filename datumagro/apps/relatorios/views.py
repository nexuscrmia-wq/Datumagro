from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Relatorio
from .serializers import RelatorioSerializer


def _get_cliente(user):
    from datumagro.apps.cadastros.models import Cliente
    perfil = getattr(user, 'perfilusuario', None)
    cliente = getattr(perfil, 'cliente', None) if perfil else None
    if not cliente:
        cliente = Cliente.objects.filter(email_contato=user.email).first()
    return cliente


class RelatorioViewSet(viewsets.ModelViewSet):
    """Histórico de relatórios gerados pelo cliente."""
    serializer_class = RelatorioSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        cliente = _get_cliente(self.request.user)
        if not cliente:
            return Relatorio.objects.none()
        return Relatorio.objects.filter(cliente=cliente)

    @action(detail=False, methods=['post'], url_path='gerar')
    def gerar(self, request):
        """
        Cria um registro de relatório e tenta gerá-lo.
        Aceita: { tipo: 'DESEMPENHO'|'FINANCEIRO'|'SANITARIO'|'REPRODUTIVO'|'PRODUCAO',
                  parametros: {...} }
        """
        cliente = _get_cliente(request.user)
        if not cliente:
            return Response(
                {'detail': 'Cliente não encontrado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tipo = request.data.get('tipo', 'DESEMPENHO').upper()
        valid_tipos = [c[0] for c in Relatorio.TIPO_CHOICES]
        if tipo not in valid_tipos:
            tipo = 'DESEMPENHO'

        relatorio = Relatorio.objects.create(
            cliente=cliente,
            tipo_relatorio=tipo,
            status='CONCLUIDO',  # MVP: sem geração assíncrona por enquanto
            parametros=request.data.get('parametros'),
        )

        # Tenta disparar geração async via Celery se disponível
        try:
            from .tasks import gerar_relatorio_task
            gerar_relatorio_task.delay(relatorio.id)
            relatorio.status = 'GERANDO'
            relatorio.save(update_fields=['status'])
        except Exception:
            # Celery não configurado — mantém CONCLUIDO como placeholder
            pass

        serializer = self.get_serializer(relatorio)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        relatorio = self.get_object()
        if relatorio.arquivo and relatorio.status == 'CONCLUIDO':
            response = HttpResponse(
                relatorio.arquivo,
                content_type='application/octet-stream',
            )
            nome_arquivo = relatorio.arquivo.name.split('/')[-1]
            response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
            return response
        if relatorio.status == 'GERANDO':
            return Response(
                {'status': 'Relatório ainda sendo gerado.'},
                status=status.HTTP_202_ACCEPTED,
            )
        raise Http404
