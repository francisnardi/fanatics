from django.db import models

class DistributionCenter(models.Model):
    center_id = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField()
    initial_stock = models.IntegerField(default=100)  
    zip_code = models.CharField(max_length=10)

    class Meta:
        db_table = 'distribution_centers'

    def __str__(self):
        return self.center_id

    def is_low_stock(self):
        return self.stock < 0.2 * self.initial_stock  

    def save(self, *args, **kwargs):
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")
        super().save(*args, **kwargs)

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