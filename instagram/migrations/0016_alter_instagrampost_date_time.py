# Generated by Django 5.1 on 2024-09-27 13:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instagram', '0015_rename_propmt_chatgptprompt_prompt_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instagrampost',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 27, 13, 24, 19, 679821)),
        ),
    ]
