from django.db import models
from django.conf import settings
from .palavra import Palavra

class Partida(models.Model):
    STATUS_CHOICES = [
        ('em_andamento', 'Em andamento'),
        ('vitoria', 'Vitória'),
        ('derrota', 'Derrota'),
        ('cancelada', 'Cancelada'),
    ]
    TIPO_ENTRADA_CHOICES = [
        ('digitacao', 'Digitação'),
        ('blocos', 'Blocos'),
        ('teclado', 'Teclado Virtual'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='partidas'
    )
    palavra = models.ForeignKey(
        Palavra,
        on_delete=models.PROTECT,
        related_name='partidas'
    )
    tipo_entrada = models.CharField(
        'Tipo de entrada',
        max_length=20,
        choices=TIPO_ENTRADA_CHOICES,
        default='digitacao'
    )
    tentativas_restantes = models.PositiveSmallIntegerField('Tentativas restantes', default=6)
    letras_tentadas = models.CharField('Letras tentadas', max_length=50, blank=True, default='')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='em_andamento')
    pontuacao = models.PositiveIntegerField('Pontuação obtida', default=0)
    data_inicio = models.DateTimeField('Início', auto_now_add=True)
    data_fim = models.DateTimeField('Fim', null=True, blank=True)

    class Meta:
        verbose_name = 'Partida'
        verbose_name_plural = 'Partidas'
        ordering = ['-data_inicio']

    def __str__(self):
        return f'Partida de {self.usuario.email} - {self.palavra.texto} ({self.get_status_display()})'
