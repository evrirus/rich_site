import json
import random

from rest_framework.views import APIView


from authentication import SiteAuthentication, TelegramAuthentication
from rest_framework.authentication import SessionAuthentication

from django.contrib import messages

from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse


from icecream import ic

from utils import get_messages, give_money,  get_symbol_money

class GenerateCombinationView(APIView):
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []

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

    def post(self, request):

        data = json.loads(request.body)
        user_input = data.get('user_input')
        user_choice = data.get('user_choice')

        # Проверка и преобразование ставки
        bid = int(user_input) if user_input.isdigit() else 0
        if bid <= 0:
            messages.error(request, 'Ставка не может быть меньше единицы')
            return JsonResponse(
                {'success': False, 'message': 'Ставка не может быть меньше единицы', 'messages': get_messages(request)})

        balance = request.user.money[user_choice]

        # Проверка достаточности средств
        if balance < bid:
            messages.error(request, 'Недостаточно средств. | Пополнить счёт можно в Донате')
            return JsonResponse(
                {'success': False, 'message': 'Недостаточно средств.', 'messages': get_messages(request)})

        # Генерация комбинации и расчет коэффициента
        items = ["🍭", "🦄", "💵", "🦖", "👻"]
        combination = random.choices(items, k=3)  # Генерация комбинации из трех символов
        coefficient = self.get_coefficient(combination)
        # coefficient = 0 # КОЭФ

        # Рассчет выигрыша
        winnings = int(coefficient * bid) - bid

        # Обновление баланса и отправка уведомления в зависимости от коэффициента
        if coefficient > 1:

            balance += -bid + (winnings * 3)
            give_money(request, request.user.server_id, -bid + (winnings * 3), type_money=user_choice,
                       comment=f"Уведомление | Ваша ставка принята, ваш выигрыш составил {intcomma(winnings)} {get_symbol_money(user_choice)}. \nКоэффициент x{coefficient}.\nОстаточный баланс: {intcomma(balance)} {get_symbol_money(user_choice)}")

        elif coefficient < 1:

            balance += winnings
            give_money(request, request.user.server_id, winnings, type_money=user_choice,
                       comment=f"Уведомление | Ваша ставка проигрышна, вы потеряли {intcomma(winnings)} {get_symbol_money(user_choice)}. \nКоэффициент x{coefficient}.\nОстаточный баланс: {intcomma(balance)} {get_symbol_money(user_choice)}")

        elif coefficient == 1:
            give_money(request, request.user.server_id, 0, type_money=user_choice,
                       comment=f"Уведомление | Ваша ставка не принесла выигрыша.\n Коэффициент x{coefficient}.\nОстаточный баланс: {intcomma(balance)} {get_symbol_money(user_choice)}")

        return JsonResponse(
            {'combination': combination, 'success': True, 'user_input': user_input, 'user_choice': user_choice,
             'messages': get_messages(request)})

    @staticmethod
    def random_with_probability(probability):
        return random.random() < probability

    @staticmethod
    def get_keys_by_value(d, value):
        return [k for k, v in d.items() if v == value]

    def get_coefficient(self, combination: list):

        num = self.get_keys_by_value(self.coefficients, combination)

        if not num:
            return 0

        if num[0] in (1, 32, 63, 94):
            return 4
        elif num[0] == 125:
            return 7
        elif 121 < num[0] < 125 or num[0] in (100, 75, 50, 25):
            return 3
        elif 2 < num[0] < 5 or 31 < num[0] < 35 or 61 < num[0] < 65 or 91 < num[0] < 95 or num[0] in (
        7, 13, 19, 25, 38, 44, 57, 69, 75, 82, 88, 100, 107, 113, 119):
            return 2

        probability = 0.17  # 17% вероятность
        if self.random_with_probability(probability):
            return 1

        probability = 0.22  # 22% вероятность
        if self.random_with_probability(probability):
            return 0.5
        return 0