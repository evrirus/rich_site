# Generated by Django 5.1 on 2025-01-13 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casino', '0008_alter_casinomodel_max_cash_win_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casinomodel',
            name='is_authenticated',
        ),
    ]
