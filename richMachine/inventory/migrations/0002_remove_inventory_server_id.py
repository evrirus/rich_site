# Generated by Django 5.1 on 2025-01-02 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventory',
            name='server_id',
        ),
    ]
