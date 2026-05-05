// reservas/static/reservas/js/registro.js

document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    
    if (registerForm) {
        console.log('registro.js: Formulario de registro encontrado');
        
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const nombre = document.getElementById('reg_nombre')?.value.trim();
            const email = document.getElementById('reg_email')?.value.trim();
            const pass1 = document.getElementById('reg_pass1')?.value;
            const pass2 = document.getElementById('reg_pass2')?.value;
            
            // Validar campos
            if (!nombre || !email || !pass1 || !pass2) {
                Swal.fire({
                    icon: 'error',
                    title: 'Campos incompletos',
                    text: 'Por favor, completa todos los campos.',
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
            
            // Validar contraseñas
            if (pass1.length < 6) {
                Swal.fire({
                    icon: 'error',
                    title: 'Contraseña débil',
                    text: 'La contraseña debe tener al menos 6 caracteres.',
                    confirmButtonColor: '#ef233c'
                });
                return;
            }
            
            if (pass1 !== pass2) {
                Swal.fire({
                    icon: 'error',
                    title: 'Contraseñas no coinciden',
                    text: 'Las contraseñas ingresadas no son iguales.',
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
                        title: '¡Registro exitoso!',
                        text: data.message || 'Tu cuenta ha sido creada.',
                        confirmButtonColor: '#28a745',
                        confirmButtonText: 'Ir a iniciar sesión'
                    }).then(() => {
                        document.getElementById('register-card').style.display = 'none';
                        document.getElementById('login-card').style.display = 'block';
                        registerForm.reset();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.error || 'No se pudo completar el registro',
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
        console.log('registro.js: No se encontró el formulario de registro');
    }
}); 