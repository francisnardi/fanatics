from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'quantity', 'zip_code']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity deve ser um inteiro positivo.")
        return value

    def validate_zip_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Zip_code deve ser numérico.")
        return value

    def validate(self, data):
        # Verifica se order_id já existe
        if Order.objects.filter(order_id=data['order_id']).exists():
            raise serializers.ValidationError("Order_id já existe.")
        return data