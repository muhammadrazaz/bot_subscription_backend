# Generated by Django 5.1 on 2024-10-10 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0025_alter_payment_invoice_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice_id',
            field=models.CharField(default='e8f0d8cc-293a-4382-a42a-4def223398b2', max_length=100),
        ),
    ]
