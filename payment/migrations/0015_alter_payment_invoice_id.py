# Generated by Django 5.1 on 2024-10-01 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0014_alter_payment_invoice_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice_id',
            field=models.CharField(default='4bd1875b-4285-438f-8260-f2ee5a5cfc7e', max_length=100),
        ),
    ]
