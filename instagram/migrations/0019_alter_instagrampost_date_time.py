# Generated by Django 5.1 on 2024-10-01 15:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instagram', '0018_alter_instagrampost_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instagrampost',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 1, 15, 16, 31, 902540)),
        ),
    ]