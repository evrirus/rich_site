# Generated by Django 5.1 on 2025-01-13 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casino', '0004_delete_bonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='casinomodel',
            name='max_win_time',
            field=models.DateTimeField(null=True),
        ),
    ]
