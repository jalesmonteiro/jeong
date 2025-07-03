from django.urls import path
from .views.perfil import perfil_view, atualizar_tema
from .views.auth import login_view, logout_view, registro_view


app_name = 'usuarios'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro_view, name='registro'),
    path('perfil/', perfil_view, name='perfil'),
    path('atualizar_tema/', atualizar_tema, name='atualizar_tema'),

    # Adicione outras rotas conforme necessário
]
