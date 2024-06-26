# Generated by Django 5.0.3 on 2024-04-24 19:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('CompanyManager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DispatchItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stockId', models.CharField(max_length=50)),
                ('inDate', models.DateField()),
                ('outDate', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('location', models.CharField(max_length=50)),
                ('batchId', models.CharField(max_length=50)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('O', 'Out'), ('I', 'In')], max_length=1)),
                ('quantity', models.PositiveIntegerField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='StockDispatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noOfBoxes', models.IntegerField()),
                ('price', models.IntegerField()),
                ('tracking', models.CharField(max_length=50)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productId', models.CharField(max_length=50)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('active', models.BooleanField(default=True)),
                ('stockType', models.CharField(choices=[('SK', 'SKU'), ('CA', 'Carton')], default='SK', max_length=2)),
                ('sizeCbm', models.FloatField(blank=True, null=True)),
                ('unitPrice', models.FloatField(blank=True, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CompanyManager.company')),
            ],
        ),
    ]
