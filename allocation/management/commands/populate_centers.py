from django.core.management.base import BaseCommand
from allocation.models import DistributionCenter

class Command(BaseCommand):
    help = 'Popula o banco com centros de distribuição'

    def handle(self, *args, **kwargs):
        centers = [
            {'center_id': 'C1', 'stock': 100, 'zip_code': '10000'},
            {'center_id': 'C2', 'stock': 50, 'zip_code': '10003'},
            {'center_id': 'C3', 'stock': 75, 'zip_code': '10005'},
        ]
        for center in centers:
            DistributionCenter.objects.get_or_create(**center)
        self.stdout.write(self.style.SUCCESS('Centros de distribuição populados com sucesso!'))