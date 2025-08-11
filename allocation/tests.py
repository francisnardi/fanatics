from django.test import TestCase
from rest_framework.test import APIClient
from allocation.models import DistributionCenter, Order
from allocation.views import allocate_order, log_low_stock_alert
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime

class AllocationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.center1 = DistributionCenter.objects.create(center_id='C1', stock=15, initial_stock=100, zip_code='10000')
        self.center2 = DistributionCenter.objects.create(center_id='C2', stock=8, initial_stock=50, zip_code='10003')

    def test_allocate_order_success(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O1',
            'quantity': 10,
            'zip_code': '10001'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'order_id': 'O1',
            'center_id': 'C1',
            'status': 'allocated'
        })
        self.assertTrue(os.path.exists(f'logs/O1.json'))  # Verifica log S3

    def test_insufficient_stock(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O2',
            'quantity': 50,
            'zip_code': '10001'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_invalid_quantity(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O3',
            'quantity': -5,
            'zip_code': '10001'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Quantity deve ser um inteiro positivo', response.data['quantity'])

    def test_invalid_zip_code(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O4',
            'quantity': 10,
            'zip_code': 'abc'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Zip_code deve ser numérico', response.data['zip_code'])

    def test_duplicate_order_id(self):
        Order.objects.create(order_id='O5', quantity=5, zip_code='10001', center=self.center1, status='allocated')
        response = self.client.post('/allocate/', {
            'order_id': 'O5',
            'quantity': 10,
            'zip_code': '10001'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Order_id já existe', response.data['non_field_errors'])

    def test_low_stock_alert_generation(self):
        self.center1.stock = 19
        self.center1.save()
        response = self.client.post('/allocate/', {
            'order_id': 'O6',
            'quantity': 1,
            'zip_code': '10000'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists(f'alerts/{self.center1.center_id}_alert.json'))

    def test_api_key_authentication(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O7',
            'quantity': 10,
            'zip_code': '10001'
        }, format='json')
        self.assertEqual(response.status_code, 401)
        response = self.client.post('/allocate/', {
            'order_id': 'O8',
            'quantity': 10,
            'zip_code': '10001'
        }, format='json', HTTP_API_KEY='wrong-key')
        self.assertEqual(response.status_code, 401)

    def test_analytics_endpoint(self):
        Order.objects.create(order_id='O9', quantity=5, zip_code='10001', center=self.center1, status='allocated')
        response = self.client.get('/analytics/', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue(any(center['center_id'] == 'C1' and center['low_stock_alert'] for center in data))

    def test_analytics_with_date_filter(self):
        Order.objects.create(order_id='O10', quantity=5, zip_code='10001', center=self.center1, status='allocated', created_at=timezone.now() - timedelta(days=60))
        response = self.client.get('/analytics/?from_date=2025-08-01', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertFalse(any(center['center_id'] == 'C1' and center['total_orders'] > 0 for center in data))  # Pedido fora do período

    def test_openapi_schema(self):
        response = self.client.get('/schema/', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)

    def test_negative_stock_validation(self):
        self.center1.stock = -1
        with self.assertRaises(ValueError):
            self.center1.save()