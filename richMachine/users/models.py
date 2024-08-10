# from django.db import models

from django.contrib.auth.models import BaseUserManager
from django.db.models import Max
from icecream import ic


def default_nickname():
    return {
        "name": 'пользователь',
        "max": 15,
        "link": False
    }

def default_money():
    return {
        'cash': 10000,
        'bank': 0,
        'dollar': 0,
        'bitcoin': 0,
    }

def default_job():
    return {
        "title": None,
        "level": 1,
        "salary": 0,
        "description": None,
        "tasks_completed": 0,
        "next_job": 'now' # timezone.now()
    }

def default_house():
    return {
        "houses": [],
        "maxPlaces": 1,
        "order": [],
        "offer": []
    }

def default_car():
    return {
        "cars": [],
        "maxPlaces": 2,
        "order": [],
        "offer": []
    }

def default_yacht():
    return {
        "yachts": [],
        "maxPlaces": 1,
        "order": [],
        "offer": []
    }

def default_couple():
    return {
        'user_id': None,
        'order': [],
        'offer': []
    }



from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from djongo import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from bson import ObjectId
from django.db.models import Max
from icecream import ic

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_('The Username must be set'))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    _id = models.ObjectIdField(primary_key=True, editable=False, default=ObjectId)  # Удалить это поле
    server_id = models.IntegerField(default=0)
    user_id = models.IntegerField(blank=True, null=True)
    donate_balance = models.IntegerField(default=0)
    job_lvl = models.IntegerField(default=1)
    nickname = models.JSONField(default=default_nickname)
    money = models.JSONField(default=default_money, db_index=False)
    job = models.JSONField(default=default_job, db_index=False)
    house = models.JSONField(default=default_house, db_index=False)
    car = models.JSONField(default=default_car, db_index=False)

    yacht = models.JSONField(default=default_yacht, db_index=False)
    couple = models.JSONField(default=default_couple, db_index=False)
    registration = models.DateField(auto_now=True)
    language = models.CharField(max_length=10, default='ru')
    username_tg = models.CharField(max_length=100, default=None)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # Add any additional required fields here

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.server_id:
            max_server_id = CustomUser.objects.all().aggregate(Max('server_id')).get('server_id__max') or 0
            self.server_id = max_server_id + 1
        super().save(*args, **kwargs)
