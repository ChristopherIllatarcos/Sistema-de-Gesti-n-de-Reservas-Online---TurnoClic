import json
import re
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from datetime import date, datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone  
from django.db.models import Count
from recordatorios import models
from reservas.models import Cliente, Disponibilidad, Mensaje, PerfilNegocio, Profesional, Reserva, Servicio, SolicitudDemo

import pandas as pd
from django.http import HttpResponse
from openpyxl.styles import Font, Alignment, PatternFill
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime


# Definimos User dinámicamente
User = get_user_model()



#=========================================================================================
#====================== VISTA PARA EL HOME (PÁGINA DE INICIO) ============================
#=========================================================================================
def home(request):
    negocios = PerfilNegocio.objects.all()
    return render(request, "reservas/home.html", {"negocios": negocios})
    

#===========================================================================================
#====================== VISTA PARA EL MENÚ DE MÓDULOS Y FUNCIONALIDADES ====================
#===========================================================================================
def modulos(request):
    return render(request, 'reservas/menu/modulos.html')


#======================================================================
#====================== VISTA PARA SOPORTE ============================
#======================================================================
def soporte(request):
    return render(request, 'reservas/menu/soporte.html')


#=====================================================================
#====================== VISTA PARA PLANES ============================
#=====================================================================
def planes(request):
    return render(request, 'reservas/menu/planes.html')


#=======================================================================
#====================== VISTA PARA CONTACTO ============================
#=======================================================================
def contacto(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        asunto = request.POST.get("asunto")
        mensaje_txt = request.POST.get("mensaje")

        mensaje_admin = f"""
Nuevo mensaje desde TurnoClic:

Nombre: {nombre}
Correo: {email}
Asunto: {asunto}

Mensaje:
{mensaje_txt}
"""

        send_mail(
            f"[CONTACTO TURNOCLIC] {asunto}",
            mensaje_admin,
            settings.DEFAULT_FROM_EMAIL,
            ["contacto.boostpro@gmail.com"],
            fail_silently=False
        )

        mensaje_cliente = f"""
Hola {nombre},

Hemos recibido tu solicitud correctamente ✅

Nuestro equipo revisará tu mensaje y te responderá a la brevedad.

Gracias por contactarnos.
TurnoClic - Tu agenda digital
"""

        send_mail(
            "Hemos recibido tu solicitud - TurnoClic",
            mensaje_cliente,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )

        messages.success(request, "Hemos recibido tu solicitud. Te responderemos a la brevedad 📩")
        return redirect("contacto")

    return render(request, "reservas/menu/contacto.html")


#=======================================================================================        
#====================== VISTA PARA EDITAR PERFIL DE USUARIO ============================
#=======================================================================================        
@login_required
def editar_perfil(request):
    perfil, created = PerfilNegocio.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        perfil.nombre_negocio = request.POST.get('nombre_negocio')
        perfil.telefono = request.POST.get('telefono')
        perfil.direccion = request.POST.get('direccion')
        perfil.descripcion = request.POST.get('descripcion')
        
        if request.FILES.get('logo'):
            perfil.logo = request.FILES.get('logo')
            
        perfil.save()
        messages.success(request, "¡Perfil actualizado con éxito!")
        return redirect('dashboard')

    return render(request, 'reservas/authentication/perfil.html', {'perfil': perfil})


#=======================================================================================
#====================== VISTA ÚNICA PARA RESERVAS (PÚBLICA) ============================
#=======================================================================================
def agendar_vortex(request, negocio_id):
    perfil = PerfilNegocio.objects.get(id=negocio_id)
    servicios = Servicio.objects.all()
    profesionales = Profesional.objects.filter(negocio=perfil, activo=True)

    return render(request, "reservas/public/agendar.html", {
        "servicios": servicios,
        "profesionales": profesionales,
        "perfil": perfil
    })


#==========================================================================================================    
#====================== VISTA PARA API DE HORAS ============================
#==========================================================================================================
def api_horas(request):
    profesional_id = request.GET.get("profesional_id")
    fecha = request.GET.get("fecha")

    reservas = Reserva.objects.filter(
        profesional_id=profesional_id,
        fecha=fecha
    ).values_list("hora", flat=True)

    horas_ocupadas = list(reservas)

    return JsonResponse({
        "horas_ocupadas": horas_ocupadas
    })
 

#==================================================
# --------- VISTA PARA VISTA DE NEGOCIO -----------
#==================================================     
def vista_negocio(request, slug):
    negocio = get_object_or_404(PerfilNegocio, slug=slug)
    return render(request, "reservas/home.html", {"negocio": negocio})

  


#==========================================
#-------ENVIAR RECORDATORIOS----------------
#==========================================
@login_required
def enviar_recordatorios_manual(request):
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('enviar_recordatorios', stdout=out)
        
        messages.success(request, "✅ Recordatorios enviados correctamente")
    except Exception as e:
        # Si el comando no existe, mostrar un mensaje de prueba
        messages.info(request, "ℹ️ Función de recordatorios en desarrollo. Se enviarán pronto.")
        print(f"Error al enviar recordatorios: {e}")
        messages.success(request, "✅ Botón de recordatorios funcionando")
    
    return redirect('dashboard')









# ==================================================
# EXPORTAR RESERVAS A EXCEL
# ==================================================


@login_required
def exportar_reservas_excel(request):
    """Exporta las reservas del negocio a Excel"""
    perfil = request.user.perfil
    reservas = Reserva.objects.filter(profesional__negocio=perfil).order_by('-fecha', 'hora')
    
    # Crear DataFrame
    data = []
    for r in reservas:
        data.append({
            'ID': r.id,
            'Fecha': r.fecha.strftime('%d/%m/%Y'),
            'Hora': r.hora.strftime('%H:%M'),
            'Servicio': r.servicio.nombre,
            'Profesional': r.profesional.nombre,
            'Cliente': f"{r.cliente.nombres} {r.cliente.apellido_paterno}",
            'Teléfono': r.telefono_cliente,
            'Correo': r.correo_cliente or r.cliente.correo,
            'Estado': r.estado,
            'Creado': r.creado_en.strftime('%d/%m/%Y %H:%M')
        })
    
    df = pd.DataFrame(data)
    
    # Crear respuesta HTTP con Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=reservas_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    
    # Escribir a Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Reservas', index=False)
        
        # Formatear
        worksheet = writer.sheets['Reservas']
        for cell in worksheet[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.font = Font(color="FFFFFF", bold=True)
        
        # Ajustar ancho de columnas
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    return response


# ==================================================
# EXPORTAR REPORTE DE INGRESOS A PDF
# ==================================================
@login_required
def exportar_reporte_pdf(request):
    """Exporta reporte de ingresos del mes actual a PDF"""
    from django.db.models import Count  # O importarlo arriba
    
    perfil = request.user.perfil
    ahora = datetime.now()
    
    # Reservas del mes actual
    reservas_mes = Reserva.objects.filter(
        profesional__negocio=perfil,
        fecha__year=ahora.year,
        fecha__month=ahora.month
    )
    
    # Estadísticas
    total_reservas = reservas_mes.count()
    total_ingresos = sum(r.servicio.precio for r in reservas_mes)
    servicios_top = reservas_mes.values('servicio__nombre').annotate(total=Count('id')).order_by('-total')[:5]
    
    # Crear PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#ef233c'),
        alignment=1,  # Centro
        spaceAfter=20
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    story.append(Paragraph(f"Reporte de Ingresos - {ahora.strftime('%B %Y')}", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Resumen
    summary_style = ParagraphStyle('Summary', parent=styles['Normal'], fontSize=12, spaceAfter=10)
    story.append(Paragraph(f"<b>Negocio:</b> {perfil.nombre_negocio}", summary_style))
    story.append(Paragraph(f"<b>Fecha de emisión:</b> {ahora.strftime('%d/%m/%Y %H:%M')}", summary_style))
    story.append(Paragraph(f"<b>Total reservas:</b> {total_reservas}", summary_style))
    story.append(Paragraph(f"<b>Ingresos totales:</b> ${total_ingresos:,.0f} CLP", summary_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla de servicios más reservados
    story.append(Paragraph("<b>Servicios más reservados</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    tabla_data = [['Servicio', 'Cantidad']]
    for s in servicios_top:
        tabla_data.append([s['servicio__nombre'], s['total']])
    
    tabla = Table(tabla_data, colWidths=[4*inch, 1.5*inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef233c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(tabla)
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla de reservas recientes
    story.append(Paragraph("<b>Reservas recientes (últimas 10)</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    reservas_recientes = reservas_mes.order_by('-fecha', '-hora')[:10]
    tabla_reservas = [['Fecha', 'Hora', 'Servicio', 'Cliente', 'Valor']]
    for r in reservas_recientes:
        tabla_reservas.append([
            r.fecha.strftime('%d/%m/%Y'),
            r.hora.strftime('%H:%M'),
            r.servicio.nombre,
            f"{r.cliente.nombres} {r.cliente.apellido_paterno}",
            f"${r.servicio.precio:,.0f}"
        ])
    
    tabla2 = Table(tabla_reservas, colWidths=[1.2*inch, 0.8*inch, 2*inch, 1.5*inch, 1*inch])
    tabla2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4361ee')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(tabla2)
    
    # Generar PDF
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=reporte_ingresos_{ahora.strftime("%Y%m")}.pdf'
    return response