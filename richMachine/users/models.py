
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
# from django.utils.translation import gettext_lazy as _

from django.db.models import Max

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

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
        "level": 1,
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


# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
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
    # _id = models.ObjectIdField(primary_key=True, editable=False, default=0)  # Удалить это поле

    server_id = models.IntegerField(default=0, primary_key=True)
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

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        db_table = 'users'