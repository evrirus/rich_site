# Generated by Django 5.1 on 2024-12-19 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magazine', '0002_districts'),
    ]

    operations = [
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('attributes', models.JSONField(default=dict)),
                ('price', models.IntegerField()),
                ('max_quantity', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'items',
            },
        ),
        migrations.AlterModelTable(
            name='car',
            table='cars',
        ),
        migrations.AlterModelTable(
            name='districts',
            table='districts',
        ),
        migrations.AlterModelTable(
            name='houses',
            table='houses',
        ),
        migrations.AlterModelTable(
            name='yacht',
            table='yachts',
        ),
    ]