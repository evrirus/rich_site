from authentication import SiteAuthentication, TelegramAuthentication
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from icecream import ic
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from utils import (db_houses, get_district_by_id, get_full_houses_info,
                   get_house_by_id, get_item_by_id, get_messages, give_money)


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
    
class GetHouseView(APIView):
    """API для получения списка домов пользователя
    :param: None
    
    returns: success: bool, houses: list"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []    

    def get(self, request: Request, id_house: int):
        house_info = get_house_by_id(id_house)
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
        
        if not house_info.get('basement'):
            messages.info(request, 'Подвал | Подвал не построен.')
            return Response({'success': False, 'messages': get_messages(request),})
        
        current_balance = house_info['basement']['balance']
        if current_balance <= 0:
            messages.info(request, 'Подвал | Вы ничего не добыли.')
            return Response({'success': False, 'messages': get_messages(request),})
        
        db_houses.update_one({'id': request.data},
                             {'$set': {'basement.balance': 0}})
        give_money(request, request.user.server_id, current_balance, type_money='dollar', comment=f'Вы обналичили заработок с майнинга! Заработано: {intcomma(current_balance)}$')
        
        return Response({'success': True, 'message': 'ok',
                         'messages': get_messages(request), 'new_balance': 0,
                         'profit': current_balance})