from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import DistributionCenter, Order
from .serializers import OrderSerializer
import json
import os
import boto3
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum

# Directory for mocks
os.makedirs('alerts', exist_ok=True)

# Function to log alerts (simulating AWS CloudWatch Logs)
def log_low_stock_alert(center):
    alert_message = {
        "center_id": center.center_id,
        "stock_remaining": center.stock,
        "initial_stock": center.initial_stock,
        "timestamp": timezone.now().isoformat(),
        "message": "Low stock! Replenish immediately."
    }
    
    # Mock: Save to local file
    with open(f'alerts/{center.center_id}_alert.json', 'w') as f:
        json.dump(alert_message, f)
    
    # For real AWS: Uncomment and configure credentials
    # client = boto3.client('logs', region_name='us-east-1')
    # client.put_log_events(
    #     logGroupName='fanatics-alerts',
    #     logStreamName='low-stock',
    #     logEvents=[{'timestamp': int(timezone.now().timestamp() * 1000), 'message': json.dumps(alert_message)}]
    # )

def allocate_order(order_data):
    try:
        quantity = order_data['quantity']
        zip_code = order_data['zip_code']

        centers = DistributionCenter.objects.filter(stock__gte=quantity)
        if not centers.exists():
            return {"error": "No distribution center with sufficient stock"}

        best_center = min(
            centers,
            key=lambda c: abs(int(c.zip_code) - int(zip_code))
        )

        # Extra robustness: Prevent negative stock
        if best_center.stock - quantity < 0:
            return {"error": "Insufficient stock after verification"}

        best_center.stock -= quantity
        best_center.save()
        
        order = Order.objects.create(
            order_id=order_data['order_id'],
            quantity=quantity,
            zip_code=zip_code,
            center=best_center,
            status='allocated'
        )

        # Check and log alert if stock is low
        if best_center.is_low_stock():
            log_low_stock_alert(best_center)

        result = {
            "order_id": order.order_id,
            "center_id": best_center.center_id,
            "status": order.status
        }
        
        # Save the result to "S3" (mock, as before)
        with open(f'logs/{order.order_id}.json', 'w') as f:
            json.dump(result, f)
        
        return result

    except ValueError as e:
        return {"error": f"Value error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

@api_view(['POST'])
@authentication_classes([BasicAuthentication])  # Adds basic authentication
@permission_classes([IsAuthenticated])
def allocate_order_view(request):
    # For simple API Key: Verify header (demo; use real authentication in production)
    api_key = request.headers.get('Api-Key')
    if api_key != settings.API_KEY:
        return Response({"error": "Invalid API key"}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        result = allocate_order(serializer.validated_data)
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def center_analytics_view(request):
    one_month_ago = timezone.now() - timedelta(days=30)
    if from_date:
        try:
            one_month_ago = datetime.fromisoformat(from_date)
        except ValueError:
            return Response({"error": "Invalid from_date format (use YYYY-MM-DD)"}, status=400)
    analytics = DistributionCenter.objects.annotate(
        total_orders=Count('orders', filter=models.Q(orders__status='allocated', orders__created_at__gte=one_month_ago)),
        total_quantity=Sum('orders__quantity', filter=models.Q(orders__status='allocated', orders__created_at__gte=one_month_ago)),
        remaining_percentage=models.ExpressionWrapper(
            models.Value(100.0) * models.F('stock') / models.F('initial_stock'),
            output_field=models.FloatField()
        ),
        low_stock_alert=models.Case(
            models.When(stock__lt=0.2 * models.F('initial_stock'), then=models.Value(True)),
            default=models.Value(False),
            output_field=models.BooleanField()
        )
    ).values('center_id', 'stock', 'initial_stock', 'remaining_percentage', 'low_stock_alert', 'total_orders', 'total_quantity')

    return Response(list(analytics))