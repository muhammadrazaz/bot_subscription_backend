# Generated by Django 5.1 on 2024-09-19 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_rename_payments_status_payment_payment_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice_id',
            field=models.CharField(default='3f7a3340-9431-48da-9911-3d07633e1ca3', max_length=100),
        ),
    ]