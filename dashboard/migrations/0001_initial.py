# Generated by Django 5.1 on 2024-09-02 06:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('status', models.BooleanField()),
                ('payment', models.CharField(max_length=255)),
                ('cancelled', models.BooleanField()),
                ('subscription_id', models.CharField(max_length=255)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('plan', models.CharField(max_length=255)),
                ('price', models.IntegerField()),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth_app.userprofile')),
            ],
        ),
    ]
