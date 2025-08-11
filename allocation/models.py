from django.db import models

class DistributionCenter(models.Model):
    center_id = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField()
    zip_code = models.CharField(max_length=10)

    class Meta:
        db_table = 'distribution_centers'

    def __str__(self):
        return self.center_id

class Order(models.Model):
    order_id = models.CharField(max_length=50, unique=True)
    quantity = models.IntegerField()
    zip_code = models.CharField(max_length=10)
    center = models.ForeignKey(DistributionCenter, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return self.order_id