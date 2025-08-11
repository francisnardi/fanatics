from django.test import TestCase
from rest_framework.test import APIClient
from allocation.models import DistributionCenter, Order
from allocation.views import allocate_order, log_low_stock_alert

class AllocationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.center1 = DistributionCenter.objects.create(center_id='C1', stock=15, initial_stock=100, zip_code='10000')
        self.center2 = DistributionCenter.objects.create(center_id='C2', stock=8, initial_stock=50, zip_code='10003')

    def test_allocate_order(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O1',
            'quantity': 10,
            'zip_code': '10001'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'order_id': 'O1',
            'center_id': 'C1',
            'status': 'allocated'
        })

    def test_insufficient_stock(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O2',
            'quantity': 50,
            'zip_code': '10001'
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_allocate_order_logic(self):
        order_data = {'order_id': 'O3', 'quantity': 5, 'zip_code': '10002'}
        result = allocate_order(order_data)
        self.assertEqual(result['center_id'], 'C2')

    def test_low_stock_alert(self):
        # Força estoque baixo
        self.center1.stock = 10  # <20% de 100
        self.center1.save()
        log_low_stock_alert(self.center1)
        self.assertTrue(os.path.exists(f'alerts/{self.center1.center_id}_alert.json'))

    def test_analytics(self):
        # Cria um pedido para testar
        Order.objects.create(order_id='O4', quantity=5, zip_code='10001', center=self.center1, status='allocated')
        response = self.client.get('/analytics/')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue(any(center['center_id'] == 'C1' and center['low_stock_alert'] for center in data))