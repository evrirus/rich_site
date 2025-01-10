from django.contrib.auth.backends import BaseBackend
from .models import CustomUser

class TelegramBackend(BaseBackend):
    def authenticate(self, request, telegram_id=None, **kwargs):
        if telegram_id:
            try:
                user = CustomUser.objects.get(telegram_id=telegram_id)
                return user
            except CustomUser.DoesNotExist:
                return None
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

