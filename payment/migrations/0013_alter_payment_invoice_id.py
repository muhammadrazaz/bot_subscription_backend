# Generated by Django 5.1 on 2024-09-27 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0012_alter_payment_invoice_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice_id',
            field=models.CharField(default='a22c4090-d2a8-4590-a9be-e21ff6b9746d', max_length=100),
        ),
    ]
