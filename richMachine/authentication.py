from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from icecream import ic
from utils import coll

User = get_user_model()

class TelegramAuthentication(BaseAuthentication):
    def authenticate(self, request):
        telegram_id = request.data.get('telegram_id')

        if not telegram_id:
            return None

        try:

            user = User.objects.get(telegram_id=telegram_id)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
        
        
class SiteAuthentication(BaseAuthentication):
    def authenticate(self, request):

        server_id = request.data.get('server_id')

        if not server_id:
            return None

        try:
            user = User.objects.get(server_id=server_id)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

