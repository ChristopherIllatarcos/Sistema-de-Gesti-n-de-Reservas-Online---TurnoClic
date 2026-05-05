import json
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from reservas.models import Disponibilidad, PerfilNegocio, Profesional, Resena, Servicio

# TODO: Mover CRUDs aquí

# ==================== GESTIÓN DE SERVICIOS ====================
@login_required
def lista_servicios(request):
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    if not perfil:
        messages.error(request, 'No tienes un negocio registrado')
        return redirect('dashboard')
    
    servicios = Servicio.objects.filter(negocio=perfil)
    return render(request, 'reservas/gestion/servicios.html', {
        'servicios': servicios,
        'perfil': perfil
    })
    

#=======================================
#-------CREAR SERVICIO-----------------
#=======================================
@login_required
def crear_servicio(request):
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    if not perfil:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No tienes un negocio registrado'})
        return redirect('dashboard')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        duracion = request.POST.get('duracion')
        descripcion = request.POST.get('descripcion')
        
        if not nombre:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'El nombre del servicio es obligatorio'})
            messages.error(request, 'El nombre del servicio es obligatorio')
            return redirect('crear_servicio')
        
        if not precio or int(precio) <= 0:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Ingresa un precio válido'})
            messages.error(request, 'Ingresa un precio válido')
            return redirect('crear_servicio')
        
        if not duracion or int(duracion) <= 0:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Ingresa una duración válida'})
            messages.error(request, 'Ingresa una duración válida')
            return redirect('crear_servicio')
        
        try:
            servicio = Servicio.objects.create(
                nombre=nombre,
                precio=precio,
                duracion_minutos=duracion,
                descripcion=descripcion,
                negocio=perfil
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Servicio {nombre} creado correctamente',
                    'servicio': {
                        'id': servicio.id,
                        'nombre': servicio.nombre,
                        'precio': servicio.precio,
                        'duracion': servicio.duracion_minutos
                    }
                })
            
            messages.success(request, f'Servicio {nombre} creado correctamente')
            return redirect('lista_servicios')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Error: {str(e)}')
            return redirect('crear_servicio')
    
    return render(request, 'reservas/gestion/crear_servicio.html', {'perfil': perfil})


#=======================================
#-------EDITAR SERVICIO-----------------
#=======================================
@login_required
def editar_servicio(request, id):
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    if not perfil:
        return redirect('dashboard')
    
    servicio = get_object_or_404(Servicio, id=id, negocio=perfil)
    
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            precio = request.POST.get('precio')
            duracion = request.POST.get('duracion')
            descripcion = request.POST.get('descripcion')
            
            if not nombre:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'El nombre es requerido'})
                messages.error(request, 'El nombre es requerido')
                return redirect('editar_servicio', id=id)
            
            if not precio or float(precio) <= 0:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Precio inválido'})
                messages.error(request, 'Precio inválido')
                return redirect('editar_servicio', id=id)
            
            if not duracion or int(duracion) <= 0:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Duración inválida'})
                messages.error(request, 'Duración inválida')
                return redirect('editar_servicio', id=id)
            
            servicio.nombre = nombre
            servicio.precio = precio
            servicio.duracion_minutos = duracion
            servicio.descripcion = descripcion
            servicio.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Servicio {nombre} actualizado correctamente'
                })
            
            messages.success(request, f'Servicio {nombre} actualizado correctamente')
            return redirect('lista_servicios')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Error: {str(e)}')
            return redirect('editar_servicio', id=id)
    
    return render(request, 'reservas/gestion/editar_servicio.html', {
        'servicio': servicio,
        'perfil': perfil
    })


#============================
#---- ELIMINAR SERVICIO ----
#============================
@login_required
def eliminar_servicio(request, id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
        if not perfil:
            return JsonResponse({'success': False, 'error': 'No tienes un negocio registrado'})
        
        servicio = get_object_or_404(Servicio, id=id, negocio=perfil)
        nombre = servicio.nombre
        servicio.delete()
        
        return JsonResponse({'success': True, 'message': f'Servicio {nombre} eliminado'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    
#==========================================
#-------OBTENER SERVICIO-------------------
#==========================================
@login_required
def obtener_servicio(request, id):
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    if not perfil:
        return JsonResponse({'success': False, 'error': 'No tienes un negocio registrado'})
    
    servicio = get_object_or_404(Servicio, id=id, negocio=perfil)
    
    return JsonResponse({
        'success': True,
        'servicio': {
            'id': servicio.id,
            'nombre': servicio.nombre,
            'precio': servicio.precio,
            'duracion': servicio.duracion_minutos,
            'descripcion': servicio.descripcion
        }
    })
    
    
#=================================================================
# ==================== LISTA DE PROFESIONALES ====================
#=================================================================
@login_required
def lista_profesionales(request):
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    if not perfil:
        messages.error(request, 'No tienes un negocio registrado')
        return redirect('dashboard')
    
    profesionales = Profesional.objects.filter(negocio=perfil)
    total = profesionales.count()
    activos = profesionales.filter(activo=True).count()
    inactivos = profesionales.filter(activo=False).count()
    
    context = {
        'profesionales': profesionales,
        'perfil': perfil,
        'total_profesionales': total,
        'activos': activos,
        'inactivos': inactivos,
    }
    return render(request, 'reservas/gestion/profesionales.html', context)


#===================================================================
#=================== CREAR PROFESIONALES ===========================
#===================================================================
@login_required
def crear_profesional(request):
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    if not perfil:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No tienes un negocio registrado'})
        return redirect('dashboard')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        especialidad = request.POST.get('especialidad')
        activo = request.POST.get('activo') == 'on'
        
        if not nombre:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'El nombre es requerido'})
            messages.error(request, 'El nombre es requerido')
            return redirect('crear_profesional')
        
        profesional = Profesional.objects.create(
            nombre=nombre,
            especialidad=especialidad,
            negocio=perfil,
            activo=activo
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'profesional': {
                    'id': profesional.id,
                    'nombre': profesional.nombre,
                    'especialidad': profesional.especialidad
                }
            })
        
        messages.success(request, f'¡Profesional {nombre} creado exitosamente!')
        return redirect('lista_profesionales')
    
    return render(request, 'reservas/gestion/crear_profesional.html', {'perfil': perfil})


#========================================================================
#=================== EDITAR PROFESIONALES ===========================
#========================================================================
@login_required
def editar_profesional(request, id):
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    if not perfil:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No tienes un negocio registrado'})
        return redirect('dashboard')
    
    profesional = get_object_or_404(Profesional, id=id, negocio=perfil)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        especialidad = request.POST.get('especialidad')
        activo = request.POST.get('activo') == 'on'
        
        if not nombre:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'El nombre es requerido'})
            messages.error(request, 'El nombre es requerido')
            return redirect('editar_profesional', id=id)
        
        profesional.nombre = nombre
        profesional.especialidad = especialidad
        profesional.activo = activo
        profesional.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Profesional {nombre} actualizado correctamente',
                'profesional': {
                    'id': profesional.id,
                    'nombre': profesional.nombre,
                    'especialidad': profesional.especialidad,
                    'activo': profesional.activo
                }
            })
        
        messages.success(request, f'Profesional {nombre} actualizado correctamente')
        return redirect('lista_profesionales')
    
    return render(request, 'reservas/gestion/editar_profesional.html', {
        'profesional': profesional,
        'perfil': perfil
    })
    

#========================================================================
#=================== ELIMINAR PROFESIONALES =============================
#========================================================================
@login_required
def eliminar_profesional(request, id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
        profesional = get_object_or_404(Profesional, id=id, negocio=perfil)
        nombre = profesional.nombre
        profesional.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Profesional {nombre} eliminado'})
        
        messages.success(request, f'Profesional {nombre} eliminado')
        return redirect('lista_profesionales')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f'Error: {str(e)}')
        return redirect('lista_profesionales')


#==========================================
#-------TOGGLE PROFESIONAL-----------------
#==========================================
@login_required
def toggle_profesional(request, id):
    if request.method == 'POST':
        try:
            perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
            profesional = get_object_or_404(Profesional, id=id, negocio=perfil)
            
            data = json.loads(request.body)
            profesional.activo = data.get('activo', False)
            profesional.save()
            
            return JsonResponse({'success': True, 'activo': profesional.activo})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


#==========================================
#-------LISTA HORARIOS---------------------
#==========================================    
@login_required
def lista_horarios(request):
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    if not perfil:
        messages.error(request, 'No tienes un negocio registrado')
        return redirect('dashboard')
    
    profesionales = Profesional.objects.filter(negocio=perfil, activo=True)
    horarios = Disponibilidad.objects.filter(profesional__negocio=perfil).order_by('-fecha', 'hora')
    
    context = {
        'perfil': perfil,
        'profesionales': profesionales,
        'horarios': horarios,
    }
    return render(request, 'reservas/gestion/horarios.html', context)


#==========================================
#-------CREAR HORARIO----------------------
#==========================================
@login_required
def crear_horario(request):
    if request.method == 'POST':
        try:
            perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
            if not perfil:
                return JsonResponse({'success': False, 'error': 'No tienes un negocio registrado'})
            
            profesional_id = request.POST.get('profesional_id')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            esta_libre = request.POST.get('esta_libre') == 'on'
            
            if not profesional_id:
                return JsonResponse({'success': False, 'error': 'Debes seleccionar un profesional'})
            if not fecha:
                return JsonResponse({'success': False, 'error': 'Debes seleccionar una fecha'})
            if not hora:
                return JsonResponse({'success': False, 'error': 'Debes seleccionar una hora'})
            
            profesional = get_object_or_404(Profesional, id=int(profesional_id), negocio=perfil)
            
            disponibilidad, created = Disponibilidad.objects.get_or_create(
                profesional=profesional,
                fecha=fecha,
                hora=hora,
                defaults={'esta_libre': esta_libre}
            )
            
            if not created:
                disponibilidad.esta_libre = esta_libre
                disponibilidad.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Horario guardado correctamente'})
            
            messages.success(request, 'Horario guardado correctamente')
            return redirect('lista_horarios')
            
        except Exception as e:
            print(f"Error: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Error: {str(e)}')
            return redirect('lista_horarios')
    
    return redirect('lista_horarios')


#==========================================
#-------EDITAR HORARIO---------------------
#==========================================
@login_required
def editar_horario(request, id):
    if request.method == 'POST':
        try:
            perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
            if not perfil:
                return JsonResponse({'success': False, 'error': 'No tienes un negocio registrado'})
            
            horario = get_object_or_404(Disponibilidad, id=id, profesional__negocio=perfil)
            
            profesional_id = request.POST.get('profesional_id')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            esta_libre = request.POST.get('esta_libre') == 'on'
            
            horario.profesional_id = profesional_id
            horario.fecha = fecha
            horario.hora = hora
            horario.esta_libre = esta_libre
            horario.save()
            
            return JsonResponse({'success': True, 'message': 'Horario actualizado correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)     


#==========================================
#-------ELIMINAR HORARIO--------------------
#==========================================
@login_required
def eliminar_horario(request, id):
    if request.method == 'POST':
        try:
            perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
            horario = get_object_or_404(Disponibilidad, id=id, profesional__negocio=perfil)
            horario.delete()
            return JsonResponse({'success': True, 'message': 'Horario eliminado correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


#==========================================
#-------OBTENER HORARIO--------------------
#==========================================
@login_required
def obtener_horario(request, id):
    try:
        perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
        if not perfil:
            return JsonResponse({'success': False, 'error': 'No tienes un negocio registrado'})
        
        horario = get_object_or_404(Disponibilidad, id=id, profesional__negocio=perfil)
        
        return JsonResponse({
            'success': True,
            'horario': {
                'id': horario.id,
                'profesional_id': horario.profesional.id,
                'fecha': horario.fecha.strftime('%Y-%m-%d'),
                'hora': horario.hora.strftime('%H:%M'),
                'esta_libre': horario.esta_libre
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


#==========================================
#-------EDITAR NEGOCIO---------------------    
#==========================================
@login_required
def editar_negocio(request):
    perfil = request.user.perfil
    if request.method == 'POST':
        perfil.nombre_negocio = request.POST.get('nombre_negocio')
        perfil.descripcion = request.POST.get('descripcion')
        perfil.rubro = request.POST.get('rubro')
        perfil.slug = request.POST.get('slug')
        perfil.telefono = request.POST.get('telefono')
        perfil.direccion = request.POST.get('direccion')
        perfil.instagram = request.POST.get('instagram')
        perfil.whatsapp = request.POST.get('whatsapp')
        
        if PerfilNegocio.objects.exclude(id=perfil.id).filter(slug=perfil.slug).exists():
            messages.error(request, 'Este slug ya está en uso. Elige otro.')
            return redirect('editar_negocio')
        
        perfil.save()
        messages.success(request, 'Negocio actualizado correctamente')
        return redirect('dashboard')
    
    return render(request, 'reservas/gestion/editar_negocio.html', {'perfil': perfil})



@login_required
def lista_resenas(request):
    """Lista de reseñas del negocio"""
    perfil = PerfilNegocio.objects.filter(usuario=request.user).first()
    
    if not perfil:
        messages.error(request, 'No tienes un negocio registrado')
        return redirect('dashboard')
    
    resenas = Resena.objects.filter(negocio=perfil).order_by('-fecha_creacion')
    
    # Calcular promedio
    promedio = 0
    if resenas.exists():
        promedio = sum(r.puntuacion for r in resenas) / resenas.count()
    
    # Distribución de estrellas
    distribucion = {
        5: resenas.filter(puntuacion=5).count(),
        4: resenas.filter(puntuacion=4).count(),
        3: resenas.filter(puntuacion=3).count(),
        2: resenas.filter(puntuacion=2).count(),
        1: resenas.filter(puntuacion=1).count(),
    }
    
    context = {
        'perfil': perfil,
        'resenas': resenas,
        'total_resenas': resenas.count(),
        'promedio': round(promedio, 1),
        'distribucion': distribucion,
    }
    
    return render(request, 'reservas/gestion/resenas.html', context)