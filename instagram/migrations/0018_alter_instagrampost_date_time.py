# Generated by Django 5.1 on 2024-10-01 06:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instagram', '0017_alter_instagrampost_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instagrampost',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 1, 6, 34, 58, 276151)),
        ),
    ]