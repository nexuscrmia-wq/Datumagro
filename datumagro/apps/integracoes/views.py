# datumagro/apps/integracoes/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated  # Usaremos autenticação por Token
from .serializers import DadosRfidPesagemSerializer
from .services import processar_dados_rfid_pesagem


class RegistroAutomaticoView(APIView):
    """
    Endpoint principal para receber dados de hardware.
    Ex: POST /api/integracoes/registrar-pesagem/

    A autenticação será feita via API Token associado ao usuário/cliente.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Recebe e processa um registro de pesagem vindo de um leitor RFID + Balança.
        """
        serializer = DadosRfidPesagemSerializer(data=request.data)

        if serializer.is_valid():
            cliente = request.user.perfilusuario.cliente
            dados_validados = serializer.validated_data

            sucesso, mensagem = processar_dados_rfid_pesagem(cliente=cliente, dados=dados_validados)

            if sucesso:
                return Response({"status": "sucesso", "mensagem": mensagem}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": "erro", "mensagem": mensagem}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)