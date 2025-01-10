
from django.utils import timezone
from icecream import ic

from magazine.models import Houses
from users.models import CustomUser
from django.db.models import Q
from utils import (coll, db_houses, db_rates, db_stock, get_house_by_id,
                   get_item_by_id)


def give_payday():
    """
    Payday:\n
    Доход с видеокарт\n
    Процент в банке
    """

    counter = 0
    total_distributed_money = {
        "rubles": 0,
        "dollars": 0
        }

    # Фильтруем только пользователей с домами
    users_with_houses = CustomUser.objects.filter(~Q(house__houses=[]))

    for user in users_with_houses:
        # Начисление процентов на банковский баланс
        percent = user.money['bank'] // 1500
        if percent >= 1:
            user.money['bank'] += percent
            total_distributed_money['rubles'] += percent

        # Проверяем наличие домов у пользователя
        houses = user.house.get('houses', [])
        if houses:
            total_house_income = 0

            for house in houses:
                house_info = get_house_by_id(house['id'])

                # Проверяем наличие видеокарт в доме
                basement = house_info.basement
                videocards = basement.get('videocards', {})

                ic(videocards)

                if not videocards:
                    continue

                # Вычисляем доход с видеокарт
                for videocard_id, qty in videocards.items():
                    videocard_info = get_item_by_id(int(videocard_id))
                    ic(videocard_info, videocard_id, qty)
                    performance = videocard_info.attributes.get('performance', 0)
                    total_house_income += performance * qty

                # Обновляем баланс в доме
                house_info.basement['balance'] += total_house_income // 24
                house_info.save()

                total_distributed_money['dollars'] += total_house_income


        # Сохраняем изменения в пользователе
        user.save()
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