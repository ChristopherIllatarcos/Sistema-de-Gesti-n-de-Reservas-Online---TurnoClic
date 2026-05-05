// reservas/static/reservas/js/loading.js

// Mostrar overlay de carga
function mostrarLoading() {
    let overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

// Ocultar overlay de carga
function ocultarLoading() {
    let overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}