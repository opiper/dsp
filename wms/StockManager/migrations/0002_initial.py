# Generated by Django 5.0.3 on 2024-04-24 19:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('CourierManager', '0001_initial'),
        ('StockManager', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='agent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stock',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StockManager.product'),
        ),
        migrations.AddField(
            model_name='dispatchitems',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StockManager.stock'),
        ),
        migrations.AddField(
            model_name='stockchange',
            name='agent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stockchange',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StockManager.product'),
        ),
        migrations.AddField(
            model_name='stockdispatch',
            name='agent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stockdispatch',
            name='courierOption',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CourierManager.courieroption'),
        ),
        migrations.AddField(
            model_name='dispatchitems',
            name='stockDispatch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StockManager.stockdispatch'),
        ),
    ]
