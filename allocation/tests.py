from django.test import TestCase
from rest_framework.test import APIClient
from allocation.models import DistributionCenter, Order
from allocation.views import allocate_order
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import os

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
        self.assertEqual(response.data['center_id'], 'C1')
        self.assertTrue(os.path.exists(f'logs/O1.json'))  # Cobrindo log S3

    def test_insufficient_stock(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O2',
            'quantity': 50,
            'zip_code': '10001'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_invalid_quantity_serializer(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O3',
            'quantity': -5,
            'zip_code': '10001'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Quantity deve ser um inteiro positivo', response.data['quantity'][0])

    def test_invalid_zip_code_serializer(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O4',
            'quantity': 10,
            'zip_code': 'abc'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Zip_code deve ser numérico', response.data['zip_code'][0])

    def test_duplicate_order_id_serializer(self):
        Order.objects.create(order_id='O5', quantity=5, zip_code='10001', center=self.center1, status='allocated')
        response = self.client.post('/allocate/', {
            'order_id': 'O5',
            'quantity': 10,
            'zip_code': '10001'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Order_id já existe', response.data['non_field_errors'][0])

    def test_low_stock_alert(self):
        self.center1.stock = 19
        self.center1.save()
        allocate_order({'order_id': 'O6', 'quantity': 1, 'zip_code': '10000'})
        self.assertTrue(os.path.exists(f'alerts/C1_alert.json'))  # Cobrindo alerta CloudWatch

    def test_api_key_authentication(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O7',
            'quantity': 10,
            'zip_code': '10001'
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_analytics_endpoint(self):
        Order.objects.create(order_id='O8', quantity=5, zip_code='10001', center=self.center1, status='allocated')
        response = self.client.get('/analytics/', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue(any(d['center_id'] == 'C1' and d['low_stock_alert'] for d in data))

    def test_analytics_with_date_filter(self):
        Order.objects.create(order_id='O9', quantity=5, zip_code='10001', center=self.center1, status='allocated', created_at=timezone.now() - timedelta(days=60))
        response = self.client.get('/analytics/?from_date=' + timezone.now().strftime('%Y-%m-%d'), HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertFalse(any(d['center_id'] == 'C1' and d['total_orders'] > 0 for d in data))  # Pedido fora do período

    def test_negative_stock_validation_model(self):
        self.center1.stock = -1
        with self.assertRaises(ValueError):
            self.center1.save()

    def test_openapi_schema(self):
        response = self.client.get('/schema/', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)