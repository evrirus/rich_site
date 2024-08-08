import json
from wsgiref.simple_server import WSGIRequestHandler

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from icecream import ic
from pymongo.errors import ConnectionFailure, OperationFailure
from utils import (client, coll, db_cars, db_houses, db_yachts,
                   get_district_by_id, get_house_by_id, get_item_by_id, get_item_in_inventory_user_by_id, get_messages,
                   give_money, verify_telegram_auth, db_inv)

# Create your views here.
def inventory(request: WSGIRequestHandler):
    # Получение информации о пользователе и его инвентаре
    inventory_user = db_inv.find_one({'server_id': request.user.server_id})

    # Список для хранения информации о предметах, которые будут отображаться
    show_items = []

    # Заполнение списка информацией о видеокартах
    for item in inventory_user.get('inventory', []):
        if item['type'] == 'videocard':
            videocard_info = get_item_by_id(item['id'])
            show_items.append({
                'name': videocard_info['name'],
                'performance': videocard_info['attributes']['performance'],
                'type': videocard_info['type']
            })
        if item['type'] == 'plate':
            show_items.append({
                'num': item['attributes']['value'],
                'type': item['type'],
            })

    # Определение разности между максимальным количеством и текущим количеством предметов
    max_quantity = inventory_user.get('maxQuantity', 0)
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


