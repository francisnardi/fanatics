from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import DistributionCenter, Order
from .serializers import OrderSerializer
import json
import os

# Simula salvamento no S3 (salva localmente para demonstração)
def save_to_s3_mock(data, order_id):
    with open(f'logs/{order_id}.json', 'w') as f:
        json.dump(data, f)

def allocate_order(order_data):
    try:
        quantity = order_data['quantity']
        zip_code = order_data['zip_code']
        if not (isinstance(quantity, int) and quantity > 0 and zip_code.isdigit()):
            return {"error": "Dados inválidos: quantity deve ser um inteiro positivo e zip_code deve ser numérico"}

        centers = DistributionCenter.objects.filter(stock__gte=quantity)
        if not centers.exists():
            return {"error": "Nenhum centro com estoque suficiente"}

        best_center = min(
            centers,
            key=lambda c: abs(int(c.zip_code) - int(zip_code))
        )

        best_center.stock -= quantity
        best_center.save()
        
        order = Order.objects.create(
            order_id=order_data['order_id'],
            quantity=quantity,
            zip_code=zip_code,
            center=best_center,
            status='allocated'
        )

        result = {
            "order_id": order.order_id,
            "center_id": best_center.center_id,
            "status": order.status
        }
        
        # Salva o resultado no "S3" (mock)
        save_to_s3_mock(result, order.order_id)
        
        return result

    except Exception as e:
        return {"error": str(e)}

@api_view(['POST'])
def allocate_order_view(request):
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        result = allocate_order(serializer.validated_data)
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def center_analytics_view(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Sum

    one_month_ago = timezone.now() - timedelta(days=30)
    analytics = DistributionCenter.objects.filter(
        orders__status='allocated',
        orders__created_at__gte=one_month_ago
    ).annotate(
        total_orders=Count('orders'),
        total_quantity=Sum('orders__quantity')
    ).values('center_id', 'total_orders', 'total_quantity')

    return Response(list(analytics))