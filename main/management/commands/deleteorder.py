# from django.core.management.base import BaseCommand, CommandError
# from main.models import Orden,OrdenAsiento

# class Command(BaseCommand):
#     help = 'Elimina los asientos reservados de las ordenes no pagadas'

#     def handle(self, *args, **options):
#         orden_id=1427
#         try:
#             orden = Orden.objects.get(id=orden_id)
#         except Orden.DoesNotExist:
#             raise CommandError('La orden "%s" not existe' % orden_id)

#         precio=orden.total_dolares
#         orden.total_dolares=precio+1
#         orden.save()

#         self.stdout.write('Orden  "%s" actualizada con exito' % orden_id)

from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from datetime import timedelta
from main.models import HorarioAsiento
class Command(BaseCommand):
    help = 'Elimina los registros de la tabla horario_asiento de las ordenes que no fueron pagadas'

    def handle(self, *args, **options):        
        given_time=5 #minutes
        given_time=timedelta(minutes=given_time)

        pending_seats=HorarioAsiento.objects.filter(status='RP')
        deleted_seats=[]
        for seat in pending_seats:
            seat_time=seat.fecha.replace(tzinfo=None)
            elapsed_time=datetime.now()-seat_time
            if elapsed_time>given_time :
                seat.status='DE'
                deleted_seats.append(seat)
                seat.delete()
        if deleted_seats:
            self.stdout.write('Asientos eliminados: "%s"' % deleted_seats)

