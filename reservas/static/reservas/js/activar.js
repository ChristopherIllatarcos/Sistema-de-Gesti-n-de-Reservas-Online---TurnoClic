// reservas/static/reservas/js/activar.js

document.addEventListener('DOMContentLoaded', function() {
    const activateForm = document.querySelector('#activate-card form');
    
    if (activateForm) {
        console.log('activar.js: Formulario de activación encontrado');
        
        activateForm.addEventListener('submit', function(e) {
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
                        title: '¡Cuenta activada!',
                        text: data.message || 'Tu cuenta ha sido activada exitosamente.',
                        confirmButtonColor: '#28a745',
                        confirmButtonText: 'Iniciar sesión'
                    }).then(() => {
                        // Volver al login
                        document.getElementById('activate-card').style.display = 'none';
                        document.getElementById('login-card').style.display = 'block';
                        activateForm.reset();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.error || 'No se pudo activar la cuenta',
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
        console.log('activar.js: No se encontró el formulario de activación');
    }
});