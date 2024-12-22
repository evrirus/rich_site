from django.db import models

from users.models import CustomUser

# Create your models here.

class Car(models.Model):
    # user = models.ForeignKey(CustomUser, related_name='cars', on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)  # Автоматическое поле для ID
    max_quantity = models.IntegerField()  # Максимальное количество
    name = models.CharField(max_length=255)  # Название машины
    price = models.IntegerField()  # Цена машины
    quantity = models.IntegerField()  # Текущее количество
    plate = models.CharField(max_length=255)

    def __str__(self):
        return self.name  # Удобный вывод имени объекта
    class Meta:
        db_table = 'cars'


class Yacht(models.Model):
    # user = models.ForeignKey(CustomUser, related_name='yachts', on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)  # Автоматическое поле для ID
    max_quantity = models.IntegerField()  # Максимальное количество
    name = models.CharField(max_length=255)  # Название яхты
    price = models.IntegerField()  # Цена яхты
    quantity = models.IntegerField()  # Текущее количество
    plate = models.CharField(max_length=255)

    def __str__(self):
        return self.name  # Удобный вывод имени объекта

    class Meta:
        db_table = 'yachts'



class Houses(models.Model):
    id = models.AutoField(primary_key=True)
    class_field = models.CharField(max_length=255, db_column='class')
    floors = price = models.IntegerField(default=1)
    price = models.IntegerField()
    type_field = models.CharField(max_length=255, db_column='type')
    basement = models.JSONField(default=dict)
    district_id = models.IntegerField()
    owner = models.IntegerField(null=True)
    id_for_district = models.IntegerField()
    
    def __str__(self):
        return f"№{self.id} - D{self.district_id}"

    class Meta:
        db_table = 'houses'
    

class Districts(models.Model):
    id = models.AutoField(primary_key=True)
    district_id = models.IntegerField(default=1)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'districts'

class Items(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    attributes = models.JSONField(default=dict)
    price = models.IntegerField(null=False)
    max_quantity = models.IntegerField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'items'