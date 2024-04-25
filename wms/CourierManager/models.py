from django.db import models


class Courier(models.Model):
    name = models.CharField(max_length=50)


class CourierOption(models.Model):
    boxChoices = [
        (1,'Small Box'),
        (2, 'Medium Box'),
        (3, 'Large Box'),
        (4,'No Box'),
        (5,'Own Box'),
        (6, 'Bag')
    ]
    box = models.IntegerField(
        choices=boxChoices,
        default=None,
        blank=False
    )
    priceChoices = [
        (1,'Standard Price'),
        (2,'High Price')
    ]
    price = models.IntegerField(
        choices=priceChoices,
        default=None,
        blank=False
    )
    dropship = models.BooleanField(blank=True)
    envelope = models.BooleanField(blank=True)
    finalPrice = models.FloatField()
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)