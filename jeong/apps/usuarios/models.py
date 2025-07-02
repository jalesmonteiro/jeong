from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    username = None  # Remove o campo username padrão
    email = models.EmailField('e-mail', unique=True)
    nome_completo = models.CharField('Nome completo', max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome_completo']

    def __str__(self):
        return self.email
