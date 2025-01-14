from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse
from django.shortcuts import render
from icecream import ic
from rest_framework.request import Request

from inventory.models import Inventory, InventoryItem
from users.models import CustomUser
from utils import (generate_ucode,
                   get_district_by_id, get_house_by_id, get_item_by_id,
                   send_message_to_user, Money)
from .models import Car, Yacht, Districts, Houses, Items


# Create your views here.

@login_required(login_url="/users/login/")
def magazin(request: Request):
    data = {
        "items": [{
            "code": "cars",
            "title": "Автомобили",
            "svg": """<svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg"><g clip-path="url(#clip0_295_2)"><path d="M9.44991 13.1813C10.1733 11.4938 11.3763 10.0558 12.9095 9.04584C14.4428 8.03588 16.2389 7.49837 18.0749 7.5H41.9324C45.6824 7.5 49.0724 9.735 50.5499 13.1813L53.5199 20.1112C53.8012 20.7675 54.3074 21.3075 54.9449 21.6263C56.8199 22.5638 58.1512 24.3075 58.5637 26.3587L59.8199 32.655C59.9449 33.26 60.0062 33.8725 60.0037 34.4925V36.0412C60.0037 39.0938 58.5412 41.8275 56.2537 43.53V50.625C56.2537 51.1223 56.0561 51.5992 55.7045 51.9508C55.3529 52.3025 54.8759 52.5 54.3787 52.5H46.8787C46.3814 52.5 45.9045 52.3025 45.5528 51.9508C45.2012 51.5992 45.0037 51.1223 45.0037 50.625V45.6075C40.1587 45.7875 34.7099 45.9375 30.0037 45.9375C25.2974 45.9375 19.8487 45.7875 15.0037 45.6075V50.625C15.0037 51.1223 14.8061 51.5992 14.4545 51.9508C14.1029 52.3025 13.6259 52.5 13.1287 52.5H5.62866C5.13138 52.5 4.65447 52.3025 4.30284 51.9508C3.95121 51.5992 3.75366 51.1223 3.75366 50.625V43.53C1.46616 41.8275 0.00366211 39.0938 0.00366211 36.0412V34.4925C0.00429147 33.8754 0.06584 33.26 0.187412 32.655L1.44366 26.355C1.85616 24.3075 3.18741 22.56 5.05866 21.6263C5.70053 21.308 6.20733 20.7706 6.48741 20.1112L9.45741 13.1813H9.44991ZM11.2499 37.5C12.2445 37.5 13.1983 37.1049 13.9016 36.4016C14.6048 35.6984 14.9999 34.7446 14.9999 33.75C14.9999 32.7554 14.6048 31.8016 13.9016 31.0984C13.1983 30.3951 12.2445 30 11.2499 30C10.2554 30 9.30152 30.3951 8.59826 31.0984C7.895 31.8016 7.49991 32.7554 7.49991 33.75C7.49991 34.7446 7.895 35.6984 8.59826 36.4016C9.30152 37.1049 10.2554 37.5 11.2499 37.5ZM48.7499 37.5C49.7445 37.5 50.6983 37.1049 51.4016 36.4016C52.1048 35.6984 52.4999 34.7446 52.4999 33.75C52.4999 32.7554 52.1048 31.8016 51.4016 31.0984C50.6983 30.3951 49.7445 30 48.7499 30C47.7553 30 46.8015 30.3951 46.0983 31.0984C45.395 31.8016 44.9999 32.7554 44.9999 33.75C44.9999 34.7446 45.395 35.6984 46.0983 36.4016C46.8015 37.1049 47.7553 37.5 48.7499 37.5ZM22.4999 30C21.5054 30 20.5515 30.3951 19.8483 31.0984C19.145 31.8016 18.7499 32.7554 18.7499 33.75C18.7499 34.7446 19.145 35.6984 19.8483 36.4016C20.5515 37.1049 21.5054 37.5 22.4999 37.5H37.4999C38.4945 37.5 39.4483 37.1049 40.1516 36.4016C40.8548 35.6984 41.2499 34.7446 41.2499 33.75C41.2499 32.7554 40.8548 31.8016 40.1516 31.0984C39.4483 30.3951 38.4945 30 37.4999 30H22.4999ZM10.8974 19.4588C10.7508 19.7612 10.6865 20.0969 10.711 20.4321C10.7355 20.7674 10.8479 21.0902 11.0369 21.3681C11.2258 21.6461 11.4847 21.8693 11.7874 22.0154C12.0901 22.1614 12.426 22.2251 12.7612 22.2C16.1737 21.9263 25.3237 21.5625 29.9999 21.5625C34.6762 21.5625 43.8299 21.9263 47.2387 22.2C47.5738 22.2251 47.9097 22.1614 48.2124 22.0154C48.5151 21.8693 48.774 21.6461 48.963 21.3681C49.1519 21.0902 49.2643 20.7674 49.2888 20.4321C49.3133 20.0969 49.249 19.7612 49.1024 19.4588L45.5174 12.285C45.3615 11.9739 45.1222 11.7124 44.8262 11.5296C44.5301 11.3468 44.1891 11.25 43.8412 11.25H16.1587C15.8107 11.25 15.4697 11.3468 15.1737 11.5296C14.8776 11.7124 14.6383 11.9739 14.4824 12.285L10.8974 19.4588Z" fill="white"/></g><defs><clipPath id="clip0_295_2"><rect width="60" height="60" fill="white"/></clipPath></defs></svg>"""
        },
            {
                "code": "districts",
                "title": "Районы",
                "svg": """<svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.5 52.5V17.625H22.9375V11.875L30 5.00001L37.0625 11.875V28H52.5V52.5H7.5ZM11.25 48.75H17.875V42.125H11.25V48.75ZM11.25 38.375H17.875V31.75H11.25V38.375ZM11.25 28H17.875V21.375H11.25V28ZM26.6875 48.75H33.3125V42.125H26.6875V48.75ZM26.6875 38.375H33.3125V31.75H26.6875V38.375ZM26.6875 28H33.3125V21.375H26.6875V28ZM26.6875 17.625H33.3125V11H26.6875V17.625ZM42.125 48.75H48.75V42.125H42.125V48.75ZM42.125 38.375H48.75V31.75H42.125V38.375Z" fill="#E8EAED"/></svg>"""
            },
            # {
            #     "code": "houses",
            #     "title": "Недвижимость",
            #     "svg": """<svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.5 52.5V17.625H22.9375V11.875L30 5.00001L37.0625 11.875V28H52.5V52.5H7.5ZM11.25 48.75H17.875V42.125H11.25V48.75ZM11.25 38.375H17.875V31.75H11.25V38.375ZM11.25 28H17.875V21.375H11.25V28ZM26.6875 48.75H33.3125V42.125H26.6875V48.75ZM26.6875 38.375H33.3125V31.75H26.6875V38.375ZM26.6875 28H33.3125V21.375H26.6875V28ZM26.6875 17.625H33.3125V11H26.6875V17.625ZM42.125 48.75H48.75V42.125H42.125V48.75ZM42.125 38.375H48.75V31.75H42.125V38.375Z" fill="#E8EAED"/></svg>"""
            # },
            {
                "code": "videocards",
                "title": "Видеокарты",
                "svg": """<svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg"><g clip-path="url(#clip0_285_97)"><path d="M0 1.87502C0 1.37773 0.197544 0.900821 0.549175 0.54919C0.900806 0.197559 1.37772 1.52588e-05 1.875 1.52588e-05L58.125 1.52588e-05C58.6223 1.52588e-05 59.0992 0.197559 59.4508 0.54919C59.8025 0.900821 60 1.37773 60 1.87502V13.125C60 13.6223 59.8025 14.0992 59.4508 14.4508C59.0992 14.8025 58.6223 15 58.125 15H52.5V22.5H58.125C58.6223 22.5 59.0992 22.6976 59.4508 23.0492C59.8025 23.4008 60 23.8777 60 24.375V35.625C60 36.1223 59.8025 36.5992 59.4508 36.9508C59.0992 37.3025 58.6223 37.5 58.125 37.5H52.5V45H58.125C58.6223 45 59.0992 45.1976 59.4508 45.5492C59.8025 45.9008 60 46.3777 60 46.875V58.125C60 58.6223 59.8025 59.0992 59.4508 59.4508C59.0992 59.8025 58.6223 60 58.125 60H1.875C1.37772 60 0.900806 59.8025 0.549175 59.4508C0.197544 59.0992 0 58.6223 0 58.125V46.875C0 46.3777 0.197544 45.9008 0.549175 45.5492C0.900806 45.1976 1.37772 45 1.875 45H7.5V37.5H1.875C1.37772 37.5 0.900806 37.3025 0.549175 36.9508C0.197544 36.5992 0 36.1223 0 35.625V24.375C0 23.8777 0.197544 23.4008 0.549175 23.0492C0.900806 22.6976 1.37772 22.5 1.875 22.5H7.5V15H1.875C1.37772 15 0.900806 14.8025 0.549175 14.4508C0.197544 14.0992 0 13.6223 0 13.125V1.87502ZM11.25 15V22.5H28.125V15H11.25ZM31.875 15V22.5H48.75V15H31.875ZM11.25 37.5V45H28.125V37.5H11.25ZM31.875 37.5V45H48.75V37.5H31.875ZM3.75 3.75002V11.25H16.875V3.75002H3.75ZM20.625 3.75002V11.25H39.375V3.75002H20.625ZM43.125 3.75002V11.25H56.25V3.75002H43.125ZM3.75 26.25V33.75H16.875V26.25H3.75ZM20.625 26.25V33.75H39.375V26.25H20.625ZM43.125 26.25V33.75H56.25V26.25H43.125ZM3.75 48.75V56.25H16.875V48.75H3.75ZM20.625 48.75V56.25H39.375V48.75H20.625ZM43.125 48.75V56.25H56.25V48.75H43.125Z" fill="white"/></g><defs><clipPath id="clip0_285_97"><rect width="60" height="60" fill="white"/></clipPath></defs></svg>""",
            },
            {
                "code": "yachts",
                "title": "Яхты",
                "svg": """<svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.5 33.75L27.5 5V33.75H7.5ZM17.0625 28.75H22.5V20.9375L17.0625 28.75ZM31.25 33.75C31.75 32.5833 32.2917 30.5417 32.875 27.625C33.4583 24.7083 33.75 21.75 33.75 18.75C33.75 15.75 33.4688 12.6667 32.9062 9.5C32.3438 6.33333 31.7917 4 31.25 2.5C33.7917 3.25 36.3229 4.64583 38.8438 6.6875C41.3646 8.72917 43.6354 11.1667 45.6562 14C47.6771 16.8333 49.3229 19.9479 50.5938 23.3438C51.8646 26.7396 52.5 30.2083 52.5 33.75H31.25ZM37.75 28.75H47C46.2917 25.5417 45.1354 22.6042 43.5312 19.9375C41.9271 17.2708 40.2292 15 38.4375 13.125C38.5208 14 38.5938 14.9062 38.6562 15.8438C38.7188 16.7812 38.75 17.75 38.75 18.75C38.75 20.7083 38.6562 22.5208 38.4688 24.1875C38.2812 25.8542 38.0417 27.375 37.75 28.75ZM22.5 47.5C21 47.5 19.6042 47.1458 18.3125 46.4375C17.0208 45.7292 15.9167 44.8333 15 43.75C14.4167 44.375 13.7812 44.9583 13.0938 45.5C12.4062 46.0417 11.6458 46.4792 10.8125 46.8125C9.35417 45.7292 8.11458 44.3854 7.09375 42.7812C6.07292 41.1771 5.375 39.4167 5 37.5H55C54.625 39.4167 53.9271 41.1771 52.9062 42.7812C51.8854 44.3854 50.6458 45.7292 49.1875 46.8125C48.3542 46.4792 47.5938 46.0417 46.9062 45.5C46.2188 44.9583 45.5833 44.375 45 43.75C44.0417 44.8333 42.9271 45.7292 41.6562 46.4375C40.3854 47.1458 39 47.5 37.5 47.5C36 47.5 34.6042 47.1458 33.3125 46.4375C32.0208 45.7292 30.9167 44.8333 30 43.75C29.0833 44.8333 27.9792 45.7292 26.6875 46.4375C25.3958 47.1458 24 47.5 22.5 47.5ZM5 57.5V52.5H7.5C8.83333 52.5 10.1354 52.2917 11.4062 51.875C12.6771 51.4583 13.875 50.8333 15 50C16.125 50.8333 17.3229 51.4479 18.5938 51.8438C19.8646 52.2396 21.1667 52.4375 22.5 52.4375C23.8333 52.4375 25.125 52.2396 26.375 51.8438C27.625 51.4479 28.8333 50.8333 30 50C31.125 50.8333 32.3229 51.4479 33.5938 51.8438C34.8646 52.2396 36.1667 52.4375 37.5 52.4375C38.8333 52.4375 40.125 52.2396 41.375 51.8438C42.625 51.4479 43.8333 50.8333 45 50C46.1667 50.8333 47.375 51.4583 48.625 51.875C49.875 52.2917 51.1667 52.5 52.5 52.5H55V57.5H52.5C51.2083 57.5 49.9375 57.3438 48.6875 57.0312C47.4375 56.7188 46.2083 56.25 45 55.625C43.7917 56.25 42.5625 56.7188 41.3125 57.0312C40.0625 57.3438 38.7917 57.5 37.5 57.5C36.2083 57.5 34.9375 57.3438 33.6875 57.0312C32.4375 56.7188 31.2083 56.25 30 55.625C28.7917 56.25 27.5625 56.7188 26.3125 57.0312C25.0625 57.3438 23.7917 57.5 22.5 57.5C21.2083 57.5 19.9375 57.3438 18.6875 57.0312C17.4375 56.7188 16.2083 56.25 15 55.625C13.7917 56.25 12.5625 56.7188 11.3125 57.0312C10.0625 57.3438 8.79167 57.5 7.5 57.5H5Z" fill="#E8EAED"/></svg>"""
            }],
        'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
        'title': 'Magazine'
    }

    return render(request, 'magazine/magazine.html', data)


@login_required(login_url="/users/login/")
def get_transport_info(request: Request, type: str, id: int):
    ic(type, request.method)
    if type == 'cars':
        transport = Car.objects.get(id=id)
        # transport = db_cars.find_one({'id': id})
    elif type == 'yachts':
        # transport = Yacht.objects.filter(id=id).first()
        transport = Yacht.objects.get(id=id)
    else:
        return JsonResponse({'error': 'Invalid type'})

    data = {
        'name': transport.name,  #transport.get('name'),
        'price': intcomma(transport.price),  #intcomma(transport.get('price')),
        'produced': intcomma(transport.max_quantity),
        'quantity': intcomma(transport.quantity),
    }

    return JsonResponse(data)


@login_required(login_url="/users/login")
def buy_transport(request: Request, type, id):
    if request.method == 'POST':
        # user_server_id = request.POST.get('server_id') or request.user.server_id
        user = request.user
        # user_info = coll.find_one({'server_id': request.user.server_id})
        if type == 'yachts':
            transport_info = Yacht.objects.get(id=id)
            if user.yacht.get('maxPlaces', 2) <= len(user.yacht.get('yachts', {})):
                send_message_to_user(request.user.server_id, {'text': 'Превышено максимальное количество мест в вашем флоте.'})
                # messages.error(request, 'Превышено максимальное количество мест в вашем флоте.')
                return JsonResponse({'success': False})

        elif type == 'cars':
            transport_info = Car.objects.get(id=id)

            if user.car.get('maxPlaces', 2) <= len(user.car.get('cars', {})):
                send_message_to_user(request.user.server_id, {'text': 'Превышено максимальное количество мест в вашем гараже.'})
                # messages.error(request, 'Превышено максимальное количество мест в вашем гараже.')
                return JsonResponse({'success': False})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid type'})

        if transport_info.quantity <= 0:
            send_message_to_user(request.user.server_id, {'text': 'Транспорт раскуплен.'})
            # messages.error(request, 'Транспорт раскуплен.')
            return JsonResponse({'success': False})

        if user.money.get('cash', {}) < transport_info.price:
            send_message_to_user(request.user.server_id, {'text': 'Недостаточно средств.'})
            # messages.error(request, 'Недостаточно средств.')
            return JsonResponse({'success': False})

        sample = {
            'id': transport_info.id,
            'name': transport_info.name,
            'price': transport_info.price,
            'plate': None,
            'ucode': generate_ucode()
        }

        money = Money(request, -transport_info.price).give()

        if type == 'cars':
            user.car['cars'].append(sample)

            car = Car.objects.get(id=transport_info.id)
            car.quantity -= 1
            car.save()
        else:
            user.yacht['yachts'].append(sample)

            yacht = Yacht.objects.get(id=transport_info.id)
            yacht.quantity -= 1
            yacht.save()

        user.save()
        money.create_notification('Покупка прошла успешно!')

        return JsonResponse({'success': True, 'type': type, 'id': id})
    else:
        return JsonResponse({'success': False, 'message': 'Метод не поддерживается.'})


@login_required(login_url="/users/login")
def get_house_info(request: Request, house_id: int):
    house_info = get_house_by_id(house_id)
    district_info = get_district_by_id(house_info.district_id)
    house_info.district_info = district_info
    ic(house_info.class_field)

    return JsonResponse({'district_name': house_info.district_info.name,
                         'house_type': "Дом" if house_info.type_field == "house" else "Квартира",
                         'house_id': intcomma(house_info.id),
                         'house_id_for_district': house_info.id_for_district,
                         'house_price': intcomma(house_info.price),
                         'house_basement': f"Имеется[<span style='color: rgb(255, 28, 28);'>lvl</span>={house_info.basement['level']}]" if
                         house_info.basement else "Отсутствует",
                         #  'house_basement_level': house_info['basement']['level'] if house_info['basement'] else 0,
                         'house_floor': house_info.floors,
                         'house_class': house_info.class_field})


@login_required(login_url="/users/login")
def buy_house(request: Request, id: int):
    house_info = get_house_by_id(id)
    if house_info.owner:
        send_message_to_user(request.user.server_id, {'text': 'Дом уже занят!'})
        # messages.error(request, "Дом уже занят!")
        return JsonResponse({'success': False})

    user_info = request.user

    if user_info.money.get('cash', {}) < house_info.price:
        send_message_to_user(request.user.server_id, {'text': 'Недостаточно средств.'})
        # messages.error(request, 'Недостаточно средств.')
        return JsonResponse({'success': False})

    if user_info.house.get('maxPlaces', 2) <= len(user_info.house.get('houses', {})):
        send_message_to_user(request.user.server_id, {'text': 'Превышено максимальное количество.'})
        # messages.error(request, 'Превышено максимальное количество.')
        return JsonResponse({'success': False})

    money = Money(request, -house_info.price).give()

    user = CustomUser.objects.get(server_id=user_info.server_id)
    user.house['houses'].append({'id': house_info.id})
    user.save()

    house = Houses.objects.get(id=house_info.id)
    house.owner = user_info.server_id
    house.save()

    money.create_notification('Дом успешно приобретен!')

    return JsonResponse({'success': True})


@login_required(login_url="/users/login/")
def get_videocard_info(request: Request, videocard_id: int):
    ic(videocard_id)
    videocard = Items.objects.get(id=videocard_id)
    # videocard = db_items.find_one({'id': videocard_id})
    ic(videocard)

    data = {
        'name': videocard.name,
        'price': intcomma(videocard.price),
        'currency': 'USD',
        'performance': intcomma(videocard.attributes.get('performance')),
        'maxQuantity': intcomma(videocard.max_quantity),
        'type': videocard.type
    }
    ic(data)
    return JsonResponse(data)


@login_required(login_url="/users/login")
def buy_videocard(request: Request, videocard_id: int):
    videocard_info = get_item_by_id(videocard_id)
    ic(videocard_info, 'buy_videocard')

    if request.user.money.get('dollar', {}) < videocard_info.price:

        send_message_to_user(request.user.server_id, {'text': 'Недостаточно средств.'})
        return JsonResponse({'success': False, 'message': 'Недостаточно средств.', })

    user_inventory = Inventory.objects.get(user=request.user)
    inventory_items = InventoryItem.objects.filter(inventory=user_inventory)
    ic(inventory_items[0].item_id)
    if len(inventory_items) >= user_inventory.max_quantity:

        send_message_to_user(request.user.server_id, {'text': 'Ваш инвентарь полон. Недостаточно места.'})
        return JsonResponse({'success': False, 'message': 'Ваш инвентарь полон. Недостаточно места.'})

    money = Money(request, -videocard_info.price, type_money='dollar').give()

    inventory_items.create(inventory=user_inventory, item_id=videocard_info.id, item_type=videocard_info.type)

    money.create_notification(f'Видеокарта {videocard_info} куплена!')

    return JsonResponse({"success": True})


class Magazine:

    @staticmethod
    def get_cars():
        return Car.objects.filter(quantity__gt=0)

    @staticmethod
    def get_yachts():
        return Yacht.objects.filter(quantity__gt=0)

    @staticmethod
    def get_districts():
        return Districts.objects.all()

    @staticmethod
    def get_free_houses_by_district_id(district_id):
        return list(set(Houses.objects.filter(district_id=district_id, owner=None)))

    @staticmethod
    def get_videocards():
        return Items.objects.filter(type='videocard')



def get_cars(request: Request):
    with open(r'C:\Users\kovalskiy\Documents\GitHub\rich_site\richMachine\magazine\static\magazine\img\transport.svg',
              'r') as file:
        icon_content = file.read()

    return render(request,
                  'magazine/magazine_transport.html',
                  {
                      'type': 'cars',
                      'icon': icon_content,
                      'transport': Magazine().get_cars(),
                      'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
                      'title': 'Cars'})


def get_yachts(request: Request):

    with open(r'C:\Users\kovalskiy\Documents\GitHub\rich_site\richMachine\magazine\static\magazine\img\transport.svg',
              'r') as file:
        icon_content = file.read()
    return render(request,
                  'magazine/magazine_transport.html',
                  {
                      'type': 'yachts',
                      'icon': icon_content,
                      'transport': Magazine().get_yachts(),
                      'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
                      'title': 'Yachts'})


def get_districts(request: Request):

    with open(r'C:\Users\kovalskiy\Documents\GitHub\rich_site\richMachine\magazine\static\magazine\img\district.svg',
              'r') as file:
        icon_content = file.read()

    return render(request,
                  'magazine/magazine_districts.html',
                  {
                      'type': 'districts',
                      'icon': icon_content,
                      'districts': Magazine().get_districts(),
                      'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
                      'title': 'Districts'})


def get_houses(request: Request, district_id: int):
    with open(r'C:\Users\kovalskiy\Documents\GitHub\rich_site\richMachine\magazine\static\magazine\img\house.svg',
              'r') as file:
        icon_content = file.read()

    return render(request,
                  'magazine/magazine_houses.html',
                  {'type': 'houses',
                   'icon': icon_content,
                   'houses': Magazine().get_free_houses_by_district_id(district_id),
                   'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
                   'title': 'Houses'})


def get_videocards(request: Request):
    with open(r'C:\Users\kovalskiy\Documents\GitHub\rich_site\richMachine\magazine\static\magazine\img\videocard.svg',
              'r') as file:
        icon_content = file.read()

    return render(request,
                    'magazine/magazine_videocards.html',
                  {
                      'type': 'videocard',
                   'icon': icon_content,
                   'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
                   'title': 'Videocards',
                   'videocards': Magazine().get_videocards()
                  }
                  )
