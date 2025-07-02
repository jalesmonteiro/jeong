from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.usuarios.forms import LoginEmailForm, RegistroForm

def login_view(request):
    if request.method == 'POST':
        form = LoginEmailForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')
    else:
        form = LoginEmailForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('usuarios:login')

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro realizado! Faça login para continuar.')
            return redirect('usuarios:login')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})
