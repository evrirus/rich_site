from django.db import models

# Create your models here.
class Jobs(models.Model):
    JOB_LEVELS = [
        (1, 'Дворник'),
        (2, 'Риелтор'),
        (3, 'Банкир'),
        (4, 'Автодилер'),
        (5, 'Коллекционер'),
        (6, 'Трейдер'),
        (7, 'Крупье'),
    ]

    name = models.CharField(max_length=100, unique=True)  # Название работы
    sphere = models.CharField(max_length=100, unique=False, null=True)
    level = models.IntegerField(choices=JOB_LEVELS)  # Уровень работы (можно использовать выбор из списка)
    salary = models.DecimalField(max_digits=10, decimal_places=2)  # Зарплата
    description = models.TextField()  # Описание работы
    required_exp = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'jobs'