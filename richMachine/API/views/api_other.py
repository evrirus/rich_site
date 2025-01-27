from icecream import ic
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated
from authentication import SiteAuthentication, TelegramAuthentication
from inventory.models import Inventory
from magazine.models import Items
from utils import db_crypt


class GetSymbolCrypt(APIView):
    """API для получения баланса пользователя
    :param: None
    
    returns: success: bool, cash: int, bitcoin: int, ..."""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request: Request):


        symbol = db_crypt.find_one({'name': request.data['crypt'].title()}, projection={'_id': 0, 'symbol': 1})['symbol']
        ic(symbol)
        return Response({"success": True, "symbol": symbol})
    
    
class GetInventory(APIView):
    """API для получения инвентаря пользователя по страницам
    :param: None
    
    returns: success: bool, inventory: list[dict], page: int"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request: Request):

        inv = Inventory.objects.get(user=request.user)

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

