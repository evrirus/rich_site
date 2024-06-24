from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone

import datetime

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
        "next_job": datetime.datetime.utcfromtimestamp(1)
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

class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        user = self.create_user(email=email, username=username, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class AbstractUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        abstract = True

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name="%(class)s_groups",
        related_query_name="%(class)s_group",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name="%(class)s_user_permissions",
        related_query_name="%(class)s_user_permission",
    )

class MyUser(AbstractUser):
    server_id = models.IntegerField(default=1)
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

    class Meta:
        db_table = 'lerkalalka'

    def __str__(self):
        return self.username
