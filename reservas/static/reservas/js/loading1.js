// demo.js - Efecto de carga estilo Windows 11

// Mostrar overlay de carga
function mostrarLoading() {
    let overlay = document.getElementById('loadingOverlay');
    if (!overlay) {
        // Crear overlay si no existe
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="windows11-loading">
                <div class="spinner-windows">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
                <div class="loading-text">
                    <div class="loading-title">Procesando solicitud</div>
                    <div class="loading-subtitle">
                        Estamos configurando tu espacio
                        <div class="loading-dots">
                            <span>.</span><span>.</span><span>.</span>
                        </div>
                    </div>
                </div>
                <div class="progress-bar-windows">
                    <div class="progress-fill"></div>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    overlay.style.display = 'flex';
}

// Ocultar overlay de carga
function ocultarLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Datos de rubros
const rubros = {
    hora: ['Barbería', 'Consulta médica', 'Consulta profesional', 'Medicina Alternativa', 'Peluquería', 'Salón de Belleza'],
    espacio: ['Multicanchas', 'Oficinas', 'Recintos', 'Salones'],
    atencion: ['Centro de atención', 'Kinesiología', 'Dental'],
    clase: ['Clases grupales', 'Yoga', 'Entrenamiento']
};

// Cambiar rubro y actualizar dropdown
function cambiarRubro(key, element) {
    // Actualizar tarjetas
    document.querySelectorAll('.service-card').forEach((c) => c.classList.remove('active'));
    element.classList.add('active');
    
    // Actualizar dropdown
    const select = document.getElementById('select-categorias');
    select.innerHTML = '<option value="">Seleccione..</option>';
    
    rubros[key].forEach((item) => {
        const opt = document.createElement('option');
        opt.value = item.toLowerCase().replace(' ', '_');
        opt.textContent = item;
        select.appendChild(opt);
    });
    
    // Guardar rubro seleccionado
    document.getElementById('rubro_seleccionado').value = key;
}

// Inicializar
window.onload = () => {
    cambiarRubro('hora', document.querySelector('.service-card.active'));
    
    // Configurar envío del formulario
    const formDemo = document.getElementById('form-demo');
    if (formDemo) {
        formDemo.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Mostrar overlay de carga
            mostrarLoading();
            
            const formData = new FormData(this);
            
            fetch(formDemo.action, {
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



