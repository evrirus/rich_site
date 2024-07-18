import datetime
import re

from icecream import ic
from pymongo import MongoClient

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

def get_house_by_id(house_id: int):
    return db_houses.find_one({'id': house_id}, projection={'_id': False})

def get_district_by_id(dis_id: int):
    return db_districts.find_one({'district_id': dis_id}, projection={'_id': False})

def get_car_by_id(car_id: int):
    return db_cars.find_one({'id': car_id})

def get_yacht_by_id(yacht_id: int):
    return db_yachts.find_one({'id': yacht_id})

def give_money(user_id: int, sum: int, type_money: str = 'cash'):
    result = coll.update_one(
        {'user_id': user_id},
        {'$inc': {f'money.{type_money}': sum}}
    )
    if result.modified_count > 0:
        return True
    return False


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
    item_info = db_items.find_one({'_id': item_id})

    return item_info


def get_item_by_name(item_name: str):
    video_info = db_items.find_one({'items': {'$elemMatch': {'name': item_name}}}, projection={'items.$': 1, '_id': False})
    # ic(video_info)
    return {'model': video_info['items'][0]['name'], 
            'attributes': video_info['items'][0]['attributes'],
            'price': video_info['items'][0]['price'],
            'id': video_info['items'][0]['_id']}


def add_inventory(user_id: int, id_item: str, quantity: int = 1):
    user_inv = db_inv.find_one({'user_id': user_id})
    
    if user_inv['inventory'].get(f'{id_item}'):
        return db_inv.update_one({'user_id': user_id},
                                       {'$inc': {f'inventory.{id_item}': quantity}})
    
    db_inv.update_one({'user_id': user_id},
                            {'$set': {f'inventory.{id_item}': quantity}})

    
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


