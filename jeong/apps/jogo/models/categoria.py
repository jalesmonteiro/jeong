from django.db import models

class Categoria(models.Model):
    nome = models.CharField('Nome da categoria', max_length=50, unique=True)
    descricao = models.TextField('Descrição', blank=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome
