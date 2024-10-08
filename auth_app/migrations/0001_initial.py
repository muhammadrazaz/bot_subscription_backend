# Generated by Django 5.1 on 2024-09-02 06:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('chat_id', models.CharField(max_length=50, unique=True)),
                ('telegram_username', models.CharField(blank=True, max_length=50, unique=True)),
                ('bot_father_token', models.CharField(blank=True, max_length=255)),
                ('bot_url', models.CharField(blank=True, max_length=255)),
                ('server_username', models.CharField(blank=True, max_length=255)),
                ('server_password', models.CharField(blank=True, max_length=255)),
                ('instance_dns', models.CharField(blank=True, max_length=255)),
                ('instance_username', models.CharField(blank=True, default='', max_length=255)),
                ('instance_password', models.CharField(blank=True, max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
