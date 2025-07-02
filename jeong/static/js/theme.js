document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('theme-toggle');
    btn.addEventListener('click', function() {
        const html = document.documentElement;
        const current = html.getAttribute('data-theme');
        html.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
    });
});
