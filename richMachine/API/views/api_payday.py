
from django.utils import timezone
from icecream import ic
from utils import (coll, db_houses, db_rates, db_stock, get_house_by_id,
                   get_item_by_id)


def give_payday():
    """
    Payday:\n
    Доход с видеокарт\n
    Процент в банке
    """

    counter = 0
    give_all_money = {
        "rubles": 0,
        "dollars": 0
        }
    
    for user in coll.find({'house.houses': {'$ne': []}}):

        # Добавление процентов в банке
        percent = user['money']['bank'] // 1500
        if percent >= 1:
            coll.update_one({'user_id': user['user_id']},
                            {"$inc": {"money.bank": percent}})
            give_all_money['rubles'] += percent
            
        if user['house'].get('houses'):
            balance_house = 0
            
            for house in user['house']['houses']:
                house_info = get_house_by_id(house['id'])
                
                if not house_info.get('basement', {}).get('videocards'):
                    continue
                
                for videocard, qty in house_info['basement']['videocards'].items():
                    videocard_info = get_item_by_id(int(videocard))
                    balance_house += videocard_info['attributes']['performance'] * qty
            
            db_houses.update_one({'id': house},
                                       {'$inc': {'basement.balance': balance_house // 24}})
            give_all_money['dollars'] += balance_house
        
        counter += 1
    
    # await log_action(user_id='payday', situation='give_payday', 
    #                  qty_users=counter, give_all_money=give_all_money)

def exchange_rates():
    # Получение уникальных типов криптовалют
    get_all_name_crypto = db_stock.aggregate([
        {
            '$group': {'_id': "$type_crypt"}
        },
        {
            '$project': {
                '_id': 0,
                'type_crypt': "$_id"
            }
        }
    ])
    
    # Получение текущих курсов валют из базы данных
    crypts = db_rates.find_one({})
    
    # Если курсов в базе данных нет, создаем пустую запись
    if not crypts:
        db_rates.insert_one({})
    
    # Обновление курсов валют в базе данных
    for crypt in get_all_name_crypto:
        
        # Получение всех записей о криптовалютах данного типа
        rates = db_stock.find({'type_crypt': crypt['type_crypt']}, projection={'_id': False})
        
        # Инициализация переменных для подсчета среднего значения цены
        quantity = 0
        unit_price = []

        # Рассчитываем среднюю цену для каждой криптовалюты
        for rate in rates:
            quantity += 1
            unit_price.append(rate['unit_price'])

        average_price = sum(unit_price) / quantity

        # Обновляем запись о курсе данной криптовалюты в базе данных
        db_rates.update_one({'_id': {'$exists': True}},
                            {'$set': {crypt['type_crypt']: average_price}})
    
    # new_course = db_rates.find_one({'_id': False})
    # ic(new_course)
    # log_action(user_id='exchange', situation='exchange_rates', new_course=new_course)
    ic(f"[Курс] Курс обновился. Текущее время: {timezone.now()}")