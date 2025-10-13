# datumagro/apps/relatorios/views.py

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Relatorio
from .serializers import RelatorioSerializer
from .tasks import gerar_pdf_lote_task
# CORREÇÃO: Importando Lote de 'operacional'
from datumagro.apps.operacional.models import Lote
from datumagro.apps.cadastros.models import Propriedade


class RelatorioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para o cliente visualizar seu histórico de relatórios
    e disparar a geração de novos.
    """
    serializer_class = RelatorioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Relatorio.objects.filter(cliente=self.request.user.perfilusuario.cliente)

    @action(detail=False, methods=['post'], url_path='gerar-pdf-lote')
    def gerar_pdf_lote(self, request):
        lote_id = request.data.get('lote_id')
        if not lote_id:
            return Response({'erro': 'lote_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        lote = get_object_or_404(Lote, id=lote_id, propriedade__cliente=request.user.perfilusuario.cliente)

        # Dispara a tarefa em segundo plano
        gerar_pdf_lote_task.delay(lote.id)

        return Response({'status': 'A geração do relatório foi iniciada. Consulte o histórico em breve.'},
                        status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        relatorio = self.get_object()
        if relatorio.arquivo and relatorio.status == 'CONCLUIDO':
            response = HttpResponse(relatorio.arquivo, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{relatorio.arquivo.name.split("/")[-1]}"'
            return response

        elif relatorio.status == 'GERANDO':
            return Response({'status': 'O relatório ainda está sendo gerado.'}, status=status.HTTP_202_ACCEPTED)

        raise Http404