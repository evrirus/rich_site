
from utils import (get_district_by_id, get_full_houses_info,
                    get_item_by_id)

from django.db import transaction

from django.contrib import messages

from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse

from icecream import ic
from magazine.models import Houses
from utils import (db_houses,get_house_by_id,
                   get_messages, give_money)

from authentication import SiteAuthentication, TelegramAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from django.urls import reverse_lazy
from rest_framework.views import APIView


class GetMyHousesView(APIView):
    """API для получения списка домов пользователя
    :param: None
    
    returns: success: bool, houses: list"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []
    
    def post(self, request: Request):
        user_info = request.user
            
        if not user_info:
            return Response({"success": False, "error": "user_not_found"})
        
        houses = [get_full_houses_info(x['id']) for x in user_info.house['houses']]
        
        return Response(houses)


class SellHouseView(APIView):
    """API для продажи дома игрока
    :param: NewNickname

    returns: success: bool, message: str"""
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []

    def post(self, request: Request, id: int):
        ic(id)
        house_info = get_house_by_id(id)

        if not house_info:
            messages.error(request, "Дом не найден")
            return Response({"success": False, "error": "Дом не найден", 'messages': get_messages(request)})

        if house_info.owner != request.user.server_id:
            messages.error(request, "Дом не найден")
            return Response({"success": False, "error": "Дом не найден",
                             'messages': get_messages(request)})

        with transaction.atomic():
            # Предполагаем, что house_info.id содержит id, который нужно удалить
            request.user.house['houses'] = [tr for tr in request.user.house['houses'] if tr['id'] != house_info.id]
            request.user.save()

            house = Houses.objects.get(id=house_info.id)
            house.owner = None
            house.save()

        give_money(request, request.user.server_id, house_info.price // 2)
        messages.success(request, 'Продажа прошла успешно!')
        return JsonResponse({'success': True, 'message': 'Продажа прошла успешно!', 'messages': get_messages(request)})

class GetHouseView(APIView):
    """API для получения списка домов пользователя
    :param: None
    
    returns: success: bool, houses: list"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []    

    def get(self, request: Request, id_house: int):
        house_info = get_house_by_id(id_house)
        if not house_info:
            messages.error(request, 'Дом не найден')
            return JsonResponse({"success": False, "error": "Дом не найден",
                                 'messages': get_messages(request)})

        district_info = get_district_by_id(house_info.district_id)

        standart_district_info = {
            'name': district_info.name,
        }

        standart_house_info = {
            'id_for_district': house_info.id_for_district,
            'district_info': standart_district_info,
            'basement': house_info.basement.get('level', 0) if house_info.basement else 0,
            'price': house_info.price,
            'type': 'Дом' if house_info.type_field == 'house' else 'Квартира',
            'class': house_info.class_field.title(),
            'floors': house_info.floors,
            'id': house_info.id,
        }
        ic(standart_house_info)
        return Response({'success': True, 'message': 'ok',
                        **standart_house_info})
        
class GetBasementView(APIView):
    """API для получения списка домов пользователя
    :param: None
    
    returns: success: bool, houses: list"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []    

    def get(self, request: Request, id_house: int):
        ic(id_house)
        house_info = get_house_by_id(id_house)

        ic(house_info)
        
        videocards = []
        mix_videocards = []
        # if not house_info['basement'].get('videocards'):
        #     return Response({'success': False, 'message': 'ok',
        #                      **house_info})

        standart_house_info = {
            'id': house_info.id,
            'basement': house_info.basement,
            'balance': house_info.basement.get('balance', 0),
        }
        ic(standart_house_info)
        ic(house_info.basement)

        for id, qty in house_info.basement.get('videocards', {}).items():
            if qty == 0:
                continue
            
            card = get_item_by_id(int(id))
            videocards.extend([{'id': card['id'], 'name': card['name'],
                               'performance': card['attributes']['performance'],
                               'price': card['price']}] * qty)
            
            mix_videocards.append({'name': card['name'], 'quantity': qty})

        return Response({'success': True, 'message': 'ok',
                         'videocards': videocards, 'house_info': standart_house_info,
                         'mix_videocards': mix_videocards})
        

class GetTakeProfitBasementView(APIView):
    """API для получения прибыли с подвала
    :param: None
    
    returns: success: bool, houses: list"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []   
    
    def post(self, request: Request):
        house_info = get_house_by_id(request.data)

        if not house_info.basement:
            messages.info(request, 'Подвал | Подвал не построен.')
            return Response({'success': False, 'messages': get_messages(request),})
        
        current_balance = house_info.basement['balance']
        if current_balance <= 0:
            messages.info(request, 'Подвал | Вы ничего не добыли.\nВозможно, вы недавно забирали прибыль')
            return Response({'success': False, 'messages': get_messages(request),})

        house = Houses.objects.get(id=house_info.id)
        house.basement['balance'] = 0
        house.save()

        db_houses.update_one({'id': request.data},
                             {'$set': {'basement.balance': 0}})
        give_money(request, request.user.server_id, current_balance, type_money='dollar', comment=f'Вы обналичили заработок с майнинга! Заработано: {intcomma(current_balance)}$')
        
        return Response({'success': True, 'message': 'ok',
                         'messages': get_messages(request), 'new_balance': 0,
                         'profit': current_balance})


class GetBalanceBasementView(APIView):
    """API для получения значения прибыли с подвала
    :param: None

    returns: success: bool, balance: int"""

    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []

    def get(self, request: Request, id_house: int):
        house_info = get_house_by_id(id_house)

        if house_info.owner != request.user.server_id:
            # messages.error(request, 'Вы не являетесь владельцем этого дома.')
            return Response({'success': False})

        if not house_info.basement:
            # messages.error(request, 'Нет подвала.')
            return Response({'success': False})

        return Response({'success': True, 'balance': house_info.basement['balance']})


class CreateBasementView(APIView):
    """API для постройки подвала в доме
    :param: None

    returns: success: bool, houses: list"""

    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []

    def post(self, request: Request, *args, **kwargs):
        ic(request.data)
        house = Houses.objects.get(id=request.data)

        if house.basement:
            messages.error(request, 'Подвал | У вас уже имеется подвал.')
            return Response({'success': False, 'messages': get_messages(request)})

        PRICE_FIRST_LEVEL = 4_000_000

        if request.user.money['cash'] < PRICE_FIRST_LEVEL:
            messages.error(request, "Недостаточно средств.")
            return Response({'success': False, 'messages': get_messages(request)})

        house.basement = {
                'level': 1,
                'maxQuantity': 10,
                'balance': 0,
                'videocards': {}
            }
        house.save()

        give_money(request, request.user.server_id, -PRICE_FIRST_LEVEL)

        messages.success(request, 'Поздравляем | Вы построили подвал первого уровня!')
        return Response({'success': True, 'messages': get_messages(request), 'level': 1, 'house_id': house.id})


class UpgradeBasementView(APIView):
    """API для постройки подвала в доме
    :param: None

    returns: success: bool, houses: list
    levels:
    1 lvl: 10 videocards, 4 000 000₽
    2 lvl: 30 videocards, 5 000 000₽
    3 lvl: 60 videocards, 7 000 000₽
    """

    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []

    def get(self, request: Request, id_house: int):
        house_info = get_house_by_id(id_house)
        upgrade_data = {
            1: {'maxQuantity': 10, 'level': 1, 'price': 4_000_000},
            2: {'maxQuantity': 30, 'level': 2, 'price': 5_000_000},
            3: {'maxQuantity': 60, 'level': 3, 'price': 7_000_000},
        }

        if not house_info.basement:
            messages.error(request, 'Нет подвала.')
            return Response({'success': False, 'messages': get_messages(request)})

        if house_info.basement.get('level', 0) < 1:
            messages.error(request, 'Нет подвала.')
            return Response({'success': False, 'messages': get_messages(request)})

        if house_info.owner != request.user.server_id:
            messages.error(request, "Дом не найден")
            return Response({'success': False, 'messages': get_messages(request)})

        if house_info.basement.get('level', 0) >= max(upgrade_data.keys()):
            messages.error(request, 'Уровень подвала максимален')

        if house_info.basement.get('level', 0) not in upgrade_data.keys():
            messages.error(request, 'Неизвестная ошибка.')
            return Response({'success': False, 'messages': get_messages(request)})

        if request.user.money['cash'] < upgrade_data[house_info.basement.get('level', 0) + 1]['price']:
            messages.error(request, 'Недостаточно средств.')
            return Response({'success': False, 'messages': get_messages(request)})

        give_money(request, request.user.server_id, -upgrade_data[house_info.basement.get('level', 0) + 1]['price'])

        house_info.basement['maxQuantity'] = upgrade_data[house_info.basement.get('level', 0) + 1]['maxQuantity']
        house_info.basement['level'] += 1
        house_info.save()

        messages.success(request, f'Вы улучшили подвал до {house_info.basement['level']} уровня! Теперь подвал вмещает больше видеокарт.')
        return Response({'success': True, 'messages': get_messages(request), 'new_level': house_info.basement['level']})

        #TODO: доделать обновление подвала
        ...