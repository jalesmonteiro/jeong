from django.db import models
from .categoria import Categoria

class Palavra(models.Model):
    texto = models.CharField('Texto da palavra', max_length=100, unique=True)
    jamo = models.CharField('Sequência de letras (jamo)', max_length=200)
    idioma = models.CharField('Idioma', max_length=30, default='coreano')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='palavras'
    )

    class Meta:
        verbose_name = 'Palavra'
        verbose_name_plural = 'Palavras'
        ordering = ['texto']

    def __str__(self):
        return self.texto
