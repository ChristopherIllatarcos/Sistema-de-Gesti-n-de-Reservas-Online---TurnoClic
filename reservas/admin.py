from django.contrib import admin
from .models import Disponibilidad, Mensaje, PerfilNegocio, Profesional, Reserva, Servicio, SolicitudDemo


# Register your models here.

#admin.site.register(Usuario)
admin.site.register(PerfilNegocio)

#admin.site.register(Profesional)
#admin.site.register(Servicio)
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion_minutos')
    search_fields = ('nombre',)

#admin.site.register(Servicio)
@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especialidad", "activo", "negocio")
    list_filter = ("activo", "negocio")
    search_fields = ("nombre", "especialidad")
    

@admin.register(Disponibilidad)
class DisponibilidadAdmin(admin.ModelAdmin):
    # Mostramos las columnas nuevas: Profesional, Fecha, Hora y si está libre
    list_display = ('profesional', 'fecha', 'hora', 'esta_libre')
    
    # Filtros laterales para buscar más rápido por fecha o profesional
    list_filter = ('fecha', 'profesional', 'esta_libre')
    
    # Ordenar por fecha y luego por hora para que se vea organizado
    ordering = ('fecha', 'hora')      


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fecha",
        "hora",
        "servicio",
        "profesional",
        "cliente",
    )

    list_filter = ("fecha", "profesional")
    search_fields = ("rut_cliente", "cliente__rut")


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "correo", "asunto", "leido", "archivado", "creado_en")
    list_filter = ("leido", "archivado", "creado_en")
    search_fields = ("nombre", "correo", "asunto", "mensaje")
    
#======================================================================================
#----------------------------SOLICITUD DEMO--------------------------------------------
#======================================================================================
@admin.register(SolicitudDemo)
class SolicitudDemoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'telefono', 'fecha_creacion', 'leida']
    list_filter = ['leida', 'fecha_creacion']
    search_fields = ['nombre', 'email', 'telefono']
    actions = ['marcar_como_leidas']
    
    def marcar_como_leidas(self, request, queryset):
        queryset.update(leida=True)
    marcar_como_leidas.short_description = "Marcar seleccionadas como leídas"