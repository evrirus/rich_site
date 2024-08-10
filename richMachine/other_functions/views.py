import json
import random
import uuid
from datetime import timedelta
from wsgiref.simple_server import WSGIRequestHandler

import matplotlib.pyplot as plt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from icecream import ic
from pymongo.errors import ConnectionFailure, OperationFailure
from utils import (client, coll, db_cars, db_houses, db_inv, db_yachts,
                   generate_ucode, get_district_by_id, get_house_by_id,
                   get_item_by_id, get_item_in_inventory_user_by_id,
                   get_messages, give_money, verify_telegram_auth, get_symbol_money)

from .models import UserToken

coefficients = {
        1: ['🍭', '🍭', '🍭'],
        2: ['🍭', '🍭', '🦄'],
        3: ['🍭', '🍭', '💵'],
        4: ['🍭', '🍭', '🦖'],
        5: ['🍭', '🍭', '👻'],
        6: ['🍭', '🦄', '🍭'],
        7: ['🍭', '🦄', '🦄'],
        8: ['🍭', '🦄', '💵'],
        9: ['🍭', '🦄', '🦖'],
        10: ['🍭', '🦄', '👻'],
        11: ['🍭', '💵', '🍭'],
        12: ['🍭', '💵', '🦄'],
        13: ['🍭', '💵', '💵'],
        14: ['🍭', '💵', '🦖'],
        15: ['🍭', '💵', '👻'],
        16: ['🍭', '🦖', '🍭'],
        17: ['🍭', '🦖', '🦄'],
        18: ['🍭', '🦖', '💵'],
        19: ['🍭', '🦖', '🦖'],
        20: ['🍭', '🦖', '👻'],
        21: ['🍭', '👻', '🍭'],
        22: ['🍭', '👻', '🦄'],
        23: ['🍭', '👻', '💵'],
        24: ['🍭', '👻', '🦖'],
        25: ['🍭', '👻', '👻'],
        26: ['🦄', '🍭', '🍭'],
        27: ['🦄', '🍭', '🦄'],
        28: ['🦄', '🍭', '💵'],
        29: ['🦄', '🍭', '🦖'],
        30: ['🦄', '🍭', '👻'],
        31: ['🦄', '🦄', '🍭'],
        32: ['🦄', '🦄', '🦄'],
        33: ['🦄', '🦄', '💵'],
        34: ['🦄', '🦄', '🦖'],
        35: ['🦄', '🦄', '👻'],
        36: ['🦄', '💵', '🍭'],
        37: ['🦄', '💵', '🦄'],
        38: ['🦄', '💵', '💵'],
        39: ['🦄', '💵', '🦖'],
        40: ['🦄', '💵', '👻'],
        41: ['🦄', '🦖', '🍭'],
        42: ['🦄', '🦖', '🦄'],
        43: ['🦄', '🦖', '💵'],
        44: ['🦄', '🦖', '🦖'],
        45: ['🦄', '🦖', '👻'],
        46: ['🦄', '👻', '🍭'],
        47: ['🦄', '👻', '🦄'],
        48: ['🦄', '👻', '💵'],
        49: ['🦄', '👻', '🦖'],
        50: ['🦄', '👻', '👻'],
        51: ['💵', '🍭', '🍭'],
        52: ['💵', '🍭', '🦄'],
        53: ['💵', '🍭', '💵'],
        54: ['💵', '🍭', '🦖'],
        55: ['💵', '🍭', '👻'],
        56: ['💵', '🦄', '🍭'],
        57: ['💵', '🦄', '🦄'],
        58: ['💵', '🦄', '💵'],
        59: ['💵', '🦄', '🦖'],
        60: ['💵', '🦄', '👻'],
        61: ['💵', '💵', '🍭'],
        62: ['💵', '💵', '🦄'],
        63: ['💵', '💵', '💵'],
        64: ['💵', '💵', '🦖'],
        65: ['💵', '💵', '👻'],
        66: ['💵', '🦖', '🍭'],
        67: ['💵', '🦖', '🦄'],
        68: ['💵', '🦖', '💵'],
        69: ['💵', '🦖', '🦖'],
        70: ['💵', '🦖', '👻'],
        71: ['💵', '👻', '🍭'],
        72: ['💵', '👻', '🦄'],
        73: ['💵', '👻', '💵'],
        74: ['💵', '👻', '🦖'],
        75: ['💵', '👻', '👻'],
        76: ['🦖', '🍭', '🍭'], 
        77: ['🦖', '🍭', '🦄'],
        78: ['🦖', '🍭', '💵'],
        79: ['🦖', '🍭', '🦖'],
        80: ['🦖', '🍭', '👻'],
        81: ['🦖', '🦄', '🍭'],
        82: ['🦖', '🦄', '🦄'],
        83: ['🦖', '🦄', '💵'],
        84: ['🦖', '🦄', '🦖'],
        85: ['🦖', '🦄', '👻'],
        86: ['🦖', '💵', '🍭'],
        87: ['🦖', '💵', '🦄'],
        88: ['🦖', '💵', '💵'],
        89: ['🦖', '💵', '🦖'],
        90: ['🦖', '💵', '👻'],
        91: ['🦖', '🦖', '🍭'],
        92: ['🦖', '🦖', '🦄'],
        93: ['🦖', '🦖', '💵'],
        94: ['🦖', '🦖', '🦖'],
        95: ['🦖', '🦖', '👻'],
        96: ['🦖', '👻', '🍭'],
        97: ['🦖', '👻', '🦄'],
        98: ['🦖', '👻', '💵'],
        99: ['🦖', '👻', '🦖'],
        100: ['🦖', '👻', '👻'],
        101: ['👻', '🍭', '🍭'],
        102: ['👻', '🍭', '🦄'],
        103: ['👻', '🍭', '💵'],
        104: ['👻', '🍭', '🦖'],
        105: ['👻', '🍭', '👻'],
        106: ['👻', '🦄', '🍭'],
        107: ['👻', '🦄', '🦄'],
        108: ['👻', '🦄', '💵'],
        109: ['👻', '🦄', '🦖'],
        110: ['👻', '🦄', '👻'],
        111: ['👻', '💵', '🍭'],
        112: ['👻', '💵', '🦄'],
        113: ['👻', '💵', '💵'],
        114: ['👻', '💵', '🦖'],
        115: ['👻', '💵', '👻'],
        116: ['👻', '🦖', '🍭'],
        117: ['👻', '🦖', '🦄'],
        118: ['👻', '🦖', '💵'],
        119: ['👻', '🦖', '🦖'],
        120: ['👻', '🦖', '👻'],
        121: ['👻', '👻', '🍭'],
        122: ['👻', '👻', '🦄'],
        123: ['👻', '👻', '💵'],
        124: ['👻', '👻', '🦖'],
        125: ['👻', '👻', '👻'],
    }


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
    



class GenerateCombinationView(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        data = json.loads(request.body)
        user_input = data.get('user_input')
        user_choice = data.get('user_choice')
        
        # Проверка и преобразование ставки
        bid = int(user_input) if user_input.isdigit() else 0
        if bid <= 0:
            messages.error(request, 'Ставка не может быть меньше единицы')
            return JsonResponse({'success': False, 'message': 'Ставка не может быть меньше единицы', 'messages': get_messages(request)})
        
        # Получение информации о пользователе
        user_info = coll.find_one({'server_id': request.user.server_id})
        balance = user_info.get('money', {}).get(user_choice, 0)
        ic(balance)
        
        # Проверка достаточности средств
        if balance < bid:
            messages.error(request, 'Недостаточно средств. | Пополнить счёт можно в Донате')
            return JsonResponse({'success': False, 'message': 'Недостаточно средств.', 'messages': get_messages(request)})
        
        # Генерация комбинации и расчет коэффициента
        items = ["🍭", "🦄", "💵", "🦖", "👻"]
        combination = random.choices(items, k=3)  # Генерация комбинации из трех символов
        coefficient = self.get_coefficient(combination)
        # coefficient = 0 # КОЭФ
        ic(coefficient)
        
        # Рассчет выигрыша
        ic(bid)
        winnings = int(coefficient * bid) - bid
        ic(winnings)
        
        # Обновление баланса и отправка уведомления в зависимости от коэффициента
        ic(balance)
        ic(-bid+(winnings*3))
        if coefficient > 1:
            balance += winnings
            give_money(request, request.user.server_id, -bid+(winnings*3), type_money=user_choice, 
                       comment=f"Уведомление | Ваша ставка принята, ваш выигрыш составил {intcomma(winnings)} {get_symbol_money(user_choice)}. \nКоэффициент x{coefficient}.\nОстаточный баланс: {intcomma(balance)} {get_symbol_money(user_choice)}")
        elif coefficient < 1:
            loss = -(bid + winnings)
            ic(loss)
            balance += winnings
            give_money(request, request.user.server_id, winnings, type_money=user_choice, 
                       comment=f"Уведомление | Ваша ставка проигрышна, вы потеряли {intcomma(winnings)} {get_symbol_money(user_choice)}. \nКоэффициент x{coefficient}.\nОстаточный баланс: {intcomma(balance)} {get_symbol_money(user_choice)}")
        elif coefficient == 1:
            give_money(request, request.user.server_id, 0, type_money=user_choice,
                       comment=f"Уведомление | Ваша ставка не принесла выигрыша.\n Коэффициент x{coefficient}.\nОстаточный баланс: {intcomma(balance)} {get_symbol_money(user_choice)}")

        
        return JsonResponse({'combination': combination, 'success': True, 'user_input': user_input, 'user_choice': user_choice, 'messages': get_messages(request)})



    def random_with_probability(self, probability):
        return random.random() < probability

    def get_keys_by_value(self, d, value):
        return [k for k, v in d.items() if v == value]

    def get_coefficient(self, combination: list):
        
        num = self.get_keys_by_value(coefficients, combination)

        if not num:
            return 0

        if num[0] in (1, 32, 63, 94):
            return 4
        elif num[0] == 125:
            return 7
        elif 121 < num[0] < 125 or num[0] in (100, 75, 50, 25):
            return 3
        elif 2 < num[0] < 5 or 31 < num[0] < 35 or 61 < num[0] < 65 or 91 < num[0] < 95 or num[0] in (7, 13, 19, 25, 38, 44, 57, 69, 75, 82, 88, 100, 107, 113, 119):
            return 2

        probability = 0.17  # 20% вероятность
        if self.random_with_probability(probability):
            return 1
        
        probability = 0.22  # 20% вероятность
        if self.random_with_probability(probability):
            return 0.5
        return 0

def slot_machine(request):
    return render(request, 'other_functions/casino_slot.html', {'my_server_id': request.user.server_id})
