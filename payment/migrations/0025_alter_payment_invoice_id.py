# Generated by Django 5.1 on 2024-10-10 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0024_alter_payment_invoice_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice_id',
            field=models.CharField(default='398c981a-cafd-49ca-bc3a-5fe1c8c85b5a', max_length=100),
        ),
    ]
