# recordatorios/management/commands/enviar_recordatorios.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta
from reservas.models import Reserva
from django.conf import settings

class Command(BaseCommand):
    help = 'Envía recordatorios de citas programadas'

    def handle(self, *args, **options):
        # Fecha de mañana
        manana = timezone.now().date()  # Para probar con reservas de hoy
        
        # Buscar reservas para mañana
        reservas = Reserva.objects.filter(
            fecha=manana,
            estado='pendiente'
        ).select_related('cliente', 'servicio', 'profesional', 'negocio')
        
        self.stdout.write(f"🔍 {reservas.count()} reservas encontradas para {manana}")
        
        enviados = 0
        errores = 0
        
        for reserva in reservas:
            try:
                cliente_nombre = reserva.cliente.nombres if reserva.cliente else reserva.nombre_cliente
                cliente_email = reserva.cliente.correo if reserva.cliente else reserva.correo_cliente
                
                if not cliente_email:
                    self.stdout.write(f"⚠️ No email para reserva {reserva.id}")
                    continue
                
                # Crear contenido HTML
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f4f4f4;">
                    <div style="background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        
                        <div style="background: #ef233c; color: white; padding: 20px; text-align: center;">
                            <h2 style="margin: 0;">🔔 Recordatorio de reserva</h2>
                        </div>
                        
                        <div style="padding: 25px;">
                            <p style="font-size: 16px;">Hola <strong>{cliente_nombre}</strong>,</p>
                            <p>Te recordamos que mañana tienes una cita programada.</p>
                            
                            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                                <p><strong>📋 Detalles:</strong></p>
                                <p>📅 Fecha: <strong>{reserva.fecha.strftime('%d/%m/%Y')}</strong></p>
                                <p>⏰ Hora: <strong>{reserva.hora.strftime('%H:%M')}</strong></p>
                                <p>💈 Servicio: <strong>{reserva.servicio.nombre}</strong></p>
                                <p>👤 Profesional: <strong>{reserva.profesional.nombre}</strong></p>
                            </div>
                            
                            <div style="text-align: center; margin-top: 20px;">
                                <a href="http://127.0.0.1:8000/reservar/" style="background: #ef233c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                                    Ver detalles
                                </a>
                            </div>
                        </div>
                        
                        <div style="background: #f4f4f4; text-align: center; padding: 15px; font-size: 12px; color: #666;">
                            <p>Si no puedes asistir, te pedimos cancelar con anticipación.</p>
                            <p>© TURNOCLIC - Sistema de gestión de reservas</p>
                        </div>
                    </div>
                </div>
                """
                
                # Enviar correo
                msg = EmailMultiAlternatives(
                    subject=f"🔔 Recordatorio - {reserva.servicio.nombre} mañana",
                    body=f"Hola {cliente_nombre}, te recordamos tu cita mañana a las {reserva.hora.strftime('%H:%M')}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[cliente_email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                
                enviados += 1
                self.stdout.write(f"✅ Recordatorio enviado a {cliente_email}")
                
            except Exception as e:
                errores += 1
                self.stdout.write(f"❌ Error con reserva {reserva.id}: {e}")
        
        self.stdout.write(f"\n📊 Resumen:")
        self.stdout.write(f"   - Enviados: {enviados}")
        self.stdout.write(f"   - Errores: {errores}")