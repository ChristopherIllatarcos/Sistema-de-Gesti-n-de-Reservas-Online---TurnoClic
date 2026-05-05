// ===============================
// VARIABLES GLOBALES
// ===============================
let fechaActual = new Date();
let diasAtencion = [];
let fechaSeleccionada = null;
let horaSeleccionada = null;

// ===============================
// ACTUALIZAR INFO SERVICIO (precio/tiempo)
// ===============================
function actualizarInformacionServicio() {
    const selector = document.getElementById("service-select");
    const infoBox = document.getElementById("info-reserva");

    const displayPrecio = document.getElementById("display-precio");
    const displayTiempo = document.getElementById("display-tiempo");
    const displayDescripcion = document.getElementById("display-descripcion");

    if (!selector || !infoBox || !displayPrecio || !displayTiempo || !displayDescripcion) {
        console.error("Faltan elementos HTML para mostrar precio/tiempo/descripción.");
        return;
    }

    const option = selector.options[selector.selectedIndex];

    if (option && option.value) {
        const precio = option.getAttribute("data-precio") || "0";
        const tiempo = option.getAttribute("data-tiempo") || "0";
        const descripcion = option.getAttribute("data-descripcion") || "";

        displayPrecio.innerText = precio;
        displayTiempo.innerText = tiempo;
        displayDescripcion.innerText = descripcion;

        infoBox.style.display = "block";
    } else {
        infoBox.style.display = "none";
    }
}

// ===============================
// VALIDAR PASO 1 Y AVANZAR
// ===============================
function irAlPaso2() {
    const servicioEl = document.getElementById("service-select");
    const proEl = document.getElementById("pro-select");

    if (!servicioEl || !proEl) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: "No se encuentran los selectores en el formulario.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    const servicio = servicioEl.value;
    const profesional = proEl.value;

    if (!servicio) {
        Swal.fire({
            icon: "warning",
            title: "Campo requerido",
            text: "Por favor, selecciona un servicio.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    if (!profesional) {
        let mensaje = "Por favor, selecciona ";
        const rubro = document.body.getAttribute('data-rubro') || '';
        if (rubro === 'deporte') {
            mensaje += "una cancha o espacio.";
        } else if (rubro === 'educacion') {
            mensaje += "un instructor.";
        } else if (rubro === 'salud') {
            mensaje += "un especialista.";
        } else {
            mensaje += "un profesional.";
        }
        
        Swal.fire({
            icon: "warning",
            title: "Campo requerido",
            text: mensaje,
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    // Mostrar nombres
    const nombreServicio = servicioEl.selectedOptions[0].text;
    const nombreProfesional = proEl.selectedOptions[0].text;

    document.getElementById("nombre-servicio").innerText = nombreServicio;
    document.getElementById("nombre-profesional").innerText = nombreProfesional;

    mostrarPaso("paso-2");

    requestAnimationFrame(() => {
        cargarDisponibilidad();
    });
}

// ===============================
// PASO 2 -> PASO 1
// ===============================
function irAlPaso1() {
    document.getElementById("paso-2").style.display = "none";
    document.getElementById("paso-1").style.display = "block";
}

// ===============================
// CARGAR DISPONIBILIDAD DEL PROFESIONAL
// ===============================
function cargarDisponibilidad() {
    const proEl = document.getElementById("pro-select");
    if (!proEl) return;

    const profesionalId = proEl.value;

    fetch(`/api/disponibilidad/?profesional_id=${profesionalId}`)
        .then(res => res.json())
        .then(data => {
            diasAtencion = data.fechas_disponibles || [];
            renderizarCalendario();
        })
        .catch(err => console.error("Error cargando disponibilidad:", err));
}

// ===============================
// CAMBIAR MES (BOTONES ❮ ❯)
// ===============================
function cambiarMes(direccion) {
    fechaActual.setMonth(fechaActual.getMonth() + direccion);
    renderizarCalendario();
}

// ===============================
// RENDERIZAR CALENDARIO
// ===============================
function renderizarCalendario() {
    const cuerpo = document.getElementById("calendar-body");
    const displayMes = document.getElementById("month-name");

    if (!cuerpo || !displayMes) {
        console.error("No existe calendar-body o month-name");
        return;
    }

    cuerpo.innerHTML = "";

    const anioActual = fechaActual.getFullYear();
    const mesActual = fechaActual.getMonth();

    const meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ];

    displayMes.innerText = `${meses[mesActual]} ${anioActual}`;

    // Encabezados de días
    const diasSemana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"];
    diasSemana.forEach(d => {
        const div = document.createElement("div");
        div.className = "day-name";
        div.innerText = d;
        cuerpo.appendChild(div);
    });

    // Primer día del mes
    let primerDia = new Date(anioActual, mesActual, 1).getDay() - 1;
    if (primerDia === -1) primerDia = 6;

    // Espacios vacíos
    for (let i = 0; i < primerDia; i++) {
        const vacio = document.createElement("div");
        vacio.className = "calendar-day empty";
        cuerpo.appendChild(vacio);
    }

    // Días del mes
    const diasEnMes = new Date(anioActual, mesActual + 1, 0).getDate();

    for (let dia = 1; dia <= diasEnMes; dia++) {
        const divDia = document.createElement("div");
        divDia.className = "calendar-day";
        divDia.innerText = dia;

        const f_mes = (mesActual + 1).toString().padStart(2, "0");
        const f_dia = dia.toString().padStart(2, "0");
        const fechaCotejo = `${anioActual}-${f_mes}-${f_dia}`;

        if (diasAtencion.includes(fechaCotejo)) {
            divDia.classList.add("available");

            divDia.onclick = function () {
                seleccionarDia(fechaCotejo, divDia);
            };

        } else {
            divDia.style.opacity = "0.3";
            divDia.style.pointerEvents = "none";
        }

        cuerpo.appendChild(divDia);
    }
}

// ===============================
// SELECCIONAR DÍA
// ===============================
function seleccionarDia(fecha, elemento) {
    fechaSeleccionada = fecha;
    horaSeleccionada = null;

    document.querySelectorAll(".calendar-day").forEach(d => {
        d.classList.remove("selected");
    });

    elemento.classList.add("selected");

    const containerHoras = document.getElementById("container-horas");
    const textoFecha = document.getElementById("fecha-seleccionada-texto");

    if (containerHoras && textoFecha) {
        containerHoras.style.display = "block";
        textoFecha.innerText = `HORAS DISPONIBLES PARA: ${fecha}`;
    }

    cargarHorasDisponibles(fecha);
}

// ===============================
// CARGAR HORAS DISPONIBLES
// ===============================
function cargarHorasDisponibles(fecha) {
    const proEl = document.getElementById("pro-select");
    const horasGrid = document.getElementById("horas-grid");

    if (!proEl || !horasGrid) return;

    const profesionalId = proEl.value;

    if (!profesionalId) {
        horasGrid.innerHTML = "<p style='font-size:0.85rem;'>Selecciona un profesional primero.</p>";
        return;
    }

    if (!fecha) {
        horasGrid.innerHTML = "<p style='font-size:0.85rem;'>Selecciona una fecha.</p>";
        return;
    }

    horasGrid.innerHTML = "<p style='font-size:0.85rem;'>Cargando horas...</p>";

    fetch(`/api/horas/?profesional_id=${profesionalId}&fecha=${fecha}`)
        .then(res => res.json())
        .then(data => {
            const horasDisponibles = data.horas_disponibles || [];
            const horasOcupadas = data.horas_ocupadas || [];

            horasGrid.innerHTML = "";

            if (horasDisponibles.length === 0) {
                horasGrid.innerHTML = "<p style='font-size:0.85rem;'>No hay horas disponibles.</p>";
                return;
            }

            horasDisponibles.forEach(hora => {
                const btn = document.createElement("button");
                btn.className = "hora-btn";
                btn.type = "button";
                btn.innerText = hora;
                btn.dataset.hora = hora;

                if (horasOcupadas.includes(hora)) {
                    btn.disabled = true;
                    btn.classList.add("hora-ocupada");
                }

                btn.onclick = function () {
                    seleccionarHora(hora, btn);
                };

                horasGrid.appendChild(btn);
            });
        })
        .catch(err => {
            console.error("Error cargando horas:", err);
            horasGrid.innerHTML = "<p style='font-size:0.85rem;'>Error cargando horas.</p>";
        });
}

// ===============================
// SELECCIONAR HORA
// ===============================
function seleccionarHora(hora, boton) {
    horaSeleccionada = hora;

    document.querySelectorAll(".hora-btn").forEach(b => {
        b.classList.remove("selected-hora");
    });

    boton.classList.add("selected-hora");
}

// ===============================
// VALIDAR PASO 2 Y AVANZAR
// ===============================
function irAlPaso3() {
    if (!fechaSeleccionada) {
        Swal.fire({
            icon: "warning",
            title: "Fecha no seleccionada",
            text: "Por favor, selecciona una fecha disponible.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    if (!horaSeleccionada) {
        Swal.fire({
            icon: "warning",
            title: "Hora no seleccionada",
            text: "Por favor, selecciona una hora disponible.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    mostrarPaso("paso-3");

    const proSelect = document.getElementById("pro-select");
    const nombreProfesional = proSelect?.selectedOptions[0]?.text || "";

    document.getElementById("resumen-profesional").innerText = nombreProfesional;
    document.getElementById("resumen-fecha").innerText = fechaSeleccionada;
    document.getElementById("resumen-hora").innerText = horaSeleccionada;
}

// ===============================
// VALIDAR RUT Y AVANZAR
// ===============================
function irAlPaso4() {
    const rut = document.getElementById("rut-cliente").value.trim();

    if (!rut) {
        Swal.fire({
            icon: "warning",
            title: "Campo requerido",
            text: "Por favor, ingresa tu RUT para continuar.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    if (rut.length < 8) {
        Swal.fire({
            icon: "error",
            title: "RUT inválido",
            text: "Por favor, ingresa un RUT válido.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    mostrarPaso("paso-4");
    buscarCliente();
}

// ===============================
// VALIDAR FORMULARIO Y CONFIRMAR RESERVA
// ===============================
function confirmarReserva() {
    const btn = document.querySelector(".btn-main[onclick='confirmarReserva()']");
    const btnOriginal = btn;
    
    const nombres = document.getElementById("nombres-cliente").value.trim();
    const apellidoP = document.getElementById("apellido-paterno").value.trim();
    const telefono = document.getElementById("telefono-cliente").value.trim();
    const correo = document.getElementById("correo-cliente").value.trim();

    if (!nombres) {
        Swal.fire({
            icon: "warning",
            title: "Campo requerido",
            text: "Por favor, ingresa tus nombres.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    if (!apellidoP) {
        Swal.fire({
            icon: "warning",
            title: "Campo requerido",
            text: "Por favor, ingresa tu apellido paterno.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    if (!telefono) {
        Swal.fire({
            icon: "warning",
            title: "Campo requerido",
            text: "Por favor, ingresa tu número de teléfono.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    if (!correo) {
        Swal.fire({
            icon: "warning",
            title: "Campo requerido",
            text: "Por favor, ingresa tu correo electrónico.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(correo)) {
        Swal.fire({
            icon: "error",
            title: "Email inválido",
            text: "Por favor, ingresa un correo electrónico válido.",
            confirmButtonColor: "#ef233c"
        });
        return;
    }

    const servicioId = document.getElementById("service-select").value;
    const profesionalId = document.getElementById("pro-select").value;
    const tipoDocumento = document.getElementById("tipo-documento").value;
    const rutCliente = document.getElementById("rut-cliente").value.trim();
    const apellidoM = document.getElementById("apellido-materno").value.trim();
    const csrfToken = document.getElementById("csrf-token")?.value;

    if (btnOriginal) {
        btnOriginal.disabled = true;
        btnOriginal.innerText = "Procesando...";
    }

    Swal.fire({
        title: "Procesando reserva...",
        text: "Por favor espera",
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading()
    });

    fetch("/api/reservar/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken || ""
        },
        body: JSON.stringify({
            servicio_id: servicioId,
            profesional_id: profesionalId,
            fecha: fechaSeleccionada,
            hora: horaSeleccionada,
            rut_cliente: rutCliente,
            tipo_documento: tipoDocumento,
            nombres: nombres,
            apellido_paterno: apellidoP,
            apellido_materno: apellidoM,
            telefono: telefono,
            correo: correo
        })
    })
    .then(res => res.json())
    .then(data => {
        Swal.close();

        if (data.success) {
            // ✅ Mostrar opción de calificar
            Swal.fire({
                icon: "success",
                title: "¡Reserva confirmada!",
                text: "Tu cita fue agendada correctamente",
                showCancelButton: true,
                confirmButtonColor: "#4361ee",
                cancelButtonColor: "#6c757d",
                confirmButtonText: "⭐ Calificar experiencia",
                cancelButtonText: "Cerrar"
            }).then((result) => {
                if (result.isConfirmed) {
                    // Mostrar modal de calificación
                    mostrarModalCalificacion(data.reserva_id, nombres);
                } else {
                    window.location.href = "/reservar/";
                }
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "No se pudo reservar",
                text: data.error || "Error desconocido",
                confirmButtonColor: "#ef233c"
            });
            if (btnOriginal) resetBtnSafe(btnOriginal);
        }
    })
    .catch(err => {
        console.error(err);
        Swal.close();
        Swal.fire({
            icon: "error",
            title: "Error de conexión",
            text: "No se pudo conectar con el servidor",
            confirmButtonColor: "#ef233c"
        });
        if (btnOriginal) resetBtnSafe(btnOriginal);
    });
}

// ============================================
// Función para mostrar modal de calificación
// ============================================
function mostrarModalCalificacion(reservaId, nombreCliente) {
    let puntuacionSeleccionada = 0;
    
    Swal.fire({
        title: `¡Gracias ${nombreCliente.split(' ')[0]}!`,
        text: "¿Cómo calificarías tu experiencia?",
        html: `
            <div class="rating-modal">
                <div class="stars-container" style="display: flex; gap: 12px; justify-content: center; margin: 15px 0;">
                    <i class="far fa-star" data-rating="1" style="font-size: 35px; cursor: pointer; transition: all 0.2s; color: #e4e5e9;"></i>
                    <i class="far fa-star" data-rating="2" style="font-size: 35px; cursor: pointer; transition: all 0.2s; color: #e4e5e9;"></i>
                    <i class="far fa-star" data-rating="3" style="font-size: 35px; cursor: pointer; transition: all 0.2s; color: #e4e5e9;"></i>
                    <i class="far fa-star" data-rating="4" style="font-size: 35px; cursor: pointer; transition: all 0.2s; color: #e4e5e9;"></i>
                    <i class="far fa-star" data-rating="5" style="font-size: 35px; cursor: pointer; transition: all 0.2s; color: #e4e5e9;"></i>
                </div>
                <textarea id="comentario-calificacion" class="swal2-textarea" placeholder="Cuéntanos tu experiencia (opcional)" rows="3" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #ddd; font-family: inherit;"></textarea>
            </div>
        `,
        showCancelButton: true,
        confirmButtonColor: "#28a745",
        cancelButtonColor: "#6c757d",
        confirmButtonText: "⭐ Enviar calificación",
        cancelButtonText: "⏳ Ahora no",
        reverseButtons: false,
        customClass: {
            confirmButton: 'btn-calificar-confirm',
            cancelButton: 'btn-calificar-cancel'
        },
        preConfirm: () => {
            const comentario = document.getElementById("comentario-calificacion").value;
            if (puntuacionSeleccionada === 0) {
                Swal.showValidationMessage("⭐ Selecciona una calificación");
                return false;
            }
            return { puntuacion: puntuacionSeleccionada, comentario: comentario };
        },
        didOpen: () => {
            const stars = document.querySelectorAll(".stars-container i");
            
            function actualizarEstrellas(rating) {
                stars.forEach((star, index) => {
                    if (index < rating) {
                        star.className = "fas fa-star";
                        star.style.color = "#ffc107";
                    } else {
                        star.className = "far fa-star";
                        star.style.color = "#e4e5e9";
                    }
                });
            }
            
            stars.forEach(star => {
                star.addEventListener("mouseover", function() {
                    const rating = parseInt(this.dataset.rating);
                    actualizarEstrellas(rating);
                });
                
                star.addEventListener("click", function() {
                    puntuacionSeleccionada = parseInt(this.dataset.rating);
                    actualizarEstrellas(puntuacionSeleccionada);
                });
                
                star.addEventListener("mouseout", function() {
                    actualizarEstrellas(puntuacionSeleccionada);
                });
            });
        }
    }).then((result) => {
        if (result.isConfirmed && result.value) {
            // Enviar calificación
            fetch(`/api/enviar-resena/${reservaId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.getElementById("csrf-token")?.value || ""
                },
                body: JSON.stringify({
                    puntuacion: result.value.puntuacion,
                    comentario: result.value.comentario
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: "success",
                        title: "¡Gracias por tu opinión!",
                        text: "Tu calificación nos ayuda a mejorar",
                        confirmButtonColor: "#28a745",
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.href = "/reservar/";
                    });
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: data.error || "No se pudo enviar",
                        confirmButtonColor: "#dc3545",
                        confirmButtonText: "OK"
                    }).then(() => {
                        window.location.href = "/reservar/";
                    });
                }
            })
            .catch(() => {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: "No se pudo conectar",
                    confirmButtonColor: "#dc3545"
                }).then(() => {
                    window.location.href = "/reservar/";
                });
            });
        } else {
            window.location.href = "/reservar/";
        }
    });
}

function resetBtnSafe(btn) {
    btn.disabled = false;
    btn.innerText = "CONFIRMAR";
}


// ===============================
// BUSCAR CLIENTE POR RUT
// ===============================
function buscarCliente() {
    const rut = document.getElementById("rut-cliente").value.trim();

    if (!rut) return;

    fetch(`/api/cliente/?rut=${rut}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById("nombres-cliente").value = data.nombres || "";
                document.getElementById("apellido-paterno").value = data.apellido_paterno || "";
                document.getElementById("apellido-materno").value = data.apellido_materno || "";
                document.getElementById("telefono-cliente").value = data.telefono || "";
                document.getElementById("correo-cliente").value = data.correo || "";
            }
        })
        .catch(err => console.error(err));
}

// ===============================
// EVENTOS AUTOMÁTICOS
// ===============================
document.addEventListener("DOMContentLoaded", function () {
    const servicioSelect = document.getElementById("service-select");
    if (servicioSelect) {
        servicioSelect.addEventListener("change", actualizarInformacionServicio);
    }
    
    const rutInput = document.getElementById("rut-cliente");
    if (rutInput) {
        rutInput.addEventListener("input", function() {
            const rut = this.value.trim();
            if (rut.length >= 7) {
                buscarCliente();
            }
        });
    }
});

// ===============================
// NAVEGACIÓN ENTRE PASOS
// ===============================
function mostrarPaso(siguiente) {
    document.querySelectorAll(".paso").forEach(paso => {
        paso.classList.remove("activo");
    });
    const next = document.getElementById(siguiente);
    if (next) {
        next.classList.add("activo");
    }
}

function volverPaso1() {
    mostrarPaso("paso-1");
}

function volverPaso2() {
    mostrarPaso("paso-2");
}

function volverPaso3() {
    mostrarPaso("paso-3");
}


// Cargar correo guardado del localStorage
document.addEventListener('DOMContentLoaded', function() {
    const emailGuardado = localStorage.getItem('turnoclic_email');
    const correoInput = document.getElementById('correo-cliente');
    if (emailGuardado && correoInput) {
        correoInput.value = emailGuardado;
    }
});