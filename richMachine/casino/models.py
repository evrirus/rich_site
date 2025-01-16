from django.db import models
from icecream import ic

from users.models import CustomUser




class FreeSpinType(models.Model):
    name = models.CharField(max_length=100)  # Название типа фриспина (например, "10 фриспинов с $10 ставкой")
    description = models.TextField()  # Описание типа фриспина
    prize_value = models.IntegerField()  # Количество фриспинов
    stake_value = models.IntegerField()  # Ставка для фриспинов
    currency = models.CharField(max_length=10, default='USD')  # Валюта (по умолчанию доллар)

    def __str__(self):
        return self.name


class CasinoModel(models.Model):
    user = models.ForeignKey(CustomUser, related_name='casino', on_delete=models.CASCADE)
    max_win = models.IntegerField(default=30)
    max_win_time = models.DateTimeField(auto_now_add=False, null=True)
    max_cash_win_type = models.CharField(default='USD', max_length=100, null=True)
    freespins_available = models.IntegerField(default=0)  # Сколько фриспинов осталось
    current_stake = models.IntegerField()  # Текущая ставка пользователя
    free_spin_types = models.ManyToManyField(FreeSpinType, related_name='casino_freespins')  # Связь с типами фриспинов
    # is_authenticated = models.BooleanField(default=False)


    def __str__(self):
        return f"Casino {self.user.username}"

    def add_freespins(self, free_spin_type):
        """Добавляет фриспины определенного типа пользователю."""
        # Убедитесь, что переданный free_spin_type является экземпляром модели FreeSpinType
        if not isinstance(free_spin_type, FreeSpinType):
            raise ValueError("Invalid FreeSpinType provided")

        # Увеличиваем количество фриспинов на prize_value, которое определено в типе фриспинов
        self.freespins_available += free_spin_type.prize_value
        # Устанавливаем ставку для фриспинов, равную stake_value из типа фриспинов
        self.current_stake = free_spin_type.stake_value
        # Добавляем тип фриспинов к пользователю (сохраняем связь)
        self.free_spin_types.add(free_spin_type)
        # Сохраняем изменения в базе данных
        self.save()

        # Можно вернуть информацию о добавленных фриспинах для проверки
        return {
            "freespins_available": self.freespins_available,
            "current_stake": self.current_stake,
            "free_spin_types": [spin.name for spin in self.free_spin_types.all()]
        }

    def use_freespin(self):
        """Использовать один фриспин."""
        ic(self.freespins_available)
        if self.freespins_available > 0:
            self.freespins_available -= 1  # Уменьшаем количество фриспинов
            self.save()  # Сохраняем изменения в базе данных
            return True  # Фриспин успешно использован
        return False  # Нет доступных фриспинов

    class Meta:
        db_table = "casino"

