from django.db import models
from users.models import CustomUser

# Create your models here.

class Inventory(models.Model):
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
    ucode = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"{self.item_type} in inventory {self.inventory.id}"

    class Meta:
        db_table = "inventoryitem"