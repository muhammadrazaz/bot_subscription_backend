# Generated by Django 5.1 on 2024-09-27 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0008_alter_payment_invoice_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice_id',
            field=models.CharField(default='4434f7ed-54e3-43db-accc-09a7ae5b7136', max_length=100),
        ),
    ]
