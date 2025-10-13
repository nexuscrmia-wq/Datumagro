# datumagro/apps/usuarios/forms.py

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('email', 'nome_completo')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ('email', 'nome_completo')