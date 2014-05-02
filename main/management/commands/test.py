from django.core.management.base import BaseCommand, CommandError
class Command(BaseCommand):
    help = 'Cronjob de prueba'

    def handle(self, *args, **options):        
        self.stdout.write('Ejecuccion exitosa')

