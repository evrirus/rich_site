# Generated by Django 5.1 on 2024-12-17 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magazine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Districts',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('district_id', models.IntegerField(default=1)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
    ]
