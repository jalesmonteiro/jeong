from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def perfil_view(request):
    # Busca o perfil relacionado ao usuário logado
    perfil = getattr(request.user, 'perfilusuario', None)
    context = {
        'perfil': perfil,
        'user': request.user,
    }
    return render(request, 'usuarios/perfil.html', context)
