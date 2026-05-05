// demo.js - Efecto de carga estilo Windows 11

// Datos de rubros
const rubros = {
    hora: ['Barbería', 'Consulta médica', 'Consulta profesional', 'Medicina Alternativa', 'Peluquería', 'Salón de Belleza'],
    espacio: ['Multicanchas', 'Oficinas', 'Recintos', 'Salones'],
    atencion: ['Centro de atención', 'Kinesiología', 'Dental'],
    clase: ['Clases grupales', 'Yoga', 'Entrenamiento']
};

// Cambiar rubro y actualizar dropdown
function cambiarRubro(key, element) {
    document.querySelectorAll('.service-card').forEach((c) => c.classList.remove('active'));
    element.classList.add('active');
    
    const select = document.getElementById('select-categorias');
    select.innerHTML = '<option value="">Seleccione..</option>';
    
    rubros[key].forEach((item) => {
        const opt = document.createElement('option');
        opt.value = item.toLowerCase().replace(' ', '_');
        opt.textContent = item;
        select.appendChild(opt);
    });
    
    document.getElementById('rubro_seleccionado').value = key;
}

// Inicializar
window.onload = () => {
    cambiarRubro('hora', document.querySelector('.service-card.active'));
    
    const formDemo = document.getElementById('form-demo');
    if (formDemo) {
        formDemo.addEventListener('submit', function(e) {
            e.preventDefault();
            
            mostrarLoading();  // Usa la función del global
            
            const formData = new FormData(this);
            
            fetch(formDemo.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                ocultarLoading();  // Usa la función del global
                
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Solicitud Enviada!',
                        text: data.message,
                        confirmButtonColor: '#3085d6',
                        confirmButtonText: 'Perfecto'
                    }).then(() => {
                        window.location.href = "/login/";
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.error || 'Hubo un problema al enviar tu solicitud.',
                        confirmButtonColor: '#d33'
                    });
                }
            })
            .catch(error => {
                ocultarLoading();
                Swal.fire({
                    icon: 'error',
                    title: 'Error de conexión',
                    text: 'No se pudo conectar con el servidor. Intenta nuevamente.',
                    confirmButtonColor: '#d33'
                });
            });
        });
    }
};