# Generated by Django 5.1 on 2024-12-17 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('max_quantity', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('price', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('plate', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Houses',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('class_field', models.CharField(db_column='class', max_length=255)),
                ('floors', models.IntegerField(default=1)),
                ('price', models.IntegerField()),
                ('type_field', models.CharField(db_column='type', max_length=255)),
                ('basement', models.JSONField(default=dict)),
                ('district_id', models.IntegerField()),
                ('owner', models.IntegerField(null=True)),
                ('id_for_district', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Yacht',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('max_quantity', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('price', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('plate', models.CharField(max_length=255)),
            ],
        ),
    ]