import requests
from authentication import SiteAuthentication, TelegramAuthentication
from django.contrib.humanize.templatetags.humanize import intcomma
from icecream import ic
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from magazine.models import Yacht, Car
from utils import (DOMEN, coll, db_cars, db_yachts, get_car_by_id,
                   get_district_by_id, get_full_houses_info, get_house_by_id,
                   get_transport_by_ucode, get_yacht_by_id,
                   give_money, DoRequest, send_message_to_user)


class GetMyCarsView(APIView):
    """API для получения списка машин пользователя
    :param: None
    
    returns: success: bool, cars: list"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []
    
    def post(self, request: Request):
        data = request.data
        ic(data)
        
        user_info = request.user
        
        if not user_info:
            return Response({"success": False, "error": "user_not_found"})
        
        ic(user_info)
        del user_info.car['order']
        del user_info.car['offer']

        
        return Response(user_info.car)
    
    
class GetMyYachtsView(APIView):
    """API для получения списка яхт пользователя
    :param: None
    
    returns: success: bool, yachts: list"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []
    
    def post(self, request: Request):
        data = request.data
        
        user_info = request.user
            
        if not user_info:
            return Response({"success": False, "error": "user_not_found"})
        
        del user_info.yacht['order']
        del user_info.yacht['offer']

        
        return Response(user_info.yacht)
    
    
class CheckTransportInfo(APIView):
    """API для проверки информации о транспорте пользователя
    :param: None

    returns: success: bool, type: str, info: dict"""
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]

    def get(self, request: Request):
        data = request.GET or request.data

        func = get_yacht_by_id if data['type'] == 'yacht' else get_car_by_id if data['type'] == 'car' else None
        if not func:
            return Response({"success": False, "error": "invalid_type"})

        data_transport = func(int(data['id']))

        if data.get('ucode'):
            ic(request.user.car)
            result = {
                **get_transport_by_ucode(request.user.server_id, data['type'], data['ucode']),
                'quantity': data_transport.quantity,
                'maxQuantity': data_transport.max_quantity,
            }

            ic(result)
            return Response({"success": True, "info": result})

        return Response({"success": False, 'error': "invalid_transport"})


class SellTransportToState(APIView):
    """API для продажи транспорта пользователя
    :param: None

    returns: success: bool, type: str, info: dict"""
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication, TokenAuthentication]

    def post(self, request: Request, type: str, ucode: str):
        ic(request)
        # ic(args)
        # ic(kwargs)

        if type not in ('car', 'yacht'):
            return Response({'success': False, 'error': 'Неверный тип транспорта'})

        user = request.user
        if not user:
            return Response({'success': False, 'error': 'Пользователь не найден'})

        if type == 'car':
            transports = user.car['cars']
        else:
            transports = user.yacht['yachts']

        num = 0
        for k, tr in enumerate(transports):
            if tr['ucode'] == ucode:
                num = k
        if type == 'car':
            items = user.car.get('cars', [])
        else:
            items = user.yacht.get('yachts', [])

        ic(items, num)
        transport_info = items[num]
        items.pop(num)

        if type == 'car':
            user.car['cars'] = items
        else:
            user.yacht['yachts'] = items
        user.save()

        give_money(request, request.user.server_id, transport_info['price'] // 2)

        if type == 'car':
            car = Car.objects.get(id=transport_info['id'])
            car.quantity += 1
            car.save()

        elif type == 'yacht':
            yacht = Yacht.objects.get(id=transport_info['id'])
            yacht.quantity += 1
            yacht.save()

        else:
            ic('ASHIBKA')

        send_message_to_user(request.user.server_id, {'text': 'Транспорт успешно продан!'})
        # messages.success(request, 'Транспорт успешно продан!')
        return Response({'success': True, 'message': 'Транспорт успешно продан!'})
