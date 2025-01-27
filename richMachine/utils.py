import datetime
import hashlib
import hmac
import random
import re
import string
import time
import uuid

import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.humanize.templatetags.humanize import intcomma
from icecream import ic
from pymongo import MongoClient
from rest_framework.request import Request

from magazine.models import Car, Districts, Houses, Yacht, Items
from users.models import CustomUser

DOMEN = 'http://127.0.0.1:8000/'

client = MongoClient('mongodb://localhost:27017')
db = client.get_database('lalka')

coll = db.get_collection('users_customuser')




db_items = db.get_collection('items')
db_rates = db.get_collection('rates')
db_stock = db.get_collection('stock')
db_crypt = db.get_collection('crypt')


db_houses = db.get_collection('houses')
db_inv = db.get_collection('inventory')
db_log = db.get_collection('logging')






def generate_ucode(k=9):
    """Генерирует уникальный код длиной 9 символов."""

    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=k))



def verify_telegram_auth(data, token):
    check_hash = data   .pop('hash', None)
    data_check_string = '\n'.join([f'{k}={v}' for k, v in sorted(data.items())])
    secret_key = hashlib.sha256(token.encode()).digest()
    hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if hash != check_hash:
        return False
    if time.time() - int(data['auth_date']) > 86400:
        return False
    return True


def get_crypto_info(name: str):
    data = db_crypt.find_one({'name': name})
    
    return {'name': data['name'], 'owner': data['owner'],
            'quantity': data['quantity'], 'symbol': data['symbol']}

def get_full_house_info(house_id: int) -> dict:
    house_info = get_house_by_id(house_id)
    house_info.district_info = get_district_by_id(house_info.district_id)
    return house_info

#* ID
def get_house_by_id(house_id: int):
    try:
        return Houses.objects.get(id=house_id)
    except Houses.DoesNotExist: return {}

def get_district_by_id(dis_id: int):
    try:
        return Districts.objects.get(district_id=dis_id)
    except Districts.DoesNotExist: return {}

def get_car_by_id(car_id: int):
    try:
        return Car.objects.get(id=car_id)
    except Car.DoesNotExist: return None

def get_yacht_by_id(yacht_id: int):
    try:
        return Yacht.objects.get(id=yacht_id)
    except Yacht.DoesNotExist: return None

#* ucode
def get_transport_by_ucode(request: Request, type: str, ucode: str) -> None | dict:
    ic(request)
    if type == 'car':
        for transport in request.user.car['cars']:
            if transport['ucode'] == ucode:
                return transport

    elif type == 'yacht':
        for transport in request.user.yacht['yachts']:
            if transport['ucode'] == ucode:
                return transport
    return None




def send_message_to_user(request: Request, message: dict[str, str]) -> None:
    """
    Отправляет сообщение пользователю через WebSocket.
    """

    if request.data and request.data.get('source') == 'telegram_bot':
        return

    channel_layer = get_channel_layer()
    group_name = f'user_{request.user.server_id}'

    # todo: удалить

    message['text'] += ' WS'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',  # Метод, который будет вызван в Consumer
            'message': message,          # Данные для отправки
        }
    )


def send_message_to_session(session_key: str, message: dict[str, str]):
    channel_layer = get_channel_layer()
    group_name = f"session_{session_key}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "message": message,
        }
    )


class Money:
    #todo: переделать give_money на этот класс.
    def __init__(self, request: Request,
                 amount: int, type_money: str = 'cash') -> None:

        self.type_money = type_money
        self._request = request
        self._server_id = request.user.server_id
        self.amount = amount
        self._type_money = type_money


    def give(self, save=True):
        if self.amount == 0:
            return False
        user = self._request.user

        user.money[self.type_money] += self.amount
        if save:
            user.save()

        return self


    def create_notification(self, v: str):
        if self.amount > 0 and not v:
            v = f"На баланс начислено: {intcomma(self.amount)} {self.get_symbol(self._type_money)}"

        elif self.amount < 0 and not v:
            v = f"С баланса списано: {intcomma(self.amount)} {self.get_symbol(self._type_money)}"

        send_message_to_user(self._request, {'text': v})

        return self


    @staticmethod
    def get_symbol(type_money: str = "cash"):
        if type_money in ("cash", "bank") : symbol = "₽"
        elif type_money == 'USD': symbol = "$"
        elif type_money == 'bitcoin': symbol = "₿"
        else: symbol = "(?)"
        return symbol


def calculate_total_quantity(house_id: int):
    house = get_house_by_id(house_id)
    quantity = 0
    
    for videocard in house['house_info'].get('basement', {})['videocards']:
        for name, value in videocard.items():
            ic(name, value)
            quantity += value['quantity']
    return quantity






def add_log_entry(user_id, action):
    current_time = datetime.datetime.now()
    year = current_time.year
    month = current_time.month
    day = current_time.day

    # Создание уникального идентификатора для лога
    new_id = f"{user_id}_{current_time.strftime('%Y%m%d%H%M%S')}"

    # Проверка наличия года в коллекции

    log = db_log.find_one({'user_id': user_id, 'date': f'{year}.{month}.{day}'})
    if not log:
        db_log.insert_one({'user_id': user_id, 'date': f'{year}.{month}.{day}', 'logs': []})

    # Запись в лог
    log_entry = {
        '_id': new_id,
        'user_id': user_id,
        'timestamp': current_time,
        'event': action
    }

    # Добавление лога в соответствующий день
    db_log.update_one(
        {'year': year, 'months.month': month, 'months.days.day': day},
        {'$push': {'months.$.days.$.logs': log_entry}}
    )


def get_item_by_id(item_id: int):
    try:
        return Items.objects.get(id=item_id)
    except Items.DoesNotExist: return None




def get_item_by_name(item_name: str):
    video_info = db_items.find_one({'items': {'$elemMatch': {'name': item_name}}}, projection={'items.$': 1, '_id': False})
    # ic(video_info)
    return {'model': video_info['items'][0]['name'], 
            'attributes': video_info['items'][0]['attributes'],
            'price': video_info['items'][0]['price'],
            'id': video_info['items'][0]['_id']}


def add_inventory(user_id: int, id_item: str, quantity: int = False, type_item: str = None):
    user_inv = db_inv.find_one({'user_id': user_id})
    
    if not user_inv:
        return False
    
    data = {'id': id_item, 'type': type_item}
    if quantity:
        data.update({'quantity': quantity})
    data.update({'ucode': ic(uuid.uuid5(uuid.NAMESPACE_DNS, f"{type_item}_{id_item}"))})
    
    return db_inv.update_one({'user_id': user_id},
                             {'$push': {'inventory': data}})
    

def delete_inventory(user_id: int, id_item: str, quantity: int = 1):
    user_inv = db_inv.find_one({'user_id': user_id})
    
    if user_inv['inventory'].get(f'{id_item}'):
        return db_inv.update_one({'user_id': user_id},
                                       {'$inc': {f'inventory.{id_item}': -quantity}})
        
    if not user_inv['inventory'].get(f'{id_item}'):
        db_inv.update_one({'user_id': user_id},
                                {'$unset': {f'inventory.{id_item}': quantity}})
    
    
def add_inventory_as_value(user_id: int, id_item: str = '19', value: str = None):
    user_inv = db_inv.update_one({'user_id': user_id},
                                       {'$push': {f'inventory.{id_item}''values': value}})
    if user_inv.modified_count:
        return True
    return False
    

def money_format(money: int):
    return "{:,}".format(money).replace(',', '.')

class nety_loga(BaseException):
    pass


def log_action(user_id: int | str, situation: str, balance: bool = False, **kwargs):
    
    actions = {
        "registration": {"local_id": kwargs.get('local_id'),
                         "referal": kwargs.get('referal')},
        "change_language": {"language": kwargs.get('language')},
        "received_exchange": {"quantity": kwargs.get('quantity'),
                              "type_crypt": kwargs.get('type_crypt')},
        "close_order": {"type_deal": kwargs.get('type_deal'),
                        "quantity": kwargs.get('quantity'),
                        "type_crypt": kwargs.get('type_crypt')},
        "published_order": {"type_deal": kwargs.get('type_deal'),
                            "deal_id": kwargs.get('deal_id'),
                            "quantity": kwargs.get('quantity'),
                            "type_crypt": kwargs.get('type_crypt')},
        "take_videocard": {"name_videocard": kwargs.get('name_videocard'),
                           "house_id": kwargs.get('house_id')},
        "put_videocard": {"name_videocard": kwargs.get('name_videocard'),
                          "house_id": kwargs.get('house_id')},
        "upgrade_basement": {"house_id": kwargs.get('house_id'),
                             "new_level": kwargs.get('new_level')},
        "set_class": {"house_id": kwargs.get('house_id'),
                      "new_class": kwargs.get('new_class')},
        "set_floor": {"house_id": kwargs.get('house_id'),
                      "new_floor": kwargs.get('new_floor')},
        "buy_videocard": {"name_videocard": kwargs.get('new_videocard')},
        "sell_house": {"price": kwargs.get('price'),
                       "house_id": kwargs.get('house_id'),
                       "new_owner": kwargs.get('new_owner')},
        "sell_car": {"price": kwargs.get('price')},
        "sell_yacht": {"price": kwargs.get('price')},
        "give_payday": {"qty_users": kwargs.get('qty_users'),
                        "give_all_money": kwargs.get('give_all_money')},
        "exchange_rates": {"new_course": kwargs.get('new_course')},
        "change_nickname": {"old": kwargs.get('old'),
                            "new": kwargs.get('new')},
        "marriage_is_concluded": {"couple": kwargs.get('couple')},
        "kazino": {"coefficient": kwargs.get('coefficient'),
                   "stavka": kwargs.get('stavka')},
        "new_level_job": {"level": kwargs.get('new_level')},
        "get_a_wage": {"salary": kwargs.get('salary'),
                       },
        "create_crypt": {"qty": kwargs.get('qty'), 
                         "name": kwargs.get('name'), 
                         "symbol": kwargs.get('symbol'), 
                         "id_crypt": kwargs.get('id_crypt')},
        "": {},
        }

    if situation not in actions:
        print('Не предусмотрена ситуация по логу.')
        return False
    
    user = coll.find_one({'user_id': user_id}) or {}
    action_message = actions[situation]
    current_time = datetime.datetime.now()
    log_entry = {"time": current_time, 
                 "user_id": user_id, 
                 "local_id": user.get('_id', -1), 
                 "situation": situation,
                 "action": action_message}
    if balance:
        log_entry['balance'] = user.get('money')
    db_log.insert_one(log_entry)


def DoRequest(link: str, method: str = 'GET',
              token: str = "3e3c9b5af858140a22ce5591f716c42a62571f6e",
              data: dict = {}, json: dict = {},
              **kwargs) -> dict: #todo: заменить токен на None
    link = DOMEN + link
    token = token

    headers = {
        'Authorization': f'Token {token}'
    }

    if method == 'GET':
        result = requests.get(link, headers=headers, data=data, json=json)
    elif method == 'POST':
        result = requests.post(link, headers=headers, data=data, json=json)

    else: result = None

    if not result or result.status_code != 200:
        return False

    return result.json()
