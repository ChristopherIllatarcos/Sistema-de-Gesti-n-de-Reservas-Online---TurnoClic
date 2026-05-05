from datetime import date, datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings  # ✅ Corregido: from django.conf import settings
from reservas.models import Cliente, Disponibilidad, PerfilNegocio, Profesional, Reserva, Servicio
from django.contrib.auth.decorators import login_required
# TODO: Mover funciones de reservas aquí

#=============================================================================
#====================== FUNCIÓN PARA ENVIAR CORREO DE RESERVA ================
#=============================================================================
def enviar_correo_reserva(email, nombres, fecha, hora, servicio, profesional, negocio=None, reserva_id=None):
    asunto = "🎟️ Confirmación de tu reserva"
    
    # URL para calificar (si se proporciona reserva_id)
    url_calificar = f"http://127.0.0.1:8000/reserva/{reserva_id}/" if reserva_id else "#"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; background:#f4f4f4; padding:20px;">
        <div style="max-width:600px; margin:auto; background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.1);">

            <div style="background:#111; color:#fff; padding:20px; text-align:center;">
                <h2 style="margin:0;">Tu Reserva ha sido Confirmada</h2>
                <p style="margin:5px 0; font-size:14px;">Sistema de Agendamiento</p>
            </div>

            <div style="padding:20px;">

                <p>Hola <b>{nombres}</b>,</p>
                <p>Te confirmamos tu reserva con los siguientes detalles:</p>

                <div style="background:#f9f9f9; padding:15px; border-radius:10px; margin:15px 0;">
                    <p><b>📅 Fecha:</b> {fecha}</p>
                    <p><b>⏰ Hora:</b> {hora}</p>
                    <p><b>💈 Servicio:</b> {servicio}</p>
                    <p><b>👤 Profesional:</b> {profesional}</p>
                </div>

                <div style="text-align:center; margin:20px 0;">
                    <a href="{url_calificar}" style="background: #4361ee; color: white; padding: 10px 20px; text-decoration: none; border-radius: 30px; display: inline-block;">
                        ⭐ Calificar mi experiencia
                    </a>
                </div>

                <div style="text-align:center; margin-top:20px;">
                    <p style="font-size:13px; color:#666;">
                        Guarda este correo como comprobante de tu reserva
                    </p>
                </div>

            </div>

            <div style="background:#111; color:#fff; text-align:center; padding:10px; font-size:12px;">
                © Tu Sistema de Reservas
            </div>

        </div>
    </div>
    """

    msg = EmailMultiAlternatives(
        asunto,
        "Tu reserva ha sido confirmada",
        settings.EMAIL_HOST_USER,
        [email]
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print(f"✅ Correo de reserva enviado a {email}")

#==================================================
# --------- VISTA PARA AGENDAR RESERVA -----------
#==================================================
def reservar(request):
    # Primero intentar con subdominio
    host = request.get_host()
    subdominio = host.split('.')[0]
    
    # Si es localhost o no hay subdominio válido, usar parámetro GET
    if subdominio in ['127', 'localhost', 'lvh', 'www', '127.0.0.1']:
        subdominio = request.GET.get('negocio')
        
        # Si no hay parámetro, mostrar página de selección
        if not subdominio:
            negocios = PerfilNegocio.objects.all()
            return render(request, 'reservas/public/seleccionar_negocio.html', {'negocios': negocios})
    
    perfil = PerfilNegocio.objects.filter(slug=subdominio).first()
    
    if not perfil:
        return render(request, 'reservas/public/negocio_no_encontrado.html', {
            'subdominio': subdominio
        })
    
    servicios = Servicio.objects.filter(negocio=perfil)
    profesionales = Profesional.objects.filter(negocio=perfil)
    
    context = {
        'perfil': perfil,
        'servicios': servicios,
        'profesionales': profesionales,
    }
    
    return render(request, 'reservas/public/agendar.html', context)


#==========================================================================================
#====================== VISTA PARA CREAR UNA RESERVA (PÚBLICA) ============================
#==========================================================================================
@csrf_exempt
def crear_reserva(request):

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        import json
        from datetime import datetime

        data = json.loads(request.body)

        servicio_id = data.get("servicio_id")
        profesional_id = data.get("profesional_id")
        fecha = data.get("fecha")
        hora = data.get("hora")

        rut_cliente = data.get("rut_cliente")
        tipo_documento = data.get("tipo_documento", "rut")

        nombres = data.get("nombres")
        apellido_paterno = data.get("apellido_paterno")
        apellido_materno = data.get("apellido_materno")
        telefono = data.get("telefono")
        correo = data.get("correo")

        # =========================
        # VALIDACIÓN BÁSICA
        # =========================
        if not all([servicio_id, profesional_id, fecha, hora, rut_cliente]):
            return JsonResponse({"error": "Faltan datos obligatorios"}, status=400)

        if not correo:
            return JsonResponse({"error": "El correo del cliente es obligatorio"}, status=400)

        # =========================
        # DETECTAR SUBDOMINIO Y NEGOCIO
        # =========================
        host = request.get_host()
        subdominio = host.split('.')[0]
        
        perfil = PerfilNegocio.objects.filter(slug=subdominio).first()
        
        if not perfil:
            return JsonResponse({"error": "Negocio no encontrado"}, status=404)

        # =========================
        # OBTENER OBJETOS
        # =========================
        servicio = Servicio.objects.get(id=servicio_id, negocio=perfil)
        profesional = Profesional.objects.get(id=profesional_id, negocio=perfil)

        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(hora, "%H:%M").time()

        # =========================
        # VALIDAR DISPONIBILIDAD
        # =========================
        bloque = Disponibilidad.objects.filter(
            profesional=profesional,
            fecha=fecha_obj,
            hora=hora_obj,
            esta_libre=True
        ).first()

        if not bloque:
            return JsonResponse({"error": "La hora ya no está disponible"}, status=400)

        # =========================
        # CLIENTE (CREAR O ACTUALIZAR)
        # =========================
        cliente, created = Cliente.objects.get_or_create(
            rut=rut_cliente
        )

        cliente.nombres = nombres or ""
        cliente.apellido_paterno = apellido_paterno or ""
        cliente.apellido_materno = apellido_materno or ""
        cliente.telefono = telefono or ""
        cliente.correo = correo or ""
        cliente.save()

        # =========================
        # CREAR RESERVA
        # =========================
        reserva = Reserva.objects.create(
            servicio=servicio,
            profesional=profesional,
            cliente=cliente,
            fecha=fecha_obj,
            hora=hora_obj,
            rut_cliente=rut_cliente,
            tipo_documento=tipo_documento,
            nombre_cliente=nombres or "",
            telefono_cliente=telefono or "",
            negocio=perfil
        )
        
        # =========================
        # GANAR PUNTOS
        # =========================
        puntos_ganados = int(servicio.precio / 1000)
        cliente.puntos += puntos_ganados
        cliente.save()
        print(f"Cliente {cliente.nombres} ganó {puntos_ganados} puntos")

        # =========================
        # BLOQUEAR HORA
        # =========================
        bloque.esta_libre = False
        bloque.save()

        # =========================
        # CORREO DE CONFIRMACIÓN AL CLIENTE
        # =========================
        try:
            enviar_correo_reserva(
                email=correo,
                nombres=nombres or "Cliente",
                fecha=str(fecha_obj),
                hora=str(hora_obj),
                servicio=servicio.nombre,
                profesional=str(profesional),
                reserva_id=reserva.id
            )
            print(f"✅ Correo enviado a {correo}")
        except Exception as e:
            print("ERROR ENVÍO CORREO:", e)

        # =========================
        # CORREO AL ADMINISTRADOR DEL NEGOCIO
        # =========================
        try:
            send_mail(
                subject=f'📋 Nueva reserva - {perfil.nombre_negocio}',
                message=f"""
NUEVA RESERVA

Negocio: {perfil.nombre_negocio}
Cliente: {nombres} {apellido_paterno}
Email: {correo}
Teléfono: {telefono}
Servicio: {servicio.nombre}
Profesional: {profesional}
Fecha: {fecha_obj}
Hora: {hora_obj}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[perfil.usuario.email] if perfil.usuario.email else ['admin@turnoclic.cl'],
                fail_silently=True,
            )
        except Exception as e:
            print(f"ERROR CORREO ADMIN: {e}")

        return JsonResponse({
            "success": True,
            "reserva_id": reserva.id
        })

    except Servicio.DoesNotExist:
        return JsonResponse({"error": "Servicio no encontrado"}, status=404)
    except Profesional.DoesNotExist:
        return JsonResponse({"error": "Profesional no encontrado"}, status=404)
    except Exception as e:
        print(f"ERROR GENERAL: {e}")
        return JsonResponse({"error": str(e)}, status=500)
    
    
#=============================================================================================================    
#====================== VISTA PARA OBTENER LA DISPONIBILIDAD DE LOS PROFESIONALES ============================
#=============================================================================================================    
def obtener_disponibilidad(request):
    profesional_id = request.GET.get('profesional_id')
    
    if not profesional_id:
        return JsonResponse({'fechas_disponibles': []})

    fechas_disponibles = Disponibilidad.objects.filter(
        profesional_id=profesional_id,
        esta_libre=True,
        fecha__gte=date.today()
    ).values_list('fecha', flat=True).distinct().order_by('fecha')
    
    lista_fechas = [f.strftime('%Y-%m-%d') for f in fechas_disponibles]
    
    print(f"--- Datos encontrados para prof {profesional_id}: {lista_fechas} ---")
    
    return JsonResponse({'fechas_disponibles': lista_fechas})


#===========================================================================================================================
#====================== VISTA PARA OBTENER LAS HORAS DISPONIBLES DE UN PROFESIONAL EN UNA FECHA ============================
#===========================================================================================================================
def obtener_horas(request):
    profesional_id = request.GET.get('profesional_id')
    fecha = request.GET.get('fecha')

    if not profesional_id or not fecha:
        return JsonResponse({'horas_disponibles': []})

    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()

    bloques = Disponibilidad.objects.filter(
        profesional_id=profesional_id,
        fecha=fecha_obj,
        esta_libre=True
    ).order_by('hora')

    horas_list = [b.hora.strftime('%H:%M') for b in bloques]

    print("HORAS ENCONTRADAS:", horas_list)

    return JsonResponse({'horas_disponibles': horas_list})


#=============================================================================================================================  
#====================== VISTA PARA OBTENER DATOS DE CLIENTE EXISTENTE EN EL FORMULARIO DE RESERVA ============================
#=============================================================================================================================       
def obtener_cliente_por_rut(request):
    rut = request.GET.get("rut")

    try:
        cliente = Cliente.objects.get(rut=rut)

        return JsonResponse({
            "success": True,
            "nombres": cliente.nombres,
            "apellido_paterno": cliente.apellido_paterno,
            "apellido_materno": cliente.apellido_materno,
            "telefono": cliente.telefono,
            "correo": cliente.correo
        })

    except Cliente.DoesNotExist:
        return JsonResponse({"success": False})
    
    
#=========================================
# VISTA PARA CANJEAR PUNTOS POR DESCUENTOS
#=======================================
@login_required
def canjear_puntos(request):
    """Cliente canjea sus puntos por descuentos"""
    if request.method == 'POST':
        rut = request.POST.get('rut')
        puntos_a_canjear = int(request.POST.get('puntos', 0))
        
        cliente = get_object_or_404(Cliente, rut=rut)
        
        if cliente.puntos >= puntos_a_canjear:
            # Calcular descuento (100 puntos = $1000)
            descuento = (puntos_a_canjear / 100) * 1000
            
            cliente.puntos -= puntos_a_canjear
            cliente.save()
            
            return JsonResponse({
                'success': True,
                'descuento': descuento,
                'puntos_restantes': cliente.puntos
            })
        else:
            return JsonResponse({'success': False, 'error': 'Puntos insuficientes'})
    
    return JsonResponse({'error': 'Método no permitido'})