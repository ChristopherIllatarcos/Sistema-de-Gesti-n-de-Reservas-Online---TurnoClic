from django.urls import path
from reservas.views import (
    # Vistas principales (other_views)
    home, modulos, soporte, planes, contacto, editar_perfil,
    agendar_vortex, api_horas, vista_negocio, enviar_recordatorios_manual,
    exportar_reservas_excel, exportar_reporte_pdf,
    
    # Autenticación (auth_views)
    login_view, registro, salir, activar_cuenta, recuperar_contrasena,
    reset_password_confirm, activar_por_token,
    
    # Dashboard
    dashboard, panel_graficos, 
    
    # Demo
    solicitar_demo, guardar_solicitud_demo, activar_demo,
    
    # Reservas
    reservar, crear_reserva, obtener_disponibilidad, obtener_horas, obtener_cliente_por_rut,
    
    # Gestión (CRUDs)
    lista_servicios, crear_servicio, editar_servicio, eliminar_servicio, obtener_servicio,
    lista_profesionales, crear_profesional, editar_profesional, eliminar_profesional, toggle_profesional,
    lista_horarios, crear_horario, editar_horario, eliminar_horario, obtener_horario, editar_negocio, 
    lista_resenas,
    # Cliente
    mis_citas, ver_reserva, eliminar_reserva, mensajes, archivar_mensaje, limpiar_reservas_pasadas, 
    enviar_resena,
)

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('salir/', salir, name='logout'),
    path('registro/', registro, name='registro'),
    path('activar/', activar_cuenta, name='activar'),
    path('recuperar/', recuperar_contrasena, name='recuperar'),
    path('reset/<uidb64>/<token>/', reset_password_confirm, name='password_reset_confirm'),
    path('perfil/', editar_perfil, name='perfil'),
    path('modulos/', modulos, name='modulos'),
    path('soporte/', soporte, name='soporte'),
    path('planes/', planes, name='planes'),
    path("contacto/", contacto, name="contacto"),
    path('solicitar-demo/', solicitar_demo, name='solicitar_demo'),
    path('enviar-demo/', guardar_solicitud_demo, name='guardar_solicitud_demo'),
    path("reservar/<int:negocio_id>/", agendar_vortex, name="agendar_vortex"),
    path('api/disponibilidad/', obtener_disponibilidad, name='api_disponibilidad'),
    path('api/horas/', obtener_horas, name='api_horas'),
    path("api/reservar/", crear_reserva, name="api_reservar"),
    path("api/cliente/", obtener_cliente_por_rut, name="api_cliente"),
    path('mis-citas/', mis_citas, name='mis_citas'),
    path('mensajes/', mensajes, name='mensajes'),
    path('mensajes/archivar/<int:id>/', archivar_mensaje, name='archivar_mensaje'),
    path('reserva/<int:id>/', ver_reserva, name='ver_reserva'),
    path('reserva/eliminar/<int:id>/', eliminar_reserva, name='eliminar_reserva'),
    path('reservar/', reservar, name='reservar'),
    path('negocio/editar/', editar_negocio, name='editar_negocio'),
    path('servicios/', lista_servicios, name='lista_servicios'),
    path('servicios/crear/', crear_servicio, name='crear_servicio'),
    path('servicios/editar/<int:id>/', editar_servicio, name='editar_servicio'),
    path('servicios/eliminar/<int:id>/', eliminar_servicio, name='eliminar_servicio'),
    path('servicios/obtener/<int:id>/', obtener_servicio, name='obtener_servicio'),
    path('activar-demo/<uidb64>/<token>/', activar_demo, name='activar_demo'),
    path('profesionales/', lista_profesionales, name='lista_profesionales'),
    path('profesionales/crear/', crear_profesional, name='crear_profesional'),
    path('profesionales/editar/<int:id>/', editar_profesional, name='editar_profesional'),
    path('profesionales/eliminar/<int:id>/', eliminar_profesional, name='eliminar_profesional'),
    path('profesionales/toggle/<int:id>/', toggle_profesional, name='toggle_profesional'),
    path('horarios/', lista_horarios, name='lista_horarios'),
    path('horarios/crear/', crear_horario, name='crear_horario'),
    path('horarios/editar/<int:id>/', editar_horario, name='editar_horario'),
    path('horarios/eliminar/<int:id>/', eliminar_horario, name='eliminar_horario'),
    path('horarios/obtener/<int:id>/', obtener_horario, name='obtener_horario'),
    path('activar-cuenta/<uidb64>/<token>/', activar_por_token, name='activar_por_token'),
    path('enviar-recordatorios/', enviar_recordatorios_manual, name='enviar_recordatorios_manual'),
    path('resenas/', lista_resenas, name='lista_resenas'),
    path('api/enviar-resena/<int:reserva_id>/', enviar_resena, name='enviar_resena'),
    
    # ============================================
    # EXPORTAR Y GRÁFICOS (DEBEN IR ANTES DEL SLUG)
    # ============================================
    path('exportar/excel/', exportar_reservas_excel, name='exportar_reservas_excel'),
    path('exportar/pdf/', exportar_reporte_pdf, name='exportar_reporte_pdf'),
    path('panel-graficos/', panel_graficos, name='panel_graficos'),
    path('limpiar-reservas/', limpiar_reservas_pasadas, name='limpiar_reservas_pasadas'),
    
    # ⚠️ ESTA URL DEBE IR AL FINAL ⚠️ (slug genérico)
    path("<slug:slug>/", vista_negocio, name="negocio"),
]