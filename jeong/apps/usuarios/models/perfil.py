from django.conf import settings
from django.db import models

def avatar_upload_path(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'

class PerfilUsuario(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfilusuario'
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        default='img/default_avatar.png'
    )
    pontos = models.PositiveIntegerField(default=0)
    partidas_jogadas = models.PositiveIntegerField(default=0)
    vitorias = models.PositiveIntegerField(default=0)
    tema = models.CharField(max_length=10, choices=[('light', 'Claro'), ('dark', 'Escuro')], default='light')
    # Adicione outros campos conforme a gamificação: conquistas, temas, etc.

    def __str__(self):
        return f'Perfil de {self.user.email}'

    @property
    def nome_completo(self):
        return self.user.nome_completo if hasattr(self.user, 'nome_completo') else self.user.get_full_name()

    @property
    def email(self):
        return self.user.email
