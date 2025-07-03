from collections import OrderedDict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from random import choice
from ..models.palavra import Palavra
from ..models.partida import Partida
from ..models.categoria import Categoria

# Mapeamento das consoantes duplas
DUPLAS_PARA_SIMPLES = {
    'ㄲ': 'ㄱ',
    'ㄸ': 'ㄷ',
    'ㅃ': 'ㅂ',
    'ㅆ': 'ㅅ',
    'ㅉ': 'ㅈ',
}
SIMPLES_PARA_DUPLAS = {v: k for k, v in DUPLAS_PARA_SIMPLES.items()}

def is_jamo(char):
    """Retorna True se o caractere for um jamo coreano isolado."""
    if len(char) != 1:
        return False
    code = ord(char)
    return 0x3130 <= code <= 0x318F

def silabas_reveladas(texto, jamo, letras_tentadas):
    """
    Retorna uma lista: sílaba se todas as letras dela já foram tentadas, senão '_'
    """
    silabas = list(texto)
    jamo_list = list(jamo)
    total_silabas = len(silabas)
    total_jamo = len(jamo_list)
    base = total_jamo // total_silabas
    extra = total_jamo % total_silabas
    idx = 0
    resultado = []
    for i, silaba in enumerate(silabas):
        n = base + (1 if i < extra else 0)
        silaba_jamo = jamo_list[idx:idx+n]
        idx += n
        # Checa se todos os jamos da sílaba foram tentados (com lógica de duplas)
        if all(jamo_revelado(j, jamo_list, i, letras_tentadas) for j in silaba_jamo):
            resultado.append(silaba)
        else:
            resultado.append('_')
    return resultado

def jamo_revelado(j, jamo_list, idx, letras_tentadas):
    """
    Retorna True se o jamo deve ser revelado, considerando duplas e simples.
    """
    # Verifica se é parte de uma dupla
    if j in DUPLAS_PARA_SIMPLES.values():
        # Simples: só revela se não for parte de dupla
        # Ex: não revela o primeiro 'ㅂ' em 'ㅂㅂ' se só tentou 'ㅂ'
        if idx > 0 and jamo_list[idx-1] == j:
            # É o segundo de uma dupla
            return False
        # Verifica se a próxima também é igual (dupla)
        if idx+1 < len(jamo_list) and jamo_list[idx+1] == j:
            # É o primeiro de uma dupla, só revela se a dupla foi tentada
            dupla = SIMPLES_PARA_DUPLAS.get(j)
            return dupla in letras_tentadas
        # Simples isolado
        return j in letras_tentadas
    elif j in DUPLAS_PARA_SIMPLES:
        # Dupla: só revela se a dupla foi tentada
        return j in letras_tentadas
    else:
        # Vogais e outros jamos
        return j in letras_tentadas

@login_required
def partida_nova_view(request):
    # 1. Verifica se já existe uma partida em andamento para o usuário
    partida_andamento = Partida.objects.filter(usuario=request.user, status='em_andamento').first()
    if partida_andamento:
        return redirect('jogo:partida_view')

    if request.method == 'POST':
        # 2. Se recebeu parâmetros, cria a partida
        categoria_id = request.POST.get('categoria')
        tipo_entrada = request.POST.get('tipo_entrada')
        dificuldade = request.POST.get('dificuldade', 1)

        palavras = Palavra.objects.all()
        if categoria_id and categoria_id != 'random':
            palavras = palavras.filter(categoria_id=int(categoria_id))

        palavras = list(palavras)
        if not palavras:
            # Nenhuma palavra para a categoria escolhida
            return render(request, 'jogo/partida_escolha.html', {
                'error': 'Nenhuma palavra encontrada para a categoria escolhida.',
                'categorias': Categoria.objects.all(),
                'tipos_entrada': [
                    ('digitacao', 'Digitação'),
                    ('blocos', 'Blocos'),
                    ('teclado', 'Teclado Virtual'),
                ],
                'dificuldades': [
                    (1, 'Fácil'),
                    (2, 'Médio'),
                    (3, 'Difícil'),
                ],
            })

        palavra = choice(palavras)
        tentativas_por_dificuldade = {'1': 20, '2': 15, '3': 10}
        tentativas = tentativas_por_dificuldade.get(str(dificuldade), 15)

        partida = Partida.objects.create(
            usuario=request.user,
            palavra=palavra,
            tentativas_restantes=tentativas,
            letras_tentadas='',
            status='em_andamento',
            pontuacao=0,
            tipo_entrada=tipo_entrada,
            dificuldade=dificuldade
        )
        return redirect('jogo:partida_view')

    # 3. Se GET, exibe a tela de escolha
    return render(request, 'jogo/partida_escolha.html', {
        'categorias': Categoria.objects.all(),
        'tipos_entrada': [
            ('digitacao', 'Digitação'),
            ('blocos', 'Blocos'),
            ('teclado', 'Teclado Virtual'),
        ],
        'dificuldades': [
            (1, 'Fácil'),
            (2, 'Médio'),
            (3, 'Difícil'),
        ],
    })

@login_required
@login_required
def partida_view(request):
    try:
        partida = Partida.objects.get(usuario=request.user, status='em_andamento')
    except Partida.DoesNotExist:
        return redirect('jogo:partida_nova')
    
    palavra = partida.palavra
    letras_tentadas = list(OrderedDict.fromkeys(partida.letras_tentadas))

    # --- Lógica de tentativa corrigida ---
    if partida.status == 'em_andamento' and request.method == 'POST':
        letra = request.POST.get('letra', '').strip()
        if not is_jamo(letra):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': "Digite apenas uma letra coreana válida (jamo)."})
            else:
                messages.warning(request, "Digite apenas uma letra coreana válida (jamo).")
                return redirect('jogo:partida_view')
        if letra and letra not in letras_tentadas:
            partida.letras_tentadas += letra
            letras_tentadas = list(OrderedDict.fromkeys(partida.letras_tentadas))

            # Nova lógica para verificar se acertou algo
            acertou = False
            jamo_list = list(palavra.jamo)
            if letra in DUPLAS_PARA_SIMPLES:
                # Tentou uma dupla: verifica se existe a sequência simples+simples
                simples = DUPLAS_PARA_SIMPLES[letra]
                for i in range(len(jamo_list)-1):
                    if jamo_list[i] == simples and jamo_list[i+1] == simples:
                        acertou = True
                        break
            elif letra in SIMPLES_PARA_DUPLAS:
                # Tentou uma simples: só acerta se houver simples isolada, não parte de dupla
                for i, j in enumerate(jamo_list):
                    if j == letra:
                        # Não pode ser parte de uma dupla
                        if not ((i+1 < len(jamo_list) and jamo_list[i+1] == letra) or
                                (i > 0 and jamo_list[i-1] == letra)):
                            acertou = True
                            break
            else:
                # Vogais e outros jamos
                if letra in jamo_list:
                    acertou = True

            if acertou:
                silabas_exibidas = silabas_reveladas(palavra.texto, palavra.jamo, letras_tentadas)
                if '_' not in silabas_exibidas:
                    partida.status = 'vitoria'
                    partida.data_fim = timezone.now()
                    partida.pontuacao = partida.tentativas_restantes * 10
            else:
                if partida.tentativas_restantes - 1 <= 0:
                    partida.status = 'derrota'
                    partida.data_fim = timezone.now()
                else:
                    partida.tentativas_restantes -= 1
            partida.save()

    # Prepara para exibição (igual ao seu código)
    silabas_exibidas = silabas_reveladas(palavra.texto, palavra.jamo, letras_tentadas)
    letras_exibidas = [l if l in letras_tentadas else '_' for l in palavra.jamo]
    linha1 = [
        {'key': 'Q', 'normal': 'ㅂ', 'shift': 'ㅃ'},
        {'key': 'W', 'normal': 'ㅈ', 'shift': 'ㅉ'},
        {'key': 'E', 'normal': 'ㄷ', 'shift': 'ㄸ'},
        {'key': 'R', 'normal': 'ㄱ', 'shift': 'ㄲ'},
        {'key': 'T', 'normal': 'ㅅ', 'shift': 'ㅆ'},
        {'key': 'Y', 'normal': 'ㅛ', 'shift': '-'},
        {'key': 'U', 'normal': 'ㅕ', 'shift': '-'},
        {'key': 'I', 'normal': 'ㅑ', 'shift': '-'},
        {'key': 'O', 'normal': 'ㅐ', 'shift': 'ㅒ'},
        {'key': 'P', 'normal': 'ㅔ', 'shift': 'ㅖ'},
    ]
    linha2 = [
        {'key': 'A', 'normal': 'ㅁ', 'shift': '-'},
        {'key': 'S', 'normal': 'ㄴ', 'shift': '-'},
        {'key': 'D', 'normal': 'ㅇ', 'shift': '-'},
        {'key': 'F', 'normal': 'ㄹ', 'shift': '-'},
        {'key': 'G', 'normal': 'ㅎ', 'shift': '-'},
        {'key': 'H', 'normal': 'ㅗ', 'shift': '-'},
        {'key': 'J', 'normal': 'ㅓ', 'shift': '-'},
        {'key': 'K', 'normal': 'ㅏ', 'shift': '-'},
        {'key': 'L', 'normal': 'ㅣ', 'shift': '-'},
    ]
    linha3 = [
        {'key': 'SHIFT-LEFT', 'normal': 'SHIFT', 'shift': 'SHIFT'},
        {'key': 'Z', 'normal': 'ㅋ', 'shift': '-'},
        {'key': 'X', 'normal': 'ㅌ', 'shift': '-'},
        {'key': 'C', 'normal': 'ㅊ', 'shift': '-'},
        {'key': 'V', 'normal': 'ㅍ', 'shift': '-'},
        {'key': 'B', 'normal': 'ㅠ', 'shift': '-'},
        {'key': 'N', 'normal': 'ㅜ', 'shift': '-'},
        {'key': 'M', 'normal': 'ㅡ', 'shift': '-'},
        {'key': 'SHIFT-RIGHT', 'normal': 'SHIFT', 'shift': 'SHIFT'},
    ]
    # Atualize letras_corretas e letras_erradas com a nova lógica
    letras_corretas = set()
    letras_erradas = set()
    jamo_list = list(palavra.jamo)
    for l in letras_tentadas:
        acertou = False
        if l in DUPLAS_PARA_SIMPLES:
            simples = DUPLAS_PARA_SIMPLES[l]
            for i in range(len(jamo_list)-1):
                if jamo_list[i] == simples and jamo_list[i+1] == simples:
                    acertou = True
                    break
        elif l in SIMPLES_PARA_DUPLAS:
            for i, j in enumerate(jamo_list):
                if j == l:
                    if not ((i+1 < len(jamo_list) and jamo_list[i+1] == l) or
                            (i > 0 and jamo_list[i-1] == l)):
                        acertou = True
                        break
        else:
            if l in jamo_list:
                acertou = True
        if acertou:
            letras_corretas.add(l)
        else:
            letras_erradas.add(l)

    context = {
        'partida': partida,
        'palavra': palavra,
        'silabas_exibidas': silabas_exibidas,
        'letras_exibidas': letras_exibidas,
        'letras_tentadas': list(letras_tentadas),
        'letras_corretas': list(letras_corretas),
        'letras_erradas': list(letras_erradas),
        'consoantes_simples': ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'],
        'consoantes_duplas': ['ㄲ', 'ㄸ', 'ㅃ', 'ㅆ', 'ㅉ'],
        'vogais_simples': ['ㅏ', 'ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ'],
        'vogais_compostas': ['ㅐ', 'ㅒ', 'ㅔ', 'ㅖ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅢ'],
        'linha1': linha1,
        'linha2': linha2,
        'linha3': linha3,
    }

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string("jogo/parcial/_partida_conteudo.html", context, request=request)
        return JsonResponse({
            'html': html,
            'letras_corretas': context['letras_corretas'],
            'letras_erradas': context['letras_erradas'],
            'status': partida.status,
            'partida_id': partida.pk
        })

    if partida.status != 'em_andamento':
        return redirect('jogo:partida_detalhe', pk=partida.pk)

    return render(request, 'jogo/partida.html', context)

@login_required
def partida_detalhe_view(request, pk):
    partida = get_object_or_404(Partida, pk=pk, usuario=request.user)
    if partida.status == 'em_andamento':
        return redirect('jogo:partida_view')
    context = {
        'partida': partida,
    }
    return render(request, 'jogo/partida_historico.html', context)