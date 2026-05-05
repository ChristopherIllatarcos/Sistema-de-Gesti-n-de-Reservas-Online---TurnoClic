// reservas/static/reservas/js/login.js

document.addEventListener('DOMContentLoaded', function() {
    // FUNCIONALIDAD: Mostrar tarjeta de registro
    const btnRegistro = document.getElementById('btn-show-register');
    if (btnRegistro) {
        btnRegistro.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('login-card').style.display = 'none';
            document.getElementById('register-card').style.display = 'block';
        });
    }
    
    // FUNCIONALIDAD: Volver a login
    const btnBackToLogin = document.querySelectorAll('.btn-back-to-login');
    btnBackToLogin.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('register-card').style.display = 'none';
            document.getElementById('forgot-card').style.display = 'none';
            document.getElementById('activate-card').style.display = 'none';
            document.getElementById('login-card').style.display = 'block';
        });
    });
    
    // FUNCIONALIDAD: Mostrar forgot
    const btnForgot = document.getElementById('btn-show-forgot');
    if (btnForgot) {
        btnForgot.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('login-card').style.display = 'none';
            document.getElementById('forgot-card').style.display = 'block';
        });
    }
    
    // FUNCIONALIDAD: Mostrar activate
    const btnActivate = document.getElementById('btn-show-activate');
    if (btnActivate) {
        btnActivate.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('login-card').style.display = 'none';
            document.getElementById('activate-card').style.display = 'block';
        });
    }
});