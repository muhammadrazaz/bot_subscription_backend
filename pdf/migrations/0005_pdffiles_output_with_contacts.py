# Generated by Django 5.1 on 2024-09-26 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdf', '0004_pdffiles_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='pdffiles',
            name='output_with_contacts',
            field=models.CharField(default='', max_length=255),
        ),
    ]
