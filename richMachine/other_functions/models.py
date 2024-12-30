import uuid

from django.db import models
from django.utils import timezone
from users.models import CustomUser




    
class Inventory(models.Model):
    server_id = models.IntegerField()  # ID сервера
    max_quantity = models.IntegerField(default=30)  # Максимальное количество предметов в инвентаре
    user = models.ForeignKey(CustomUser, related_name='inventories', on_delete=models.CASCADE)

    def __str__(self):
        return f"Inventory {self.user.username}"

    class Meta:
        db_table = "inventory"

class InventoryItem(models.Model):
    inventory = models.ForeignKey(Inventory, related_name='items', on_delete=models.CASCADE)
    item_type = models.CharField(max_length=100)  # Тип предмета (например, "videocard")
    item_id = models.IntegerField()

    def __str__(self):
        return f"{self.item_type} in inventory {self.inventory.id}"

    class Meta:
        db_table = "inventoryitem"



class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification {self.user.username} - {self.pk}"
    class Meta:
        db_table = "notification"

