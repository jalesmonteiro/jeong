from django.contrib import admin
from .models.categoria import Categoria
from .models.palavra import Palavra
from .models.partida import Partida

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(Palavra)
class PalavraAdmin(admin.ModelAdmin):
    list_display = ('texto', 'idioma', 'categoria')
    list_filter = ('idioma', 'categoria')
    search_fields = ('texto',)

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = (
        'usuario', 'palavra', 'status', 'tentativas_restantes',
        'pontuacao', 'data_inicio', 'data_fim', 'dificuldade'
    )
    list_filter = ('status', 'data_inicio', 'data_fim')
    search_fields = ('usuario__email', 'palavra__texto')
    readonly_fields = ('data_inicio', 'data_fim')
