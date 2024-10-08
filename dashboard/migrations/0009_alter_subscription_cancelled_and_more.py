# Generated by Django 5.1 on 2024-10-08 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_alter_subscription_cancelled_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='cancelled',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='plan_id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='price',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='start_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='status',
            field=models.BooleanField(),
        ),
    ]
