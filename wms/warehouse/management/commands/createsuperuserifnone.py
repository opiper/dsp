from django.core.management.base import BaseCommand
from warehouse.models import CustomUser
from ServiceManager.models import ServiceList
import os

class Command(BaseCommand):
    help = 'Create superuser if none exists'

    def handle(self, *args, **kwargs):
        if not CustomUser.objects.exists():
            user = CustomUser.objects.create_superuser(os.getenv('username'), os.getenv('email'), os.getenv('password'))
            user.role = 3
            user.save()
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser creation skipped: A user already exists'))

        if not ServiceList.objects.exists():
            ServiceList.objects.bulk_create([
                ServiceList(name='Label Change', unitPrice=0),
                ServiceList(name='Assorting', unitPrice=0),
                ServiceList(name='Change Card', unitPrice=0),
                ServiceList(name='Clearance', unitPrice=0),
                ServiceList(name='Destroy', unitPrice=0),
                ServiceList(name='Inspection', unitPrice=0),
                ServiceList(name='Photo', unitPrice=0),
            ])
            self.stdout.write(self.style.SUCCESS('Service List created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Service List creation skipped: A service already exists'))