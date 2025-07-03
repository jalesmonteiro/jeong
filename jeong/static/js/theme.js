document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('theme-toggle');
    btn.addEventListener('click', function() {
        const html = document.documentElement;
        const current = html.getAttribute('data-theme');
        const novoTema = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', novoTema);

        // Envia para o backend via AJAX
        fetch('/usuarios/atualizar_tema/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'tema=' + encodeURIComponent(novoTema)
        })
        .then(response => {
            if (!response.ok) {
                // Se der erro, volta para o tema anterior
                html.setAttribute('data-theme', current);
                alert('Erro ao salvar o tema. Tente novamente.');
            }
        })
        .catch(() => {
            html.setAttribute('data-theme', current);
            alert('Erro ao salvar o tema. Tente novamente.');
        });
    });

    // Função para pegar o CSRF token do cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
