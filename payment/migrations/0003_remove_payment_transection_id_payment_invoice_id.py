# Generated by Django 5.1 on 2024-09-17 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_alter_payment_date_time_alter_payment_transection_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='transection_id',
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice_id',
            field=models.CharField(default='6b24df04-3900-4670-a684-65793f5d24c9', max_length=100),
        ),
    ]
