from django.shortcuts import render, get_object_or_404
from ..models.palavra import Palavra

def palavra_list_view(request):
    """
    Lista todas as palavras cadastradas.
    """
    palavras = Palavra.objects.select_related('categoria').order_by('texto')
    context = {
        'palavras': palavras,
    }
    return render(request, 'jogo/palavra_list.html', context)

def palavra_detalhe_view(request, pk):
    """
    Exibe detalhes de uma palavra específica.
    """
    palavra = get_object_or_404(Palavra, pk=pk)
    context = {
        'palavra': palavra,
    }
    return render(request, 'jogo/palavra.html', context)
