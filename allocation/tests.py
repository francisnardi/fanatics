from django.test import TestCase
from rest_framework.test import APIClient
from allocation.models import DistributionCenter, Order
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import os

class TestAllocation(TestCase):
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
        self.assertTrue(os.path.exists('logs/O1.json'))  # Test S3 mock

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
        self.assertIn('Quantity deve ser um inteiro positivo', str(response.data))

    def test_invalid_zip_code_serializer(self):
        response = self.client.post('/allocate/', {
            'order_id': 'O4',
            'quantity': 10,
            'zip_code': 'abc'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Zip_code deve ser numérico', str(response.data))

    def test_duplicate_order_id_serializer(self):
        Order.objects.create(order_id='O5', quantity=5, zip_code='10001', center=self.center1, status='allocated')
        response = self.client.post('/allocate/', {
            'order_id': 'O5',
            'quantity': 10,
            'zip_code': '10001'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Order_id já existe', str(response.data))

    def test_low_stock_alert(self):
        self.center1.stock = 19
        self.center1.save()
        response = self.client.post('/allocate/', {
            'order_id': 'O6',
            'quantity': 1,
            'zip_code': '10000'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists('alerts/C1_alert.json'))  # Test CloudWatch mock

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
        self.assertTrue(any(d['center_id'] == 'C1' and d['low_stock_alert'] for d in data))

    def test_analytics_with_date_filter(self):
        Order.objects.create(order_id='O10', quantity=5, zip_code='10001', center=self.center1, status='allocated', created_at=timezone.now() - timedelta(days=60))
        response = self.client.get('/analytics/?from_date=' + timezone.now().strftime('%Y-%m-%d'), HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertFalse(any(d['center_id'] == 'C1' and d['total_orders'] > 0 for d in data))

    def test_negative_stock_validation_model(self):
        self.center1.stock = -1
        with self.assertRaises(ValueError):
            self.center1.save()

    def test_initial_stock_validation_model(self):
        self.center1.initial_stock = 10
        self.center1.stock = 15
        with self.assertRaises(ValueError):
            self.center1.save()

    def test_openapi_schema(self):
        response = self.client.get('/schema/', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)

    def test_empty_analytics(self):
        response = self.client.get('/analytics/', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)  # Two centers, no orders

    def test_no_centers_available(self):
        DistributionCenter.objects.all().delete()
        response = self.client.post('/allocate/', {
            'order_id': 'O11',
            'quantity': 10,
            'zip_code': '10001'
        }, format='json', HTTP_API_KEY=settings.API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_populate_centers_command(self):
        DistributionCenter.objects.all().delete()
        from django.core.management import call_command
        call_command('populate_centers')
        self.assertEqual(DistributionCenter.objects.count(), 3)  # C1, C2, C3