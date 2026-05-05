# reservas/management/commands/limpiar_reservas_pasadas.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from reservas.models import Reserva
from datetime import date

class Command(BaseCommand):
    help = 'Elimina o archiva las reservas con fecha pasada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivar',
            action='store_true',
            help='Archivar en lugar de eliminar',
        )

    def handle(self, *args, **options):
        hoy = date.today()
        archivar = options['archivar']
        
        # Reservas con fecha anterior a hoy
        reservas_pasadas = Reserva.objects.filter(fecha__lt=hoy)
        
        count = reservas_pasadas.count()
        
        if count == 0:
            self.stdout.write(f"✅ No hay reservas pasadas para procesar")
            return
        
        if archivar:
            # Archivar (marcar como archivadas)
            reservas_pasadas.update(archivado=True)
            self.stdout.write(f"📦 {count} reservas archivadas correctamente")
        else:
            # Eliminar
            reservas_pasadas.delete()
            self.stdout.write(f"🗑️ {count} reservas eliminadas correctamente")
        
        # Mostrar detalles
        self.stdout.write(f"\n📊 Resumen de reservas actuales:")
        self.stdout.write(f"   - Reservas activas: {Reserva.objects.filter(fecha__gte=hoy).count()}")
        self.stdout.write(f"   - Reservas pasadas: {Reserva.objects.filter(fecha__lt=hoy).count()}")