# datumagro/apps/operacional/forms.py

from django import forms
from .models import Lote, Piquete, ManejoSanitario, RegistroReprodutivo


class PiqueteForm(forms.ModelForm):
    class Meta:
        model = Piquete
        fields = ['nome', 'propriedade', 'tamanho_hectares', 'tipo_capim', 'status']

    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)
        if cliente:
            self.fields['propriedade'].queryset = cliente.propriedades.all()


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['nome', 'propriedade', 'animais']
        widgets = {
            'animais': forms.SelectMultiple(attrs={'class': 'select2'})
        }

    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)
        if cliente:
            self.fields['propriedade'].queryset = cliente.propriedades.all()
            self.fields['animais'].queryset = cliente.animais_cadastrados.all()  # Exemplo de queryset

# Outros forms (ManejoSanitarioForm, RegistroReprodutivoForm) podem ser criados seguindo o mesmo padrão.