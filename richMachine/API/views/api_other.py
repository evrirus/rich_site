from authentication import SiteAuthentication, TelegramAuthentication
from icecream import ic
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from inventory.models import Inventory
from utils import (coll, db_cars, db_crypt, db_inv, get_car_by_id,
                   get_district_by_id, get_full_houses_info, get_house_by_id,
                   get_yacht_by_id, give_money)


class GetSymbolCrypt(APIView):
    """API для получения баланса пользователя
    :param: None
    
    returns: success: bool, cash: int, bitcoin: int, ..."""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []
    
    def post(self, request: Request):
        symbol = db_crypt.find_one({'name': request.data['crypt'].title()}, projection={'_id': 0, 'symbol': 1})['symbol']
        ic(symbol)
        return Response({"success": True, "symbol": symbol})
    
    
class GetInventory(APIView):
    """API для получения инвентаря пользователя по страницам
    :param: None
    
    returns: success: bool, inventory: list[dict], page: int"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []
    
    def get(self, request: Request):

        ic(request.user.server_id)
        inv = Inventory.objects.get(server_id=request.user.server_id)

        items = inv.items.all()
        standart_items = []
        for item in items:

            standart_items.append({
                'id': item.item_id,
                'type': item.item_type
            })

        ic(standart_items)
        result = {"success": True, 'inventory': standart_items}

        return Response(result)