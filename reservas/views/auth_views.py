from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from datetime import timedelta, date
from django.utils import timezone

from reservas.models import Usuario, PerfilNegocio  # Usa Usuario, no User

# Obtener el modelo de usuario
User = get_user_model()

#=======================================================================
#====================== VISTA PARA EL LOGIN ============================
#=======================================================================
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.warning(request, "Tu cuenta aún no está activa. Revisa tu correo.")
                return redirect('home')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return redirect('home')
            
    return redirect('home')


#===================================================================================
#====================== VISTA PARA REGISTRO DE USUARIOS ============================
#===================================================================================
@csrf_exempt
def registro(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        nombre = request.POST.get('nombre_completo')
        email = request.POST.get('email')
        p1 = request.POST.get('pass1')
        p2 = request.POST.get('pass2')
        
        # Validaciones
        if not nombre or not email or not p1 or not p2:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios.'})
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('home')
        
        if p1 != p2:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Las contraseñas no coinciden.'})
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('home')
        
        if len(p1) < 6:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres.'})
            messages.error(request, "La contraseña debe tener al menos 6 caracteres.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Este correo ya está registrado.'})
            messages.error(request, "Este correo ya está registrado.")
            return redirect('home')
        
        try:
            # Crear usuario
            nuevo_usuario = User.objects.create_user(
                email=email,
                password=p1,
                first_name=nombre,
                is_active=False
            )
            print(f"✅ Usuario creado con ID: {nuevo_usuario.id}")
            
            # Crear slug
            slug_base = nombre.lower().replace(' ', '-')
            slug = slug_base
            contador = 1
            while PerfilNegocio.objects.filter(slug=slug).exists():
                slug = f"{slug_base}-{contador}"
                contador += 1
            
            # Crear perfil
            perfil = PerfilNegocio.objects.create(
                usuario=nuevo_usuario,
                nombre_negocio=f"Negocio de {nombre}",
                slug=slug,
                rubro='general',
                activo=False
            )
            print(f"✅ Perfil creado con slug: {perfil.slug}")
            
            # Generar token
            uid = urlsafe_base64_encode(force_bytes(nuevo_usuario.pk))
            token = default_token_generator.make_token(nuevo_usuario)
            activation_link = request.build_absolute_uri(f'/activar-cuenta/{uid}/{token}/')
            
            # Enviar correo
            try:
                send_mail(
                    subject='Activa tu cuenta - TURNOCLIC',
                    message=f"""
Hola {nombre},

Activa tu cuenta: {activation_link}

Tu URL: https://{perfil.slug}.turnoclic.cl
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                print(f"✅ Correo enviado a {email}")
            except Exception as e:
                print(f"❌ Error correo: {e}")
            
            success_msg = f"¡Bienvenido {nombre}! Te hemos enviado un correo a {email}"
            
            if is_ajax:
                return JsonResponse({'success': True, 'message': success_msg})
            
            messages.success(request, success_msg)
            return redirect('home')
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error: {str(e)}")
            return redirect('home')
    
    return redirect('home')


#============================================================================
#====================== VISTA PARA CERRAR SESIÓN ============================
#============================================================================
def salir(request):
    logout(request)
    return redirect('home')


#=============================================================================
#====================== VISTA PARA ACTIVAR CUENTA ============================
#=============================================================================   
@csrf_exempt
def activar_cuenta(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        email = request.POST.get('email')
        
        try:
            usuario = User.objects.get(email=email)
            if not usuario.is_active:
                usuario.is_active = True
                usuario.save()
                message = "¡Cuenta activada con éxito! Ya puedes iniciar sesión."
                if is_ajax:
                    return JsonResponse({'success': True, 'message': message})
                messages.success(request, message)
            else:
                message = "Esta cuenta ya se encuentra activa."
                if is_ajax:
                    return JsonResponse({'success': False, 'error': message})
                messages.info(request, message)
            return redirect('home')
        except User.DoesNotExist:
            error_msg = "El correo ingresado no corresponde a ninguna cuenta."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('home')
    
    return redirect('home')


#===================================================================================
#====================== VISTA PARA RECUPERAR CONTRASEÑA ============================
#=================================================================================== 
@csrf_exempt
def recuperar_contrasena(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        email = request.POST.get('email')
        
        try:
            usuario = User.objects.get(email=email)
            
            token = default_token_generator.make_token(usuario)
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            domain = "127.0.0.1:8000"
            link = f"http://{domain}/reset/{uid}/{token}/"
            
            send_mail(
                subject="Recuperar Acceso - TurnoClic",
                message=f"Hola {usuario.first_name},\n\nRestablece tu contraseña: {link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            message = "Te hemos enviado un correo con las instrucciones."
            if is_ajax:
                return JsonResponse({'success': True, 'message': message})
            messages.success(request, message)
            return redirect('home')
            
        except User.DoesNotExist:
            message = "Si el correo existe, recibirás las instrucciones."
            if is_ajax:
                return JsonResponse({'success': True, 'message': message})
            messages.success(request, message)
            return redirect('home')
        except Exception as e:
            error_msg = "Hubo un problema al enviar el correo."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('home')
    
    return redirect('home')


#================================================================================================
#====================== VISTA PARA CONFIRMAR EL CAMBIO DE CONTRASEÑA ============================
#================================================================================================
def reset_password_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        usuario = None

    if usuario is not None and default_token_generator.check_token(usuario, token):
        if request.method == 'POST':
            p1 = request.POST.get('pass1')
            p2 = request.POST.get('pass2')
            if p1 == p2:
                usuario.set_password(p1)
                usuario.save()
                messages.success(request, "Contraseña actualizada. Ya puedes iniciar sesión.")
                return redirect('home')
            else:
                messages.error(request, "Las contraseñas no coinciden.")
        
        return render(request, 'reservas/authentication/reset_password.html')
    else:
        messages.error(request, "El enlace es inválido o ha expirado.")
        return redirect('home')


#==========================================
#-------ACTIVAR CUENTA POR TOKEN-----------
#==========================================
def activar_por_token(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "¡Cuenta activada exitosamente!")
            return redirect('login')
        else:
            messages.error(request, "El enlace es inválido o ha expirado.")
            return redirect('home')
    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, "Error al activar la cuenta.")
        return redirect('home')