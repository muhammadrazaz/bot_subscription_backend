# Generated by Django 5.1 on 2024-10-10 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0027_alter_payment_invoice_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice_id',
            field=models.CharField(default='3cc1a41e-ad56-4a4b-80d3-6b4eb18ed5b0', max_length=100),
        ),
    ]
