// reservas/static/reservas/js/recuperar.js

document.addEventListener('DOMContentLoaded', function() {
    const forgotForm = document.querySelector('#forgot-card form');
    
    if (forgotForm) {
        console.log('recuperar.js: Formulario de recuperación encontrado');
        
        forgotForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[name="email"]')?.value.trim();
            
            if (!email) {
                Swal.fire({
                    icon: 'error',
                    title: 'Campo requerido',
                    text: 'Debes ingresar tu correo electrónico.',
                    confirmButtonColor: '#ef233c'
                });
                return;
            }
            
            // Validar email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                Swal.fire({
                    icon: 'error',
                    title: 'Email inválido',
                    text: 'Ingresa un correo electrónico válido.',
                    confirmButtonColor: '#ef233c'
                });
                return;
            }
            
            // Mostrar loading
            mostrarLoading();
            
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                ocultarLoading();
                
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Enlace enviado',
                        text: data.message || 'Revisa tu correo para restablecer tu contraseña.',
                        confirmButtonColor: '#28a745',
                        confirmButtonText: 'Entendido'
                    }).then(() => {
                        // Volver al login
                        document.getElementById('forgot-card').style.display = 'none';
                        document.getElementById('login-card').style.display = 'block';
                        forgotForm.reset();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.error || 'No se pudo enviar el enlace',
                        confirmButtonColor: '#ef233c'
                    });
                }
            })
            .catch(error => {
                ocultarLoading();
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error de conexión',
                    text: 'No se pudo conectar con el servidor',
                    confirmButtonColor: '#ef233c'
                });
            });
        });
    } else {
        console.log('recuperar.js: No se encontró el formulario de recuperación');
    }
});