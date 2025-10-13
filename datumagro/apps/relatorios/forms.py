# datumagro/apps/relatorios/forms.py

from django import forms
# CORREÇÃO: Importando Lote de 'operacional'
from datumagro.apps.operacional.models import Lote
from datumagro.apps.cadastros.models import Propriedade

class GerarRelatorioLoteForm(forms.Form):
    """
    Um formulário simples que funciona como um seletor, para permitir ao usuário
    escolher um lote para o qual gerar um relatório.
    """
    lote = forms.ModelChoiceField(
        queryset=Lote.objects.none(), # O queryset será filtrado na view
        label="Selecione o Lote",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)
        if cliente:
            # Filtra o campo 'lote' para mostrar apenas os lotes
            # das propriedades do cliente logado.
            self.fields['lote'].queryset = Lote.objects.filter(propriedade__cliente=cliente)

class GerarRelatorioPropriedadeForm(forms.Form):
    """
    Um formulário simples para selecionar uma propriedade.
    """
    propriedade = forms.ModelChoiceField(
        queryset=Propriedade.objects.none(),
        label="Selecione a Propriedade",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)
        if cliente:
            self.fields['propriedade'].queryset = Propriedade.objects.filter(cliente=cliente)