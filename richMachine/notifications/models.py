from django.db import models
from users.models import CustomUser


# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification {self.user.username} - {self.pk}"
    class Meta:
        db_table = "notification"
