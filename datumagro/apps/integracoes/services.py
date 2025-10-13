# datumagro/apps/integracoes/services.py

from .models import LogIntegracao
from datumagro.apps.cadastros.models import Animal, Cliente
from datumagro.apps.cadastros.services import registrar_pesagem  # Reutilizando nosso serviço já criado!
from datetime import date


def processar_dados_rfid_pesagem(cliente: Cliente, dados: dict) -> tuple[bool, str]:
    """
    Processa os dados recebidos de uma integração de RFID + Balança.

    Retorna (True, 'mensagem de sucesso') ou (False, 'mensagem de erro').
    """

    # 1. Cria um log inicial
    log = LogIntegracao.objects.create(
        cliente=cliente,
        tipo_integracao='RFID_PESAGEM',
        dados_recebidos=dados
    )

    # 2. Extrai e valida os dados
    brinco = dados.get('brinco')
    peso_kg = dados.get('peso_kg')
    data_pesagem_str = dados.get('data_pesagem', date.today().isoformat())

    if not brinco or not peso_kg:
        log.status = 'ERRO'
        log.mensagem_retorno = "Erro: 'brinco' e 'peso_kg' são campos obrigatórios."
        log.save()
        return False, log.mensagem_retorno

    try:
        animal = Animal.objects.get(propriedade__cliente=cliente, brinco=brinco)
        data_pesagem = date.fromisoformat(data_pesagem_str)
    except Animal.DoesNotExist:
        log.status = 'ERRO'
        log.mensagem_retorno = f"Erro: Animal com brinco '{brinco}' não encontrado."
        log.save()
        return False, log.mensagem_retorno
    except (ValueError, TypeError):
        log.status = 'ERRO'
        log.mensagem_retorno = f"Erro: Formato de data inválido. Use AAAA-MM-DD."
        log.save()
        return False, log.mensagem_retorno

    # 3. Chama o serviço de cadastro de pesagem
    try:
        registro = registrar_pesagem(animal=animal, data_pesagem=data_pesagem, peso_kg=peso_kg)
        log.status = 'PROCESSADO'
        log.mensagem_retorno = f"Sucesso: Pesagem de {registro.peso_kg}kg registrada para o animal {animal.brinco}."
        log.save()
        return True, log.mensagem_retorno
    except Exception as e:
        log.status = 'ERRO'
        log.mensagem_retorno = f"Erro inesperado ao registrar pesagem: {str(e)}"
        log.save()
        return False, log.mensagem_retorno