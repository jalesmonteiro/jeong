from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from apps.usuarios.models.perfil import PerfilUsuario

@login_required
def perfil_view(request):
    # Busca o perfil relacionado ao usuário logado
    perfil = getattr(request.user, 'perfilusuario', None)
    context = {
        'perfil': perfil,
        'user': request.user,
    }
    return render(request, 'usuarios/perfil.html', context)

def atualizar_tema(request):
    if request.method == "POST":
        tema = request.POST.get('tema')
        try:
            perfil = request.user.perfilusuario
            perfil.tema = tema
            perfil.save()
            return JsonResponse({'status': 'ok'})
        except PerfilUsuario.DoesNotExist:
            perfil = PerfilUsuario.objects.create(user=request.user)
            perfil.tema = tema
            perfil.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            print(f"Erro ao acessar ou salvar perfil: {e}")
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)
    return JsonResponse({'status': 'erro'}, status=400)
