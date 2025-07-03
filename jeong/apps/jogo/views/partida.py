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

# Função para dividir jamo proporcionalmente pelas sílabas
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
        if all(l in letras_tentadas for l in silaba_jamo):
            resultado.append(silaba)
        else:
            resultado.append('_')
    return resultado

def is_jamo(char):
    """Retorna True se o caractere for um jamo coreano isolado."""
    if len(char) != 1:
        return False
    code = ord(char)
    # Jamo compatíveis (usados para digitação): 0x3130–0x318F
    return 0x3130 <= code <= 0x318F

# Função para dividir o jamo conforme as sílabas do texto
def split_jamo_por_silaba(texto, jamo):
    """
    Divide a string jamo em grupos conforme o número de sílabas do texto.
    Exemplo: texto="학교", jamo="ㅎㅏㄱㄱㅛ" -> [("학", "ㅎㅏㄱ"), ("교", "ㄱㅛ")]
    """
    # Aqui, usamos o unicodedata para decompor, mas como já temos o jamo salvo, 
    # só precisamos dividir proporcionalmente.
    # O ideal é que, ao cadastrar a palavra, você salve também o "mapeamento" (quantos jamo por sílaba).
    # Para exemplo, vamos assumir 2 jamo para cada sílaba exceto se a palavra for cadastrada diferente.
    silabas = list(texto)
    jamo_list = list(jamo)
    resultado = []
    idx = 0
    for silaba in silabas:
        # Aqui, você pode melhorar para pegar a quantidade certa de jamo por sílaba.
        # Para exemplo, vamos assumir 2 jamo por sílaba, exceto se faltar menos.
        if idx + 2 <= len(jamo_list):
            silaba_jamo = jamo_list[idx:idx+2]
            idx += 2
        else:
            silaba_jamo = jamo_list[idx:]
            idx = len(jamo_list)
        resultado.append((silaba, silaba_jamo))
    return resultado

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
def partida_view(request):
    try:
        partida = Partida.objects.get(usuario=request.user, status='em_andamento')
    except Partida.DoesNotExist:
        return redirect('jogo:partida_nova')
    
    palavra = partida.palavra
    letras_tentadas = set(partida.letras_tentadas)
    status_anterior = partida.status

    # Processa tentativa de letra (jamo)
    if partida.status == 'em_andamento' and request.method == 'POST':
        letra = request.POST.get('letra', '').strip()
        if not is_jamo(letra):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': "Digite apenas uma letra coreana válida (jamo)."})
            else:
                messages.warning(request, "Digite apenas uma letra coreana válida (jamo).")
                return redirect('jogo:partida_view')
        if letra and letra not in letras_tentadas:
            letras_tentadas.add(letra)
            partida.letras_tentadas = ''.join(sorted(letras_tentadas))
            if letra in palavra.jamo:
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
        # Atualize variáveis do contexto após possível modificação
        letras_tentadas = set(partida.letras_tentadas)

    # Prepara para exibição
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
    letras_corretas = set(l for l in letras_tentadas if l in palavra.jamo)
    letras_erradas = letras_tentadas - letras_corretas

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

    # AJAX: retorna só o HTML da área dinâmica e o status da partida
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string("jogo/parcial/_partida_conteudo.html", context, request=request)
        return JsonResponse({
            'html': html,
            'letras_corretas': context['letras_corretas'],
            'letras_erradas': context['letras_erradas'],
            'status': partida.status,
            'partida_id': partida.pk
        })

    # Se a partida terminou (vitória/derrota), redirecione para a tela de detalhe
    if partida.status != 'em_andamento':
        return redirect('jogo:partida_detalhe', pk=partida.pk)

    # GET normal: renderiza a página inteira
    return render(request, 'jogo/partida.html', context)

@login_required
def partida_detalhe_view(request, pk):
    partida = get_object_or_404(Partida, pk=pk, usuario=request.user)
    if partida.status == 'em_andamento':
        # Se tentar acessar uma partida em andamento por ID, redireciona para a view principal
        return redirect('jogo:partida_view')
    # Só exibe partidas encerradas (vitória/derrota/cancelada)
    # Aqui só exibe, não executa lógica de jogo
    context = {
        'partida': partida,
        # outros dados para exibição do histórico...
    }
    return render(request, 'jogo/partida_historico.html', context)