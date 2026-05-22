from django.core.management.base import BaseCommand
from account.models import CustomUser

class Command(BaseCommand):
    def handle(self, *args, **options):
        CustomUser.objects.create_superuser(
            phone='09338484618',
            fullname='Salar Khosravi',
            email='salar.khosravi@gmail.com',
            password='Admin@123'
        )
