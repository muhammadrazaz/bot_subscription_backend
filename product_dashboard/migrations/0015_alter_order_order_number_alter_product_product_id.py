# Generated by Django 5.1 on 2024-09-27 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_dashboard', '0014_remove_orderitem_item_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_id',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]