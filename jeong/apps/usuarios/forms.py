from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario

class RegistroForm(UserCreationForm):
    email = forms.EmailField(label='E-mail', required=True)
    nome_completo = forms.CharField(label='Nome completo', max_length=150)

    class Meta:
        model = Usuario
        fields = ('nome_completo', 'email', 'password1', 'password2')

class LoginEmailForm(AuthenticationForm):
    username = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'autofocus': True}))