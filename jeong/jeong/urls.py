from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('apps.usuarios.urls')),
    path('jogo/', include('apps.jogo.urls')),
    path('gamificacao/', include('apps.gamificacao.urls')),
    path('notificacoes/', include('apps.notificacoes.urls')),
]
