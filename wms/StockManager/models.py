from django.db import models
from CompanyManager.models import Company
from warehouse.models import CustomUser
from CourierManager.models import CourierOption


class Product(models.Model):
    productId = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    stockChoices = [
        ('SK', 'SKU'),
        ('CA', 'Carton')
    ]
    stockType = models.CharField(
        max_length=2,
        choices=stockChoices,
        default='SK'
    )
    sizeCbm = models.FloatField(blank=True, null=True) # Total size in CBM
    unitPrice = models.FloatField(blank=True,null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)


class StockChange(models.Model):
    categoryChoices = [
        ('O','Out'),
        ('I','In')
    ]
    category = models.CharField(
        max_length=1,
        choices=categoryChoices
    )
    quantity = models.PositiveIntegerField()
    date = models.DateField()

    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Stock(models.Model):
    stockId = models.CharField(max_length=50)
    inDate = models.DateField() # Date of input
    outDate = models.DateField(blank=True,null=True) # Date of output
    notes = models.TextField(blank=True)
    location = models.CharField(max_length=50, blank=False)
    batchId = models.CharField(max_length=50, blank=False)
    active = models.BooleanField(default=True)

    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class StockDispatch(models.Model):
    noOfBoxes = models.IntegerField()
    price = models.IntegerField()
    tracking = models.CharField(max_length=50)
    date = models.DateField()

    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    courierOption = models.ForeignKey(CourierOption, on_delete=models.CASCADE)


class DispatchItems(models.Model):
    stockDispatch = models.ForeignKey(StockDispatch, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)