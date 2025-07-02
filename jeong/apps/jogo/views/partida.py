from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from random import choice
from ..models.palavra import Palavra
from ..models.partida import Partida
from ..models.categoria import Categoria

TIPOS_ENTRADA = [
    ('digitacao', 'Digitação'),
    ('blocos', 'Blocos'),
    ('teclado', 'Teclado Virtual'),
]

@login_required
def partida_nova_view(request):
    categoria_id = request.session.get('categoria_id')
    tipo_entrada = request.session.get('tipo_entrada')
    palavras = Palavra.objects.all()
    if categoria_id and categoria_id != "random":
        palavras = palavras.filter(categoria_id=categoria_id)
    palavra = choice(list(palavras))
    partida = Partida.objects.create(
        usuario=request.user,
        palavra=palavra,
        tentativas_restantes=10,
        letras_tentadas='',
        status='em_andamento',
        pontuacao=0,
        tipo_entrada=tipo_entrada,
    )
    # Opcional: salve o tipo de entrada na sessão para uso na view da partida
    return redirect('jogo:partida_detalhe', pk=partida.pk)


@login_required
def partida_escolha_view(request):
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        tipo_entrada = request.POST.get('tipo_entrada')
        # Salva na sessão ou passa via GET/POST para a próxima view
        request.session['categoria_id'] = categoria_id
        request.session['tipo_entrada'] = tipo_entrada
        return redirect('jogo:partida_nova')
    return render(request, 'jogo/partida_escolha.html', {
        'categorias': categorias,
        'tipos_entrada': TIPOS_ENTRADA,
    })

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
def partida_detalhe_view(request, pk):
    partida = get_object_or_404(Partida, pk=pk, usuario=request.user)
    palavra = partida.palavra
    letras_tentadas = set(partida.letras_tentadas)

    # Divide o jamo conforme as sílabas
    silabas_com_jamo = split_jamo_por_silaba(palavra.texto, palavra.jamo)

    # Processa tentativa de letra (jamo)
    if partida.status == 'em_andamento' and request.method == 'POST':
        letra = request.POST.get('letra', '').strip()
        if letra and letra not in letras_tentadas:
            # Adiciona a letra tentada (certa ou errada)
            letras_tentadas.add(letra)
            partida.letras_tentadas = ''.join(sorted(letras_tentadas))
            if letra in palavra.jamo:
                letras_tentadas.add(letra)
                partida.letras_tentadas = ''.join(sorted(letras_tentadas))
                # Verifica se todas as letras já foram tentadas
                todas_silabas_reveladas = all(
                    all(j in letras_tentadas for j in silaba_jamo)
                    for _, silaba_jamo in silabas_com_jamo
                )
                if todas_silabas_reveladas:
                    partida.status = 'vitoria'
                    partida.data_fim = timezone.now()
                    partida.pontuacao = partida.tentativas_restantes * 10
                elif partida.tentativas_restantes - 1 <= 0:
                    partida.status = 'derrota'
                    partida.data_fim = timezone.now()
                partida.save()
            else:
                if partida.tentativas_restantes - 1 <= 0:
                    partida.status = 'derrota'
                    partida.data_fim = timezone.now()
                else:
                    partida.tentativas_restantes -= 1
            partida.save()
        return redirect('jogo:partida_detalhe', pk=partida.pk)

    # Prepara para exibição: sílabas e letras
    silabas_exibidas = []
    letras_exibidas = []

    for silaba, silaba_jamo in silabas_com_jamo:
        if all(j in letras_tentadas for j in silaba_jamo):
            silabas_exibidas.append(silaba)
        else:
            silabas_exibidas.append('_')
        for j in silaba_jamo:
            if j in letras_tentadas:
                letras_exibidas.append(j)
            else:
                letras_exibidas.append('_')

    context = {
        'partida': partida,
        'palavra': palavra,
        'silabas_exibidas': silabas_exibidas,
        'letras_exibidas': letras_exibidas,
        'letras_tentadas': letras_tentadas,
        'silabas_com_jamo': silabas_com_jamo,
        'consoantes_simples': ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'],
        'consoantes_duplas': ['ㄲ', 'ㄸ', 'ㅃ', 'ㅆ', 'ㅉ'],
        'vogais_simples': ['ㅏ', 'ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ'],
        'vogais_compostas': ['ㅐ', 'ㅒ', 'ㅔ', 'ㅖ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅢ'],
    }
    return render(request, 'jogo/partida.html', context)

