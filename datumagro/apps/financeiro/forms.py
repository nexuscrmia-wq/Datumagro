# datumagro/apps/financeiro/forms.py

from django import forms
from .models import Transacao, Categoria


class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['descricao', 'valor', 'data', 'categoria', 'animal', 'observacao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Sobrescrevemos o inicializador do formulário para um propósito muito importante:
        filtrar o campo 'categoria' para mostrar apenas as categorias
        que pertencem ao cliente do usuário que está preenchendo o formulário.
        Isso impede que um cliente veja as categorias de outro.
        """
        # Extrai o 'cliente' que passaremos da view para o formulário
        cliente = kwargs.pop('cliente', None)

        super().__init__(*args, **kwargs)

        if cliente:
            # Filtra os querysets dos campos de chave estrangeira
            self.fields['categoria'].queryset = Categoria.objects.filter(cliente=cliente)
            # Opcional: filtrar animais também
            self.fields[
                'animal'].queryset = cliente.propriedades.first().animais.all() if cliente.propriedades.exists() else \
            self.fields['animal'].queryset.none()

        # Adiciona classes CSS para estilização (Bootstrap, por exemplo)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'