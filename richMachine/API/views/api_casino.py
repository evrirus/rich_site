import json
import random

from icecream import ic
from rest_framework.views import APIView

from authentication import SiteAuthentication, TelegramAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse
from rest_framework.request import Request

from casino.models import CasinoModel, FreeSpinType
from utils import send_message_to_user, Money


class GenerateCombinationView(APIView):
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = [IsAuthenticated]

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

    def post(self, request: Request):

        data = request.data

        user_input = data.get('user_input')
        user_choice = data.get('user_choice')
        user_bid = data.get('bid', 0)
        ic(user_input, user_choice, user_bid)

        casino_model = CasinoModel.objects.filter(user=request.user).first()

        # if not casino_model.is_authenticated:
        #     return JsonResponse({'is_authenticated': False, 'error': True, 'message': 'Введите пароль для авторизации.'})

        if user_bid.isdigit() and user_input.isdigit():
            bid = int(user_input)

        elif user_bid == 'vabank':
            bid = request.user.money[user_choice]

        elif user_bid == 'freespin':
            is_use = casino_model.use_freespin()
            if is_use:

                freespins = casino_model.free_spin_types.all()
                bid = freespins.first().stake_value
                user_choice = freespins.first().currency

            else:
                send_message_to_user(request, {'text': 'Нет доступных фриспинов'})

                return JsonResponse(
                    {'success': False, 'message': 'Нет доступных фриспинов', 'freespin': 0})
        else: bid = 0

        if bid <= 0:
            send_message_to_user(request, {'text': 'Ставка не может быть меньше единицы'})

            return JsonResponse(
                {'success': False, 'message': 'Ставка не может быть меньше единицы'})

        balance = request.user.money[user_choice]

        # Проверка достаточности средств
        if not user_bid == 'freespin' and balance < bid:
            send_message_to_user(request, {'text': 'Недостаточно средств. | Пополнить счёт можно в Донате'})

            return JsonResponse(
                {'success': False, 'message': 'Недостаточно средств.'})

        # Генерация комбинации и расчет коэффициента
        items = ["🍭", "🦄", "💵", "🦖", "👻"]
        combination = random.choices(items, k=3)  # Генерация комбинации из трех символов
        coefficient = self.get_coefficient(combination)
        # coefficient = 0 # КОЭФ

        # Рассчет выигрыша
        winnings = int(coefficient * bid) - bid

        # Обновление баланса и отправка уведомления в зависимости от коэффициента
        if coefficient > 1:
            balance += -bid + (winnings * 2)

            money = Money(request, -bid + (winnings * 2), type_money=user_choice)
            text = (f'Вы выиграли {intcomma(winnings)} {Money.get_symbol(user_choice)} (x{coefficient})\n'
                    f'Баланс: {intcomma(balance)} {Money.get_symbol(user_choice)}')

        elif coefficient < 1:


            if user_bid == 'freespin':
                money = Money(request, 0, type_money=user_choice)

                text = (f'Фриспин на {intcomma(bid)}{Money.get_symbol(user_choice)} (x{coefficient})\n'
                        f'Ваш баланс остался прежним!\n'
                        f'Баланс: {intcomma(balance)} {Money.get_symbol(user_choice)}')
            else:
                money = Money(request, winnings, type_money=user_choice)
                balance += winnings

                text = (f'Вы проиграли {intcomma(winnings)} {Money.get_symbol(user_choice)} (x{coefficient})\n'
                        f'Баланс: {intcomma(balance)} {Money.get_symbol(user_choice)}')

        # coefficient == 1
        else:

            money = Money(request, 0, type_money=user_choice)

            text = (f'Ваши деньги остаются при Вас (x{coefficient})\n'
                    f'Баланс: {intcomma(balance)} {Money.get_symbol(user_choice)}')


        # if money.amount > 0 and casino_model.max_win < money.amount:
        #     casino_model.max_win = money.amount
        #     casino_model.max_cash_win_type = 'dollar'
        #     if user_choice != 'dollar':
        #         ...
        #     casino_model.

                #todo: Сделать пропорцию валюты к доллару
                #todo: сначала сделать биржу



        # top_bets = CasinoModel.objects.order_by('-max_win')[:10] # 10 человек с самыми высокими ставками
        #
        # ic(top_bets)


        money.give()
        # money.create_notification(text+' CASINO')

        return JsonResponse(
            {'combination': combination, 'success': True,
             'user_input': user_input, 'user_choice': user_choice,
             'notify': text, 'freespins': casino_model.freespins_available,
             'winnings': winnings or 0,
             'balance': request.user.money[user_choice],
             })

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

        num = num[0]

        # Условие для фиксированных коэффициентов
        fixed_coefficients = {
            4: {1, 32, 63, 94},
            7: {125},
            3: {100, 75, 50, 25}.union(range(121, 125 + 1)),
            2: {7, 13, 19, 26, 38, 44, 51, 57, 69, 76, 82, 88, 101, 107, 113, 119}.union(
                range(2, 5+1), range(31, 35 + 1),
                range(61, 65 + 1), range(91, 95 + 1)
            ),
        }

        for coefficient, numbers in fixed_coefficients.items():
            if num in numbers:
                return coefficient

        # Вероятности
        if self.random_with_probability(0.13):  # 13% вероятность
            return 1
        if self.random_with_probability(0.13):  # 13% вероятность
            return 0.75
        if self.random_with_probability(0.17):  # 17% вероятность
            return 0.5
        if self.random_with_probability(0.17):  # 17% вероятность
            return 0.25

        return 0
