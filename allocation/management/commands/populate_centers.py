from django.core.management.base import BaseCommand
from allocation.models import DistributionCenter

class Command(BaseCommand):
    help = 'Popula o banco com centros de distribuição, com opções para atualizar ou limpar'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Limpa todos os centros antes de popular')
        parser.add_argument('--update', action='store_true', help='Atualiza centros existentes em vez de criar novos')

    def handle(self, *args, **options):
        centers = [
            {'center_id': 'C1', 'stock': 100, 'initial_stock': 100, 'zip_code': '10000'},
            {'center_id': 'C2', 'stock': 50, 'initial_stock': 50, 'zip_code': '10003'},
            {'center_id': 'C3', 'stock': 75, 'initial_stock': 75, 'zip_code': '10005'},
        ]

        if options['reset']:
            DistributionCenter.objects.all().delete()
            self.stdout.write(self.style.WARNING('Todos os centros foram deletados.'))

        for center in centers:
            if options['update']:
                # Atualiza centros existentes ou cria novos
                DistributionCenter.objects.update_or_create(
                    center_id=center['center_id'],
                    defaults={
                        'stock': center['stock'],
                        'initial_stock': center['initial_stock'],
                        'zip_code': center['zip_code']
                    }
                )
            else:
                # Apenas cria se não existir
                _, created = DistributionCenter.objects.get_or_create(
                    center_id=center['center_id'],
                    defaults={
                        'stock': center['stock'],
                        'initial_stock': center['initial_stock'],
                        'zip_code': center['zip_code']
                    }
                )
                if not created:
                    self.stdout.write(self.style.WARNING(f'Centro {center["center_id"]} já existe, pulando...'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Centro {center["center_id"]} criado com sucesso.'))

        self.stdout.write(self.style.SUCCESS('População concluída!'))