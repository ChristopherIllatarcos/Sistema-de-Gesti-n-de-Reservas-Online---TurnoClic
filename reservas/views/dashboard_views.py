from datetime import date, timedelta
from django.db import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from reservas.models import PerfilNegocio, Reserva
from decimal import Decimal
from reservas.models import Cliente

# TODO: Mover dashboard aquí

#==========================================================================================================    
#====================== VISTA PARA EL DASHBOARD (PÁGINA PRINCIPAL DEL SISTEMA) ============================
#==========================================================================================================
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import date, timedelta

@login_required
def dashboard(request):

    print("SUBDOMINIO:", request.subdominio)

    perfil = None

    if request.subdominio:
        perfil = PerfilNegocio.objects.filter(slug=request.subdominio).first() # Busca por slug
    
    # ✅ SI NO ENCUENTRA POR SLUG, BUSCA POR USUARIO
    if not perfil:
        perfil = PerfilNegocio.objects.filter(usuario=request.user).first() 
    
    # ✅ SI AÚN NO EXISTE, LO CREA
    if not perfil:
        perfil = PerfilNegocio.objects.create(
            usuario=request.user,
            slug=request.subdominio or f"perfil-{request.user.id}"
        )

    reservas = Reserva.objects.filter( # Accede a todos los objetos (registros) de la tabla Reserva
        profesional__negocio=perfil # Busca reservas donde el profesional asociado tenga un negocio que sea igual a perfil
    ).order_by("-fecha", "hora") # Ordena las reservas por fecha descendente

    citas_pendientes = reservas.filter(estado="pendiente").count() # Conteo de citas pendientes
    citas_hoy = reservas.filter(fecha=date.today()).count() # Conteo de citas hoy
    total_reservas = reservas.count() # Conteo de todas las reservas
    
    # ============================================
    # PUNTOS BONUS (si no existe, usar 0)
    # ============================================
    puntos = getattr(perfil, "puntos_bonus", 0) # Obtiene el atributo "puntos_bonus" del perfil
    # ============================================
    # PUNTOS TOTALES (si no existen, usar 0)
    # ============================================
    puntos_totales_clientes = Cliente.objects.aggregate(total=models.Sum('puntos'))['total'] or 0
    
    # ============================================
    # GRÁFICO: Reservas por día (últimos 7 días)
    # ============================================
    ultimos_7_dias = []
    reservas_por_dia = []
    
    for i in range(6, -1, -1): # Recorre 6, 5, 4, 3, 2, 1, 0
        fecha = date.today() - timedelta(days=i) # Resta 7, 6, 5, 4, 3, 2, 1
        ultimos_7_dias.append(fecha.strftime('%d/%m')) # Agrega a la lista
        count = reservas.filter(fecha=fecha).count() # Conteo de reservas para esa fecha
        reservas_por_dia.append(count) # Agrega a la lista
    
    # ============================================
    # GRÁFICO: Top servicios más reservados
    # ============================================
    top_servicios = list( # Devuelve una lista
        reservas.values('servicio__nombre') # Devuelve un diccionario
        .annotate(total=Count('id')) # Anota el conteo
        .order_by('-total')[:5] # Ordena por conteo descendente
    )
    
    servicios_nombres = [s['servicio__nombre'] for s in top_servicios] if top_servicios else [] # Agrega a la lista
    servicios_cantidades = [s['total'] for s in top_servicios] if top_servicios else [] # Agrega a la lista
    
    # ============================================
    # GRÁFICO: Reservas por mes (últimos 6 meses)
    # ============================================
    meses = []
    reservas_por_mes = []
    
    for i in range(5, -1, -1): # Recorre 5, 4, 3, 2, 1, 0
        mes = date.today().replace(day=1) - timedelta(days=30 * i) # Resta 30, 60, 90, 120, 150
        meses.append(mes.strftime('%B')) # Agrega a la lista
        count = reservas.filter( # Conteo de reservas para ese mes
            fecha__year=mes.year, # Filtra por año
            fecha__month=mes.month # Filtra por mes
        ).count() # Conteo
        reservas_por_mes.append(count) # Agrega a la lista 
    
    # ============================================
    # PRÓXIMAS RESERVAS (para la tabla)
    # ============================================
    proximas_reservas = reservas.filter( # Busca reservas donde la fecha sea mayor o igual a la fecha actual
        fecha__gte=date.today() # Filtra por fecha mayor o igual a la fecha actual
    ).order_by('fecha', 'hora')[:10] # Ordena por fecha ascendente

    # ============================================
    # NUEVAS ESTADÍSTICAS
    # ============================================
    
    # 1. Ingresos del mes actual
    ahora = timezone.now()
    ingresos_mes = reservas.filter(
        fecha__year=ahora.year,
        fecha__month=ahora.month
    ).aggregate(total=Sum('servicio__precio'))['total'] or 0
    
    # 2. Ingresos del mes anterior
    mes_anterior = ahora - timedelta(days=30)
    ingresos_mes_anterior = reservas.filter(
        fecha__year=mes_anterior.year,
        fecha__month=mes_anterior.month
    ).aggregate(total=Sum('servicio__precio'))['total'] or 0
    
    # 3. Porcentaje de crecimiento
    if ingresos_mes_anterior > 0:
        crecimiento = ((ingresos_mes - ingresos_mes_anterior) / ingresos_mes_anterior) * 100
    else:
        crecimiento = 100 if ingresos_mes > 0 else 0
    
    # 4. Top clientes (los que más reservan)
    top_clientes = list(
        reservas.values('cliente__nombres', 'cliente__apellido_paterno')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    
    clientes_nombres = [f"{c['cliente__nombres']} {c['cliente__apellido_paterno']}"[:20] for c in top_clientes]
    clientes_cantidades = [c['total'] for c in top_clientes]
    
    # 5. Distribución por estado de reserva
    estado_pendiente = reservas.filter(estado='pendiente').count()
    estado_confirmado = reservas.filter(estado='confirmado').count()
    estado_cancelado = reservas.filter(estado='cancelado').count()
    
    # 6. Próximos 7 días (reservas)
    proximos_7_dias = []
    reservas_proximas = []
    for i in range(1, 8):
        fecha = date.today() + timedelta(days=i)
        proximos_7_dias.append(fecha.strftime('%d/%m'))
        count = reservas.filter(fecha=fecha).count()
        reservas_proximas.append(count)
    
    # 7. Ingresos por mes para gráfico (últimos 6 meses)
    ingresos_por_mes = []
    for i in range(5, -1, -1):
        mes = date.today().replace(day=1) - timedelta(days=30 * i)
        ingreso = reservas.filter(
            fecha__year=mes.year,
            fecha__month=mes.month
        ).aggregate(total=Sum('servicio__precio'))['total'] or 0
        ingresos_por_mes.append(ingreso)

    context = {
        'perfil': perfil,
        'nombre_negocio': perfil.nombre_negocio,
        'username': request.user.first_name or request.user.email,
        'puntos': puntos,
        'reservas': reservas,
        'conteo_reservas': total_reservas,
        'citas_pendientes': citas_pendientes,
        'citas_hoy': citas_hoy,
        'total_reservas': total_reservas,
        'puntos_totales_clientes': puntos_totales_clientes,

        
        # Datos para gráficos existentes
        'dias_labels': ultimos_7_dias,
        'reservas_data': reservas_por_dia,
        'servicios_labels': servicios_nombres,
        'servicios_data': servicios_cantidades,
        'meses_labels': meses,
        'reservas_mes_data': reservas_por_mes,
        'proximas_reservas': proximas_reservas,
        
        # NUEVOS DATOS PARA GRÁFICOS
        'ingresos_mes': ingresos_mes,
        'crecimiento': round(crecimiento, 1),
        'ingresos_por_mes': ingresos_por_mes,
        'clientes_nombres': clientes_nombres,
        'clientes_cantidades': clientes_cantidades,
        'estado_pendiente': estado_pendiente,
        'estado_confirmado': estado_confirmado,
        'estado_cancelado': estado_cancelado,
        'proximos_dias_labels': proximos_7_dias,
        'proximos_dias_data': reservas_proximas,
    }

    return render(request, 'reservas/authentication/dashboard.html', context)



@login_required
def panel_graficos(request):
    """Vista para la página de gráficos y estadísticas"""
    perfil = request.user.perfil
    
    reservas = Reserva.objects.filter(profesional__negocio=perfil)
    
    # ============================================
    # GRÁFICO: Reservas por día (últimos 7 días)
    # ============================================
    ultimos_7_dias = []
    reservas_por_dia = []
    for i in range(6, -1, -1):
        fecha = date.today() - timedelta(days=i)
        ultimos_7_dias.append(fecha.strftime('%d/%m'))
        count = reservas.filter(fecha=fecha).count()
        reservas_por_dia.append(count)
    
    # ============================================
    # GRÁFICO: Top servicios más reservados
    # ============================================
    top_servicios = list(
        reservas.values('servicio__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    servicios_nombres = [s['servicio__nombre'] for s in top_servicios] if top_servicios else []
    servicios_cantidades = [s['total'] for s in top_servicios] if top_servicios else []
    
    # ============================================
    # GRÁFICO: Reservas por mes (últimos 6 meses)
    # ============================================
    meses = []
    reservas_por_mes = []
    for i in range(5, -1, -1):
        mes = date.today().replace(day=1) - timedelta(days=30 * i)
        meses.append(mes.strftime('%B'))
        count = reservas.filter(
            fecha__year=mes.year,
            fecha__month=mes.month
        ).count()
        reservas_por_mes.append(count)
    
    # ============================================
    # NUEVAS ESTADÍSTICAS (convertir Decimal a float)
    # ============================================
    ahora = timezone.now()
    ingresos_mes = reservas.filter(
        fecha__year=ahora.year,
        fecha__month=ahora.month
    ).aggregate(total=Sum('servicio__precio'))['total'] or 0
    
    # ✅ Convertir a float si es Decimal
    if isinstance(ingresos_mes, Decimal):
        ingresos_mes = float(ingresos_mes)
    
    ingresos_por_mes = []
    for i in range(5, -1, -1):
        mes = date.today().replace(day=1) - timedelta(days=30 * i)
        ingreso = reservas.filter(
            fecha__year=mes.year,
            fecha__month=mes.month
        ).aggregate(total=Sum('servicio__precio'))['total'] or 0
        if isinstance(ingreso, Decimal):
            ingreso = float(ingreso)
        ingresos_por_mes.append(ingreso)
    
    # Top clientes
    top_clientes = list(
        reservas.values('cliente__nombres', 'cliente__apellido_paterno')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    clientes_nombres = [f"{c['cliente__nombres']} {c['cliente__apellido_paterno']}"[:20] for c in top_clientes]
    clientes_cantidades = [c['total'] for c in top_clientes]
    
    # Estados
    estado_pendiente = reservas.filter(estado='pendiente').count()
    estado_confirmado = reservas.filter(estado='confirmado').count()
    estado_cancelado = reservas.filter(estado='cancelado').count()
    
    # Próximos 7 días
    proximos_7_dias = []
    reservas_proximas = []
    for i in range(1, 8):
        fecha = date.today() + timedelta(days=i)
        proximos_7_dias.append(fecha.strftime('%d/%m'))
        count = reservas.filter(fecha=fecha).count()
        reservas_proximas.append(count)
    
    # ✅ Suma total de reservas próximas
    total_proximas = sum(reservas_proximas)
    
    context = {
        'perfil': perfil,
        'nombre_negocio': perfil.nombre_negocio,
        'username': request.user.first_name or request.user.email,
        
        # Datos para gráficos
        'dias_labels': ultimos_7_dias,
        'reservas_data': reservas_por_dia,
        'servicios_labels': servicios_nombres,
        'servicios_data': servicios_cantidades,
        'meses_labels': meses,
        'reservas_mes_data': reservas_por_mes,
        'ingresos_por_mes': ingresos_por_mes,  # ✅ Ya convertido
        'clientes_nombres': clientes_nombres,
        'clientes_cantidades': clientes_cantidades,
        'estado_pendiente': estado_pendiente,
        'estado_confirmado': estado_confirmado,
        'estado_cancelado': estado_cancelado,
        'proximos_dias_labels': proximos_7_dias,
        'proximos_dias_data': reservas_proximas,
        'ingresos_mes': ingresos_mes,  # ✅ Ya convertido
        'total_proximas': total_proximas,
    }
    
    return render(request, 'reservas/authentication/panel_graficos.html', context)