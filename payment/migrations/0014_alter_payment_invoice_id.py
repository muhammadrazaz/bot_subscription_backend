# Generated by Django 5.1 on 2024-10-01 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0013_alter_payment_invoice_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice_id',
            field=models.CharField(default='cbbc7210-1cd7-41b6-9a1e-aff8bcb02803', max_length=100),
        ),
    ]
