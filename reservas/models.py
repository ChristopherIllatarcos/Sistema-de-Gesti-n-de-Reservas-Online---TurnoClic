from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from config import settings



# Create your models here.

#======= Personalizamos el modelo de usuario para usar el email como identificador=======
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

#===================== Modelo de usuario personalizado ============================
class Usuario(AbstractUser):
    # Eliminamos el username para que no moleste
    username = None
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    
    es_equipo_confianza = models.BooleanField(default=False)
    esta_activado = models.BooleanField(default=False)

    objects = UsuarioManager() # Aquí le asignamos el nuevo Manager

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Quitamos el username de aquí también

    def __str__(self):
        return self.email


#===================== Modelo para el perfil del negocio ============================

class PerfilNegocio(models.Model):
    # Definir los tipos de rubro disponibles
    RUBROS = (
        ('deporte', '🏆 Deportes / Canchas'),
        ('belleza', '✂️ Belleza / Barbería'),
        ('salud', '🏥 Salud / Bienestar'),
        ('educacion', '📚 Educación / Clases'),
        ('comida', '🍽️ Comida / Restaurante'),
        ('eventos', '🎉 Eventos / Celebraciones'),
        ('spa', '💆 Spa / Relajación'),
        ('general', '📦 General / Otros'),
    )
    
    # Usuario (OneToOne)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='perfil'
    )
    
    # Datos básicos del negocio
    nombre_negocio = models.CharField(max_length=100, default="Mi Negocio")
    descripcion = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos_negocios/', blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    puntos_bonus = models.IntegerField(default=0)
    
    # URL del negocio (slug)
    slug = models.SlugField(null=True, blank=True, unique=False)
    
    # Rubro del negocio
    rubro = models.CharField(max_length=20, choices=RUBROS, default='general')
    
    # Redes sociales
    instagram = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        help_text="Usuario de Instagram (ej: turnoclic)"
    )
    whatsapp = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        help_text="Número de WhatsApp con código país (ej: 56912345678)"
    )
    
    # ============================================
    # CAMPOS PARA DEMO Y ACTIVACIÓN
    # ============================================
    activo = models.BooleanField(
        default=False, 
        help_text="Si el negocio está activo (demo aprobada)"
    )
    fecha_solicitud = models.DateTimeField(
        default=timezone.now, 
        help_text="Fecha de solicitud demo"
    )
    fecha_expiracion = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Fecha de expiración del demo"
    )

    def __str__(self):
        return f"{self.nombre_negocio} - {self.usuario.email}"
    
    # ============================================
    # MÉTODOS PARA REDES SOCIALES
    # ============================================
    def get_instagram_url(self):
        """Genera la URL de Instagram"""
        if self.instagram:
            insta_user = self.instagram.replace('@', '').strip()
            if insta_user:
                return f"https://instagram.com/{insta_user}"
        return "#"
    
    def get_whatsapp_url(self):
        """Genera la URL de WhatsApp"""
        if self.whatsapp:
            numero = self.whatsapp.replace('+', '').replace(' ', '').replace('-', '')
            if numero:
                return f"https://wa.me/{numero}"
        return "#"
    
    # ============================================
    # MÉTODOS PARA DEMO
    # ============================================
    def dias_restantes_demo(self):
        """Días restantes del período demo"""
        if self.fecha_expiracion:
            delta = self.fecha_expiracion - timezone.now()
            return max(0, delta.days)
        return 0
    
    def esta_en_demo(self):
        """Verifica si el negocio está en período demo activo"""
        if self.fecha_expiracion:
            return self.activo and timezone.now() <= self.fecha_expiracion
        return self.activo
    
    def guardar_como_demo(self, dias=14):
        """Configura el negocio como demo por 'dias' días"""
        self.activo = False
        self.fecha_expiracion = timezone.now() + timedelta(days=dias)
        self.save()
    
    def activar_negocio(self):
        """Activa el negocio (demo o plan pagado)"""
        self.activo = True
        self.save()
    
    def extender_demo(self, dias=7):
        """Extiende el período demo"""
        if self.fecha_expiracion:
            self.fecha_expiracion += timedelta(days=dias)
        else:
            self.fecha_expiracion = timezone.now() + timedelta(days=dias)
        self.save()

#===================== Modelo para las citas/reservas ============================
class Cita(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    servicio = models.CharField(max_length=100)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    

    def __str__(self):
        return f"{self.servicio} - {self.usuario.first_name}"
    
#===================== Modelo para los servicios que ofrece el negocio ============================
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    duracion_minutos = models.PositiveIntegerField(default=30)
    negocio = models.ForeignKey('PerfilNegocio', on_delete=models.CASCADE, related_name='servicios', null=True, blank=True)



    def __str__(self):
        return f"{self.nombre} - ${self.precio}"
    
#===================== Modelo para los profesionales o personal del negocio ============================   
class Profesional(models.Model):
    negocio = models.ForeignKey(
        PerfilNegocio,
        on_delete=models.CASCADE,
        related_name="profesionales"
    )

    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.especialidad}"
    
 #===================== Modelo para los bloques de horario de cada profesional ============================   
class BloqueHorario(models.Model):
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)
    dia_semana = models.IntegerField() # 0 para Lunes, 1 para Martes, etc.
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.profesional} - Día {self.dia_semana}"
    
#===================== Modelo para la disponibilidad de cada profesional ============================    
class Disponibilidad(models.Model):
    profesional = models.ForeignKey('Profesional', on_delete=models.CASCADE)
    fecha = models.DateField(verbose_name="Fecha Disponible") 
    hora = models.TimeField(verbose_name="Hora Disponible")   
    esta_libre = models.BooleanField(default=True, verbose_name="¿Está disponible?")

    class Meta:
        verbose_name = "Bloque de Horario"
        verbose_name_plural = "Bloques de Horarios"
        unique_together = ['profesional', 'fecha', 'hora']

    def __str__(self):
        estado = "Libre" if self.esta_libre else "Ocupado"
        return f"{self.profesional} - {self.fecha} a las {self.hora} ({estado})"


 #===================== Modelo para los clientes que reservan sin crear cuenta ============================    
class Cliente(models.Model):
    rut = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    puntos = models.IntegerField(default=0)

    def __str__(self):
        return self.rut


#===================== Modelo para las reservas realizadas por los clientes ============================
class Reserva(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)

    fecha = models.DateField()
    hora = models.TimeField()

    tipo_documento = models.CharField(max_length=20, default="rut")
    rut_cliente = models.CharField(max_length=20)

    nombre_cliente = models.CharField(max_length=150, blank=True, null=True)
    telefono_cliente = models.CharField(max_length=20, blank=True, null=True)
    correo_cliente = models.EmailField(blank=True, null=True)

    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    negocio = models.ForeignKey(PerfilNegocio, on_delete=models.CASCADE, null=True, blank=True)
    archivado = models.BooleanField(default=False)

    
    estado = models.CharField(
        max_length=20,
        default="pendiente"
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva {self.rut_cliente} - {self.fecha} {self.hora}"
    
#====================================================================================
# Modelo para los mensajes entre el negocio y el cliente 
#====================================================================================
class Mensaje(models.Model):
    negocio = models.ForeignKey(PerfilNegocio, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)

    nombre = models.CharField(max_length=100)
    correo = models.EmailField()

    asunto = models.CharField(max_length=150)
    mensaje = models.TextField()

    leido = models.BooleanField(default=False)

    creado_en = models.DateTimeField(auto_now_add=True)
    
    archivado = models.BooleanField(default=False)

    def __str__(self):
        return self.asunto
    

"""
    Modelo para las solicitudes de demo 
"""
# models.py
class SolicitudDemo(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    mensaje = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    
    
#===================== Modelo para las reseñas de los clientes ============================
class Resena(models.Model):
    """Modelo para reseñas y calificaciones de clientes"""
    ESTRELLAS = (
        (1, '★☆☆☆☆ - Muy malo'),
        (2, '★★☆☆☆ - Malo'),
        (3, '★★★☆☆ - Regular'),
        (4, '★★★★☆ - Bueno'),
        (5, '★★★★★ - Excelente'),
    )
    
    reserva = models.OneToOneField('Reserva', on_delete=models.CASCADE, related_name='resena')
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='resenas')
    negocio = models.ForeignKey('PerfilNegocio', on_delete=models.CASCADE, related_name='resenas')
    
    puntuacion = models.IntegerField(choices=ESTRELLAS)
    comentario = models.TextField(blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    publicada = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
    
    def __str__(self):
        return f"{self.cliente.nombres} - {self.puntuacion} estrellas"
    
    def get_puntuacion_html(self):
        """Devuelve estrellas en HTML"""
        estrellas = ''
        for i in range(5):
            if i < self.puntuacion:
                estrellas += '<i class="fas fa-star" style="color: #ffc107;"></i>'
            else:
                estrellas += '<i class="fas fa-star" style="color: #e4e5e9;"></i>'
        return estrellas