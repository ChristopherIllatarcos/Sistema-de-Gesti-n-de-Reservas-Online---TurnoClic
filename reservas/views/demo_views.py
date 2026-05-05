from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils import timezone

from reservas.models import PerfilNegocio, SolicitudDemo

# Obtener modelo de usuario
User = get_user_model()


#=============================================================================
#====================== VISTA PARA SOLICITAR DEMO ============================
#=============================================================================
@csrf_exempt
def solicitar_demo(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')
        rubro = request.POST.get('rubro_seleccionado')
        tipo_servicio = request.POST.get('tipo_servicio')
        slug_negocio = request.POST.get('slug_negocio')
        
        nombre_completo = f"{nombre} {apellidos}"
        
        # Validar email único
        if User.objects.filter(email=email).exists():
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Este correo ya está registrado.'})
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('solicitar_demo')
        
        # Validar slug único
        if PerfilNegocio.objects.filter(slug=slug_negocio).exists():
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Este nombre de negocio ya está en uso.'})
            messages.error(request, 'Este nombre de negocio ya está en uso.')
            return redirect('solicitar_demo')
        
        try:
            # 1. Crear usuario (inactivo)
            usuario = User.objects.create_user(
                email=email,
                first_name=nombre,
                last_name=apellidos,
                password=password,
                is_active=False
            )
            print(f"✅ Usuario creado: {usuario.id}")
            
            # 2. Crear perfil de negocio (inactivo)
            perfil = PerfilNegocio.objects.create(
                usuario=usuario,
                nombre_negocio=nombre_completo,
                telefono=telefono,
                slug=slug_negocio,
                rubro=rubro,
                activo=False,
                fecha_expiracion=timezone.now() + timedelta(days=14)
            )
            print(f"✅ Perfil creado: {perfil.slug}")
            
            # 3. Guardar solicitud demo
            try:
                SolicitudDemo.objects.create(
                    nombre=nombre_completo,
                    email=email,
                    telefono=telefono,
                    mensaje=f"Rubro: {rubro}\nServicio: {tipo_servicio}\nSlug: {slug_negocio}"
                )
                print("✅ Solicitud demo guardada")
            except Exception as e:
                print(f"❌ Error guardando solicitud: {e}")
            
            # 4. Generar token de activación
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)
            activation_link = request.build_absolute_uri(f'/activar-demo/{uid}/{token}/')
            
            # 5. Enviar correo de activación
            send_mail(
                subject='🎉 Activa tu cuenta - TURNOCLIC',
                message=f"""
Hola {nombre_completo},

¡Gracias por solicitar tu demo de TURNOCLIC!

Para activar tu cuenta, haz clic en el siguiente enlace:

🔗 {activation_link}

Tu negocio estará activo por 14 días de prueba.

URL de tu negocio: https://{slug_negocio}.turnoclic.cl

¡Saludos!
El equipo de TURNOCLIC
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            success_msg = f"¡Bienvenido {nombre}! Te hemos enviado un correo a {email} para activar tu cuenta."
            
            if is_ajax:
                return JsonResponse({'success': True, 'message': success_msg})
            
            messages.success(request, success_msg)
            return redirect('home')
            
        except Exception as e:
            print(f"❌ Error: {e}")
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error: {str(e)}")
            return redirect('solicitar_demo')
    
    return render(request, 'reservas/demo/solicitar_demo.html')


#=============================================================================
#====================== VISTA PARA ACTIVAR CUENTA DEMO =======================
#=============================================================================
def activar_demo(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(usuario, token):
            # Activar usuario
            usuario.is_active = True
            usuario.save()
            
            # Activar negocio
            perfil = usuario.perfil
            perfil.activo = True
            perfil.save()
            
            messages.success(request, "¡Cuenta activada exitosamente! Ya puedes iniciar sesión y configurar tu negocio.")
            return redirect('login')
        else:
            messages.error(request, "El enlace de activación es inválido o ha expirado.")
            return redirect('home')
            
    except Exception as e:
        print(f"Error en activar_demo: {e}")
        messages.error(request, "Error al activar la cuenta.")
        return redirect('home')
    
 
 
 #=============================================================================
#====================== VISTA PARA GUARDAR SOLICITUD DEMO =====================
#=============================================================================   
@csrf_exempt
def guardar_solicitud_demo(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')
        rubro = request.POST.get('rubro_seleccionado')
        tipo_servicio = request.POST.get('tipo_servicio')
        slug_negocio = request.POST.get('slug_negocio')
        
        nombre_completo = f"{nombre} {apellidos}"
        
        print("=== DEBUG GUARDAR SOLICITUD DEMO ===")
        print(f"Email: {email}")
        print(f"Slug: {slug_negocio}")
        
        # Validar email
        if User.objects.filter(email=email).exists():
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Este correo ya está registrado.'})
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('solicitar_demo')
        
        # Validar slug
        if PerfilNegocio.objects.filter(slug=slug_negocio).exists():
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Este nombre de negocio ya está en uso.'})
            messages.error(request, 'Este nombre de negocio ya está en uso.')
            return redirect('solicitar_demo')
        
        try:
            # Crear usuario
            print("📝 Creando usuario...")
            usuario = User.objects.create_user(
                email=email,
                first_name=nombre,
                last_name=apellidos,
                password=password,
                is_active=False
            )
            print(f"✅ Usuario creado ID: {usuario.id}")
            
            # Crear o actualizar perfil
            perfil, created = PerfilNegocio.objects.get_or_create(
                usuario=usuario,
                defaults={
                    'nombre_negocio': nombre_completo,
                    'telefono': telefono,
                    'slug': slug_negocio,
                    'rubro': rubro,
                    'activo': False,
                    'fecha_expiracion': timezone.now() + timedelta(days=14)
                }
            )
            
            if created:
                print(f"✅ Perfil creado con ID: {perfil.id}")
            else:
                print(f"⚠️ El perfil ya existía, actualizando...")
                perfil.nombre_negocio = nombre_completo
                perfil.telefono = telefono
                perfil.slug = slug_negocio
                perfil.rubro = rubro
                perfil.save()
                print(f"✅ Perfil actualizado")
            
            # Guardar solicitud demo
            SolicitudDemo.objects.create(
                nombre=nombre_completo,
                email=email,
                telefono=telefono,
                mensaje=f"Rubro: {rubro}\nServicio: {tipo_servicio}\nSlug: {slug_negocio}"
            )
            print("✅ Solicitud demo guardada")
            
            # Generar token
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)
            domain = "127.0.0.1:8000"
            activation_link = f"http://{domain}/activar-demo/{uid}/{token}/"
            
            # Enviar correo
            try:
                send_mail(
                    subject='🎉 Activa tu cuenta - TURNOCLIC',
                    message=f"Hola {nombre_completo},\n\nActiva tu cuenta: {activation_link}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                print("✅ Correo enviado")
            except Exception as e:
                print(f"❌ Error correo: {e}")
            
            success_msg = f"¡Bienvenido {nombre}! Te hemos enviado un correo a {email}"
            
            if is_ajax:
                return JsonResponse({'success': True, 'message': success_msg})
            
            messages.success(request, success_msg)
            return redirect('home')
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error: {str(e)}")
            return redirect('solicitar_demo')
    
    return redirect('solicitar_demo')