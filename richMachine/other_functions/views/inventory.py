from authentication import SiteAuthentication, TelegramAuthentication
from django.contrib import messages
from icecream import ic
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import json
import random


from wsgiref.simple_server import WSGIRequestHandler
from authentication import SiteAuthentication, TelegramAuthentication
from rest_framework.authentication import SessionAuthentication

from django.contrib import messages

from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse
from django.shortcuts import  render


from django.views.decorators.csrf import csrf_exempt

from icecream import ic

import requests
from utils import (DOMEN,get_item_by_id,get_messages, give_money,  get_symbol_money)

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
                    show_items.append({
                        'name': videocard_info['name'],
                        'performance': videocard_info['attributes']['performance'],
                        'type': videocard_info['type'], 'id': item['id']
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

        # Возвращение отрендеренного шаблона с данными
        return render(request, 'other_functions/inventory.html', {
            'my_server_id': request.user.server_id,
            'items': show_items
        })