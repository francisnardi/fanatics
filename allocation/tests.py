from django.test import TestCase
from rest_framework.test import APIClient
from allocation.models import DistributionCenter
from allocation.views import allocate_order

class AllocationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        DistributionCenter.objects.create(center_id='C1', stock=15, zip_code='10000')
        DistributionCenter.objects.create(center_id='C2', stock=8, zip_code='10003')

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
        self.assertEqual(result, {
            'order_id': 'O3',
            'center_id': 'C2',
            'status': 'allocated'
        })