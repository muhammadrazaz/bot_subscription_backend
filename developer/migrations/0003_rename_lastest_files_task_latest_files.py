# Generated by Django 5.1 on 2024-10-01 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('developer', '0002_alter_task_developer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='lastest_files',
            new_name='latest_files',
        ),
    ]