import uuid

from django.db import models
from django.utils import timezone
from users.models import CustomUser



# Create your models here.
class UserToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=36, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)