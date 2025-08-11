def test_api_key_authentication(self):
    # Testa sem API Key
    response = self.client.post('/allocate/', {
        'order_id': 'O6',
        'quantity': 10,
        'zip_code': '10001'
    }, format='json')
    self.assertEqual(response.status_code, 401)  # Unauthorized

    # Testa com API Key errada (assumindo API Key em settings)
    response = self.client.post('/allocate/', {
        'order_id': 'O7',
        'quantity': 10,
        'zip_code': '10001'
    }, format='json', HTTP_API_KEY='wrong-key')
    self.assertEqual(response.status_code, 401)

def test_low_stock_alert_generation(self):
    # Força estoque baixo e aloca para acionar alerta
    self.center1.stock = 19  # <20% de 100
    self.center1.save()
    order_data = {'order_id': 'O8', 'quantity': 1, 'zip_code': '10000'}
    result = allocate_order(order_data)
    self.assertTrue(os.path.exists(f'alerts/{self.center1.center_id}_alert.json'))