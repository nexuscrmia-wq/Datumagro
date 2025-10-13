# datumagro/apps/cadastros/services.py

from datetime import date
from decimal import Decimal
from .models import Animal, RegistroPesagem


# A importação da 'inteligencia' foi REMOVIDA DAQUI de cima para quebrar o ciclo

def registrar_pesagem(animal: Animal, data_pesagem: date, peso_kg: Decimal, observacao: str = "") -> RegistroPesagem:
    """
    Serviço para criar um novo registro de pesagem para um animal.
    Após criar o registro, dispara a tarefa assíncrona da IA para analisar o desempenho.
    """
    # A importação agora é feita AQUI DENTRO, resolvendo o problema do circular import.
    from datumagro.apps.inteligencia.tasks import analisar_desempenho_task

    registro = RegistroPesagem.objects.create(
        animal=animal,
        data_pesagem=data_pesagem,
        peso_kg=peso_kg,
        observacao=observacao
    )

    # Dispara a análise da IA em segundo plano, sem travar o sistema.
    analisar_desempenho_task.delay(animal.id)

    return registro


def calcular_idade_em_meses(data_nascimento: date) -> int:
    """Calcula a idade de um animal em meses."""
    hoje = date.today()
    idade_meses = (hoje.year - data_nascimento.year) * 12 + hoje.month - data_nascimento.month
    return idade_meses


def calcular_gmd(animal: Animal) -> Decimal:
    """
    Calcula o Ganho de Peso Médio Diário (GMD) do animal.
    """
    pesagens = animal.pesagens.order_by('data_pesagem')
    if pesagens.count() < 2:
        return Decimal('0.0')

    primeira_pesagem = pesagens.first()
    ultima_pesagem = pesagens.last()

    diferenca_dias = (ultima_pesagem.data_pesagem - primeira_pesagem.data_pesagem).days
    diferenca_peso = ultima_pesagem.peso_kg - primeira_pesagem.peso_kg

    if diferenca_dias <= 0:
        return Decimal('0.0')

    gmd = diferenca_peso / Decimal(diferenca_dias)
    return round(gmd, 3)