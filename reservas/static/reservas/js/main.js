// Esperamos a que el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const btnTop = document.getElementById('btn-back-to-top');

    // Función para mostrar/ocultar el botón al hacer scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            btnTop.classList.add('show');
        } else {
            btnTop.classList.remove('show');
        }
    });

    // Acción de volver arriba al hacer click
    btnTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth' // Subida suave, no de golpe
        });
    });
});

console.log("Vortex Script Cargado con Éxito"); // Si ves esto en la consola, el archivo está vinculado

window.addEventListener('scroll', function() {
    // Calculamos el scroll
    const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    
    // Aplicamos a la barra
    const bar = document.getElementById("vortexBar");
    if (bar) {
        bar.style.width = scrolled + "%";
    }

    // Botón volver arriba
    const btnTop = document.getElementById('btn-back-to-top');
    if (btnTop) {
        if (window.pageYOffset > 300) {
            btnTop.classList.add('show');
        } else {
            btnTop.classList.remove('show');
        }
    }
});

// Evento click del botón (fuera del scroll para eficiencia)
document.addEventListener('click', function(e) {
    if (e.target.closest('#btn-back-to-top')) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});


document.addEventListener('DOMContentLoaded', function() {
    // 1. Manejo de tarjetas (Login, Registro, etc.)
    const cards = {
        login: document.getElementById('login-card'),
        forgot: document.getElementById('forgot-card'),
        activate: document.getElementById('activate-card'),
        register: document.getElementById('register-card')
    };

    const btns = {
        showForgot: document.getElementById('btn-show-forgot'),
        showActivate: document.getElementById('btn-show-activate'),
        showRegister: document.getElementById('btn-show-register'),
        backToLogin: document.querySelectorAll('.btn-back-to-login')
    };

    function switchCard(target) {
        // Solo ocultamos si la tarjeta existe para evitar errores
        Object.values(cards).forEach(card => { if(card) card.style.display = 'none'; });
        if(cards[target]) cards[target].style.display = 'block';
    }

    if (btns.showForgot) btns.showForgot.onclick = () => switchCard('forgot');
    if (btns.showActivate) btns.showActivate.onclick = () => switchCard('activate');
    if (btns.showRegister) btns.showRegister.onclick = () => switchCard('register');

    btns.backToLogin.forEach(btn => {
        btn.onclick = () => switchCard('login');
    });

    // 2. Lógica ÚNICA para el ojo (Delegación de eventos)
    // Esto funciona para el ojo del login y cualquier ojo de registro
    document.addEventListener('click', function(e) {
        const toggleBtn = e.target.closest('#toggle-eye') || e.target.closest('.toggle-reg-eye');
        
        if (toggleBtn) {
            // Buscamos el input que está justo antes del span (en el mismo grupo)
            const input = toggleBtn.parentElement.querySelector('input');
            
            if (input) {
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                
                // Feedback visual: Rojo Vortex si se ve, Gris si está oculto
                toggleBtn.style.color = isPassword ? '#ef233c' : '#999';
            }
        }
    });
});