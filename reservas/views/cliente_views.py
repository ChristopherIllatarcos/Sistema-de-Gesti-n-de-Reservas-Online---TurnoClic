from datetime import date, datetime
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from reservas.models import Mensaje, PerfilNegocio, Resena, Reserva, Disponibilidad
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# TODO: Mover perfil cliente aquí

#==================================================
# -------VISTA PARA MOSTRAR MIS CITAS--------------
#==================================================
from datetime import date

@login_required
def mis_citas(request):
    # Obtener el perfil del negocio del usuario logueado
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    
    if not perfil:
        messages.error(request, 'No tienes un negocio registrado')
        return redirect('dashboard')
    
    # ✅ Filtrar reservas SOLO del negocio y que NO hayan pasado (fecha >= hoy)
    hoy = date.today()
    reservas = Reserva.objects.filter(
        profesional__negocio=perfil,
        fecha__gte=hoy  # Solo reservas desde hoy en adelante
    ).order_by('fecha', 'hora')  # Orden ascendente (más cercanas primero)
    
    citas_hoy = reservas.filter(fecha=hoy).count()
    
    context = {
        'reservas': reservas,
        'citas_hoy': citas_hoy,
        'perfil': perfil,
    }
    
    return render(request, 'reservas/public/mis_citas.html', context)


#==================================================
# ----------- VISTA PARA VER RESERVA --------------   
#==================================================
@login_required
def ver_reserva(request, id):
    # Obtener el perfil del negocio del usuario
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    
    if not perfil:
        raise Http404("No tienes un negocio registrado")
    
    # Verificar que la reserva pertenezca al negocio del usuario
    reserva = get_object_or_404(
        Reserva, 
        id=id, 
        profesional__negocio=perfil  # Filtra por negocio
    )
    
    context = {
        "reserva": reserva,
        "perfil": perfil,
    }
    
    return render(request, "reservas/public/ver_reserva.html", context)


#==================================================
# --------- VISTA PARA ELIMINAR RESERVA -----------    
#==================================================
@login_required
def eliminar_reserva(request, id):
    perfil = request.user.perfil
    
    # Obtener la reserva antes de eliminar
    reserva = get_object_or_404(Reserva, id=id, profesional__negocio=perfil)
    
    # Liberar la hora en disponibilidad
    Disponibilidad.objects.filter(
        profesional=reserva.profesional,
        fecha=reserva.fecha,
        hora=reserva.hora
    ).update(esta_libre=True)
    
    # Eliminar reserva
    reserva.delete()
    
    messages.success(request, "Reserva eliminada correctamente")
    return redirect('dashboard')


#==================================================
# ----------VISTA PARA ENVIAR MENSAJES-------------
#================================================== 
@login_required
def mensajes(request):
    perfil = request.user.perfil
    
    mensajes = Mensaje.objects.filter(
        negocio=perfil,
        archivado=False
    ).order_by("-creado_en")
    
    return render(request, "reservas/panel/mensajes.html", {
        "mensajes": mensajes,
        "mensajes_count": mensajes.filter(leido=False).count()
    })


#==================================================
# ----------- VISTA PARA ARCHIVAR MENSAJES --------
#==================================================
@login_required
def archivar_mensaje(request, id):
    perfil = request.user.perfil
    
    Mensaje.objects.filter(
        id=id,
        negocio=perfil
    ).update(archivado=True)
    
    messages.success(request, "Mensaje archivado correctamente")
    return redirect('mensajes')


#==================================================
# --------- VISTA PARA LIMPIAR RESERVAS -----------
#==================================================
@login_required
def limpiar_reservas_pasadas(request):
    if request.method == 'POST':
        try:
            perfil = request.user.perfil
            hoy = date.today()
            
            reservas_pasadas = Reserva.objects.filter(
                profesional__negocio=perfil,
                fecha__lt=hoy
            )
            count = reservas_pasadas.count()
            
            if count > 0:
                reservas_pasadas.delete()
                return JsonResponse({
                    'success': True,
                    'message': f'{count} reservas pasadas eliminadas correctamente'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'No hay reservas pasadas para eliminar'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


#==================================================
# --------- VISTA PARA ENVIAR RESENAS -------------
#==================================================
@csrf_exempt
def enviar_resena(request, reserva_id):
    """Cliente envía reseña después de una reserva"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        import json
        data = json.loads(request.body)
        
        from reservas.models import Reserva, Resena
        from datetime import date
        
        reserva = get_object_or_404(Reserva, id=reserva_id)
        
        # Verificar si ya existe reseña
        if Resena.objects.filter(reserva=reserva).exists():
            return JsonResponse({'success': False, 'error': 'Ya calificaste esta reserva'})
        
        # Verificar que la reserva no sea futura
        if reserva.fecha > date.today():
             return JsonResponse({'success': False, 'error': 'Aún no puede calificar. Vuelve después de tu cita.'})
        
        if reserva.fecha == date.today():
            hora_actual = datetime.now().time()
            if reserva.hora > hora_actual:
                return JsonResponse({'success': False, 'error': 'Aún no puede calificar. Vuelve luego de tu cita.'})
        
        puntuacion = data.get('puntuacion')
        comentario = data.get('comentario', '')
        
        # Validar puntuación
        if not puntuacion or puntuacion < 1 or puntuacion > 5:
            return JsonResponse({'success': False, 'error': 'Puntuación inválida'})
        
        # Crear reseña
        resena = Resena.objects.create(
            reserva=reserva,
            cliente=reserva.cliente,
            negocio=reserva.profesional.negocio,
            puntuacion=puntuacion,
            comentario=comentario
        )
        
        print(f"✅ Reseña creada: {resena.id} - {puntuacion} estrellas")
        
        return JsonResponse({'success': True, 'message': 'Gracias por tu calificación'})
        
    except Exception as e:
        print(f"❌ Error en reseña: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)})