# from itertools import product
import datetime
import hashlib
import hmac
import random
import re
import string
import time
import uuid
from wsgiref.simple_server import WSGIRequestHandler

import requests
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from icecream import ic
from pymongo import MongoClient

from magazine.models import Car, Districts, Houses, Yacht
from users.models import CustomUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

DOMEN = 'http://127.0.0.1:8000/'

client = MongoClient('mongodb://localhost:27017')
db = client.get_database('lalka')

coll = db.get_collection('users_customuser')
counter_collection = db.get_collection('counters')

db_districts = db.get_collection('districts')
db_yachts = db.get_collection('yachts')
db_cars = db.get_collection('cars')

db_jobs = db.get_collection('works')
db_items = db.get_collection('items')
db_rates = db.get_collection('rates')
db_stock = db.get_collection('stock')
db_crypt = db.get_collection('crypt')

db_coeff = db.get_collection('coefficient')
db_houses = db.get_collection('houses')
db_inv = db.get_collection('inventory')
db_log = db.get_collection('logging')
db_test = db.get_collection('tests')

db_admin = db.get_collection('admin')





def generate_ucode(k=9):
    """Генерирует уникальный код длиной 9 символов."""

    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=k))



def get_messages(request):
    return [{'level': message.level, 'message': message.message, 'extra_tags': message.extra_tags} for message in messages.get_messages(request)]


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


def get_next_sequence_value(sequence_name: str):
    if not counter_collection.find_one():
        # Если нет, создаем документ с начальным значением счетчика
        counter_collection.insert_one({'_id': 'your_collection_id', 
                                             'sequence_value': 1,
                                             'deal_id': 1,
                                             'crypt_id': 1})
    counter = counter_collection.find_one_and_update(
        {'_id': 'your_collection_id'},
        {'$inc': {sequence_name: 1}},
        return_document=True
    )
    return counter[sequence_name]

def get_crypto_info(name: str):
    data = db_crypt.find_one({'name': name})
    
    return {'name': data['name'], 'owner': data['owner'],
            'quantity': data['quantity'], 'symbol': data['symbol']}

def get_full_houses_info(house_id: int) -> list[dict]:
    house_info = get_house_by_id(house_id)
    district_info = get_district_by_id(house_info.district_id)
    house_info.district_info = district_info
    return house_info

#* ID
def get_house_by_id(house_id: int):
    try:
        return Houses.objects.get(id=house_id)
    except Houses.DoesNotExist: return None

def get_district_by_id(dis_id: int):
    try:
        return Districts.objects.get(district_id=dis_id)
    except Districts.DoesNotExist: return None

def get_car_by_id(car_id: int):
    try:
        return Car.objects.get(id=car_id)
    except Car.DoesNotExist: return None

def get_yacht_by_id(yacht_id: int):
    try:
        return Yacht.objects.get(id=yacht_id)
    except Yacht.DoesNotExist: return None

#* ucode
def get_transport_by_ucode(server_id: int, type: str, ucode: str):
    ic(server_id, type, ucode)
    user = CustomUser.objects.get(server_id=server_id)
    ic(user.car['cars'])
    ic(type)
    if type == 'car':
        for transport in user.car['cars']:
            if transport['ucode'] == ucode:
                return transport
    elif type == 'yacht':
        for transport in user.yacht['yachts']:
            if transport['ucode'] == ucode:
                return transport
    return None




def send_message_to_user(user_id, message):
    """
    Отправляет сообщение пользователю через WebSocket.
    """
    ic(message, user_id)
    channel_layer = get_channel_layer()
    group_name = f'user_{user_id}'
    # ic(message)
    message['text'] += ' WS'
    ic(message, 'haah')

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',  # Метод, который будет вызван в Consumer
            'message': message,          # Данные для отправки
        }
    )


def send_message_to_session(session_key, message):
    channel_layer = get_channel_layer()
    group_name = f"session_{session_key}"
    ic(group_name)
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "message": message,
        }
    )


class Money:
    #todo: переделать give_money на этот класс.
    def __init__(self, request: WSGIRequestHandler,
                 server_id: int, sum: int,
                 type_money: str = 'cash', comment=None):

        self._request = request
        self._server_id = server_id
        self._sum = sum
        self._type_money = type_money
        self._comment = comment

    @property
    def request(self):
        return self._request

    @property
    def server_id(self):
        return self._server_id

    @property
    def sum(self):
        return self._sum

    @property
    def type_money(self):
        return self._type_money

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        if value is not None and value != self._comment:
            self._comment = value
        return self._comment

    def give(self):
        user = self.request.user
        user.money[self.type_money] += (self.sum)
        user.save()
        return self

    def create_notification(self):
        if self.sum > 0 and not self.comment:
            # ic(sum > 0 and not comment)
            messages.success(self.request, f"На баланс начислено: {intcomma(sum)} {self.get_symbol_money(self._type_money)}")
        elif self.sum < 0 and not self.comment:
            # ic(sum < 0 and not comment)
            messages.success(self.request, f"С баланса списано: {intcomma(sum)} {self.get_symbol_money(self._type_money)}")
        elif self.comment:
            # ic(comment)
            messages.success(self.request, self.comment)

        return self

    @staticmethod
    def get_symbol_money(type_money: str = "cash"):
        if type_money in ("cash", "bank") : symbol = "₽"
        elif type_money == 'dollar': symbol = "$"
        elif type_money == 'bitcoin': symbol = "₿"
        else: symbol = "(?)"
        return symbol

def get_symbol_money(type_money: str = "cash"):
    if type_money in ("cash", "bank") : symbol = "₽"
    elif type_money == 'dollar': symbol = "$"
    elif type_money == 'bitcoin': symbol = "₿"
    else: symbol = "(?)"
    return symbol

def give_money(request: WSGIRequestHandler, server_id: int, sum: int, type_money: str = 'cash', comment=None):
    user = request.user
    user.money[type_money] += (sum)
    user.save()
    
    symbol = get_symbol_money(type_money)
    ic(comment)
    if sum > 0 and not comment:
        # ic(sum > 0 and not comment)
        comment = f"На баланс начислено: {intcomma(sum)} {symbol}"
        # messages.success(request, f"На баланс начислено: {intcomma(sum)} {symbol}")
    elif sum < 0 and not comment:
        # ic(sum < 0 and not comment)
        comment = f"С баланса списано: {intcomma(sum)} {symbol}"
        # messages.success(request, f"С баланса списано: {intcomma(sum)} {symbol}")
    # elif comment:
        # ic(comment)
        # messages.success(request, comment)

    ic(user.id, user.server_id)
    ic(comment)
    send_message_to_user(user.id, {'text': comment})

    return True


def calculate_total_quantity(house_id: int):
    house = get_house_by_id(house_id)
    quantity = 0
    
    for videocard in house['house_info'].get('basement', {})['videocards']:
        for name, value in videocard.items():
            ic(name, value)
            quantity += value['quantity']
    return quantity


def calculate_money(money: str) -> int:
    match = re.match(r'(\d+)([a-zA-Zа-яА-Я]+)?$', money)

    if match:
        stavka = int(match.group(1))
        suffix = match.group(2) or ''
        suffix_factors = {'k': 1e3, 'm': 1e6, 'b': 1e9, 'к': 1e3}

        if suffix in suffix_factors:
            stavka *= suffix_factors[suffix]
        elif suffix.startswith('k'):
            stavka *= 10**(3 * len(suffix))

        return stavka

def calculate_stavka(args, bablo=None):
    stavka = calculate_money(args)

    if args in ['вабанк', 'ва-банк', 'все', 'всё', 'all', 'олл']:
        stavka = bablo['money']['cash']

    return int(stavka)



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

def add_videocard_in_house(house_id: int, id_videocard: int, qty: int = 1):
    house_info = get_house_by_id(house_id)
    ic('yeeees')
    if house_info['basement']['videocards'].get(str(id_videocard)):
        return db_houses.update_one({'id': house_id},
                               {'$inc': {f'basement.videocards.{id_videocard}': qty}})
    db_houses.update_one({'id': house_id},
                               {'$set': {f'basement.videocards.{id_videocard}': qty}})
    

def get_item_by_id(item_id: int):
    return db_items.find_one({'id': item_id})

def get_item_in_inventory_user_by_id(server_id: int, item_id: int):
    return db_inv.find_one({'server_id': server_id, 'inventory.id': item_id})
def get_item_in_inventory_user_by_type(server_id: int, item_type: str):
    return db_inv.find_one({'server_id': server_id, 'inventory.type': item_type})



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
