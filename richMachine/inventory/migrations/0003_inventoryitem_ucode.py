# Generated by Django 5.1 on 2025-01-08 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_remove_inventory_server_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryitem',
            name='ucode',
            field=models.CharField(max_length=50, null=True),
        ),
    ]