from django.db import models
from StockManager.models import Product
from warehouse.models import CustomUser


class ServiceList(models.Model):
    name = models.CharField(max_length=50)
    unitPrice  = models.DecimalField(max_digits=10, decimal_places=2)


class ServiceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    serviceType = models.ForeignKey(ServiceList, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateField()
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class LabelChangeService(ServiceHistory):
    newProduct = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='newProduct')