from django.urls import path
from .views.partida import partida_nova_view, partida_detalhe_view, partida_escolha_view
from .views.palavra import palavra_list_view, palavra_detalhe_view

app_name = 'jogo'

urlpatterns = [
    # Rotas para partidas
    path('partida/escolha/', partida_escolha_view, name='partida_escolha'),
    path('partida/nova/', partida_nova_view, name='partida_nova'),
    path('partida/<int:pk>/', partida_detalhe_view, name='partida_detalhe'),

    # Rotas para palavras
    path('palavras/', palavra_list_view, name='palavra_list'),
    path('palavra/<int:pk>/', palavra_detalhe_view, name='palavra_detalhe'),

    # Outras rotas podem ser adicionadas conforme necessário
]
