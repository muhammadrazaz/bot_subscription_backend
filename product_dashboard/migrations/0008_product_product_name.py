# Generated by Django 5.1 on 2024-09-06 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_dashboard', '0007_alter_orderitem_order_alter_orderitem_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_name',
            field=models.CharField(default='test', max_length=100),
            preserve_default=False,
        ),
    ]