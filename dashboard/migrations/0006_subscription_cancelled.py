# Generated by Django 5.1 on 2024-09-15 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_remove_subscription_cancelled_subscription_plan_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='cancelled',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
