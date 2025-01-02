from channels.generic.websocket import AsyncWebsocketConsumer
import json
from icecream import ic

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_authenticated:
            # Если пользователь авторизован, используем его ID для группы
            self.group_name = f'user_{user.id}'
        else:
            # Если пользователь не авторизован, используем session_key
            session_key = self.scope['session'].session_key
            if not session_key:
                # Создаём сессию, если её ещё нет
                self.scope['session'].create()
                session_key = self.scope['session'].session_key
            self.group_name = f'session_{session_key}'

        # Привязываем пользователя к группе
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Принимаем соединение
        await self.accept()

        # await self.send(text_data=json.dumps({'hello': 'world'}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        ic(data)
        # Для отправки данных клиенту
        await self.send(text_data=json.dumps(data))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['message']))
