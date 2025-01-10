import requests
from django.shortcuts import render
from rest_framework.request import Request
from icecream import ic
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.views import APIView

from authentication import SiteAuthentication, TelegramAuthentication
from utils import (DOMEN, get_item_by_id)


class RenderInventory(APIView):
    """API для смены никнейма
    :param: NewNickname

    returns: success: bool, old_nickname: str, new_nickname: str,
             server_id: int, max_lenght: int"""
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []

    def get(self, request: Request):

        url_get_inventory = DOMEN + 'api/get_inventory/'
        data = {"action": "get_inventory", "server_id": request.user.server_id, "source": "web"}
        response = requests.get(url_get_inventory, json=data).json()
        ic(response)
        # Список для хранения информации о предметах, которые будут отображаться
        show_items = []

        # Заполнение списка информацией о видеокартах
        for item in response.get('inventory', []):
            if item['type'] == 'videocard':

                for i in show_items:
                    if item['id'] == i['id']:
                        show_items.append({
                            'name': i['name'], 'performance': i['performance'],
                            'type': i['type'], 'id': item['id']
                        })
                        break

                else:
                    videocard_info = get_item_by_id(item['id'])
                    ic(videocard_info, item)
                    show_items.append({
                        'name': videocard_info.name,
                        'performance': videocard_info.attributes['performance'],
                        'type': videocard_info.type, 'id': item['id']
                    })

            elif item['type'] == 'plate':
                show_items.append({
                    'num': item['attributes']['value'],
                    'type': item['type'],
                })

        # Определение разности между максимальным количеством и текущим количеством предметов
        max_quantity = response.get('maxQuantity', 0)
        current_quantity = len(show_items)

        if current_quantity < max_quantity:
            difference = max_quantity - current_quantity
            # Заполнение оставшегося места пустыми элементами
            show_items.extend([{'type': 'empty'}] * difference)

        ic(show_items)

        # Возвращение отрендеренного шаблона с данными
        return render(request, 'inventory/inventory.html', {
            'my_server_id': request.user.server_id,
            'items': show_items
        })