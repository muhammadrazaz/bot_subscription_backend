# Generated by Django 5.1 on 2024-09-17 13:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instagram', '0008_alter_instagrampost_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instagrampost',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 17, 13, 12, 15, 793117)),
        ),
    ]
