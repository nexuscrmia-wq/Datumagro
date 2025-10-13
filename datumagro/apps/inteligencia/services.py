# datumagro/apps/inteligencia/services.py

from datetime import date, timedelta
from .models import Alerta
from datumagro.apps.cadastros.models import Cliente, Animal, RegistroPesagem
from datumagro.apps.cadastros.services import calcular_idade_em_meses, calcular_gmd


def gerar_alerta_vacina_bezerro(cliente: Cliente):
    """
    IA Regra 1: Verifica todos os bezerros com idade entre 3 e 8 meses
    que ainda não tomaram a vacina contra Febre Aftosa e gera um alerta.
    """
    idade_min_meses = 3
    idade_max_meses = 8
    hoje = date.today()

    data_min = hoje - timedelta(days=idade_max_meses * 30)
    data_max = hoje - timedelta(days=idade_min_meses * 30)

    # Filtra animais na faixa de idade que pertencem ao cliente
    bezerros_alvo = Animal.objects.filter(
        propriedade__cliente=cliente,
        data_nascimento__range=(data_min, data_max),
        sexo='M',  # Apenas um exemplo
        ativo=True
    )

    alertas_criados = 0
    for bezerro in bezerros_alvo:
        # Lógica de verificação: Checar se já existe registro da vacina no histórico sanitário
        # (Vamos adicionar o histórico sanitário no app 'operacional')
        # Por enquanto, vamos simular que a vacina está faltando.

        # Verifica se já não existe um alerta PENDENTE igual para este animal
        alerta_existente = Alerta.objects.filter(
            cliente=cliente,
            animal=bezerro,
            tipo_alerta='SANITARIO',
            status='PENDENTE'
        ).exists()

        if not alerta_existente:
            idade = calcular_idade_em_meses(bezerro.data_nascimento)
            Alerta.objects.create(
                cliente=cliente,
                animal=bezerro,
                tipo_alerta='SANITARIO',
                mensagem=f"Alerta Sanitário: O bezerro {bezerro.brinco}, com {idade} meses, está na idade ideal para a vacinação contra Febre Aftosa."
            )
            alertas_criados += 1

    return alertas_criados


def analisar_desempenho_gmd(animal: Animal):
    """
    IA Regra 2: Após uma nova pesagem, calcula o GMD do animal
    e gera um alerta se estiver abaixo do esperado para a categoria.
    """
    gmd = calcular_gmd(animal)

    # Limiar simples de exemplo: 0.5 kg/dia
    limiar_gmd = 0.5

    if 0 < gmd < limiar_gmd:
        # Verifica se já existe um alerta de baixo GMD pendente para evitar duplicatas
        alerta_existente = Alerta.objects.filter(
            animal=animal,
            tipo_alerta='DESEMPENHO',
            status='PENDENTE'
        ).exists()

        if not alerta_existente:
            Alerta.objects.create(
                cliente=animal.propriedade.cliente,
                animal=animal,
                tipo_alerta='DESEMPENHO',
                mensagem=f"Alerta de Desempenho: O animal {animal.brinco} está com baixo Ganho de Peso Médio Diário ({gmd} kg/dia). Recomenda-se avaliar a nutrição e saúde."
            )
            return True
    return False