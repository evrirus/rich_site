import requests
from authentication import SiteAuthentication, TelegramAuthentication
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from icecream import ic
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from magazine.models import Yacht, Car
from utils import (DOMEN, coll, db_cars, db_yachts, get_car_by_id,
                   get_district_by_id, get_full_houses_info, get_house_by_id,
                   get_messages, get_transport_by_ucode, get_yacht_by_id,
                   give_money)


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
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    
    def delete(self, request: Request):
        data = request.data
        ic(data)
        
        if data['type'] not in ('car', 'yacht'):
            return Response({'success': False, 'error': 'Неверный тип транспорта'})

        user_info = request.user
        if user_info.is_anonymous:
            return Response({'success': False, 'error': 'Пользователь не найден'})
        
        ic(data['ucode'])
        
        why_transport = request.user.car if data['type'] == 'car' else request.user.yacht

        for transport in why_transport[f"{data['type']}s"]:
            
            if transport['ucode'] == data['ucode']:
                
                url_get_transport_info = DOMEN + 'api/transport_info/'
                data = {"action": "get_transport_info", "server_id": request.user.server_id, "type": data['type'], 
                        "id": data['id'], "ucode": data['ucode'], "source": "web"}
                response = requests.get(url_get_transport_info, json=data).json()
                ic(response)
                ic(transport)
                ic("Продаю машину")
                ic(request.user.server_id)
                coll.update_one({'server_id': request.user.server_id},
                                {'$pull': {f"{data['type']}.{data['type']}s": {'ucode': data['ucode']}}})
                give_money(request, request.user.server_id, response.get('info', {}).get('price') // 2)

                if data['type'] == 'car':
                    db_cars.update_one({'id': int(data['id'])}, {'$inc': {'quantity': 1}})
                    
                elif data['type'] == 'yacht':
                    db_yachts.update_one({'id': int(data['id'])}, {'$inc': {'quantity': 1}})
                    
                response = response['info']
                messages.success(request, f"Транспорт {response['name']} был успешно продан за {intcomma(response['price'] // 2)} ₽")
                return Response({'success': True, 'sell_to': 'state', 'price': response['price'] // 2,
                                 'messages': get_messages(request), 'ucode': response['ucode'], 'id': int(data['id']),
                                 'type': data['type'], 'name': response['name']})
        else:
            return Response({'success': False, 'error': 'Машина не найдена'})