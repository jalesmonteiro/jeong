document.addEventListener('DOMContentLoaded', function () {
    let shiftAtivo = false;

    // Função para atualizar o teclado (deve ser chamada após cada AJAX)
    function atualizarTeclas() {
        document.querySelectorAll('.tecla-jamo').forEach(function (btn) {
            const normal = btn.getAttribute('data-normal');
            const shift = btn.getAttribute('data-shift');
            const letra = shiftAtivo ? shift : normal;

            btn.querySelector('.letra-normal').style.display = shiftAtivo ? 'none' : '';
            btn.querySelector('.letra-shift').style.display = shiftAtivo ? '' : 'none';

            btn.classList.remove('tecla-correta', 'tecla-errada');
            btn.disabled = false;

            if (window.letrasCorretas.includes(letra)) {
                btn.classList.add('tecla-correta');
                btn.disabled = true;
            } else if (window.letrasErradas.includes(letra)) {
                btn.classList.add('tecla-errada');
                btn.disabled = true;
            }
        });

        document.querySelectorAll('.tecla-shift').forEach(function (btn) {
            btn.classList.toggle('btn-danger', shiftAtivo);
            btn.classList.toggle('btn-secondary', !shiftAtivo);
        });
    }
    
    // Função para reatribuir eventos após AJAX
    function bindTeclado() {
        document.querySelectorAll('.tecla-jamo').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const letra = shiftAtivo ? btn.getAttribute('data-shift') : btn.getAttribute('data-normal');
                if (letra && letra !== '-') {
                    enviarLetra(letra);
                }
            });
        });
        document.querySelectorAll('.tecla-shift').forEach(function (btn) {
            btn.addEventListener('click', function () {
                shiftAtivo = !shiftAtivo;
                atualizarTeclas();
            });
        });
    }

    // Função AJAX para enviar letra
    function enviarLetra(letra) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: 'letra=' + encodeURIComponent(letra)
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('jogo-area').innerHTML = data.html;
                // Atualize as listas globais/locais
                window.letrasCorretas = data.letras_corretas || [];
                window.letrasErradas = data.letras_erradas || [];
                //shiftAtivo = false;
                bindTeclado();
                atualizarTeclas();
            });
    }

    // Atalho de teclado físico
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Shift') {
            shiftAtivo = !shiftAtivo;
            atualizarTeclas();
            event.preventDefault();
            return;
        }
        const key = event.key.toUpperCase();
        document.querySelectorAll('.tecla-jamo').forEach(function (btn) {
            if (btn.getAttribute('data-key').toUpperCase() === key) {
                const letra = shiftAtivo ? btn.getAttribute('data-shift') : btn.getAttribute('data-normal');
                if (letra && letra !== '-') {
                    enviarLetra(letra);
                    shiftAtivo = false; // Reset shift após envio por teclado físico também
                    atualizarTeclas();
                }
            }
        });
    });
    bindTeclado();
    atualizarTeclas();
});
