from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse

from authentication import SiteAuthentication, TelegramAuthentication
from django.contrib.auth.decorators import login_required

from icecream import ic

from magazine.models import Car, Items, Yacht
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from offer.models import OfferModel
from users.models import CustomUser
from utils import (Money, generate_ucode, get_car_by_id, get_transport_by_ucode,
                   get_yacht_by_id, send_message_to_user)


class GetMyCarsView(APIView):
    """API для получения списка машин пользователя
    :param: None
    
    returns: success: bool, cars: list"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        data = request.GET or request.data
        ic(data)


        func = get_yacht_by_id if data['type'] == 'yacht' else get_car_by_id if data['type'] == 'car' else None
        if not func:
            return Response({"success": False, "error": "invalid_type"})

        data_transport = func(int(data['id']))

        if data.get('ucode'):

            result = {
                **get_transport_by_ucode(request, data['type'], data['ucode']),
                'quantity': data_transport.quantity,
                'maxQuantity': data_transport.max_quantity,
            }

            ic(result)
            return Response({"success": True, "info": result})
        else:
            transport = func(int(data['id']))
            if not transport:
                return Response({"success": False, 'error': "invalid_transport"})
            
            return Response({"success": True, 'name': transport.name, 'max_quantity': transport.max_quantity,
                             'price': transport.price, 'quantity': transport.quantity, 'id': transport.id})

        


class SellTransportToState(APIView):
    """API для продажи транспорта пользователя
    :param: None

    returns: success: bool, type: str, info: dict"""
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, type: str, ucode: str):
        ic(request)
        # ic(args)
        # ic(kwargs)

        if type not in ('car', 'yacht'):
            return Response({'success': False, 'error': 'Неверный тип транспорта'})

        user = request.user
        if not user:
            return Response({'success': False, 'error': 'Пользователь не найден'})

        if type == 'car':
            transports = user.car['cars']
        else:
            transports = user.yacht['yachts']

        num = 0
        for k, tr in enumerate(transports):
            if tr['ucode'] == ucode:
                num = k
        if type == 'car':
            items = user.car.get('cars', [])
        else:
            items = user.yacht.get('yachts', [])

        ic(items, num)
        transport_info = items[num]
        items.pop(num)

        if type == 'car':
            user.car['cars'] = items
        else:
            user.yacht['yachts'] = items
        user.save()

        money = Money(request, transport_info['price'] // 2).give()

        if type == 'car':
            car = Car.objects.get(id=transport_info['id'])
            car.quantity += 1
            car.save()

        elif type == 'yacht':
            yacht = Yacht.objects.get(id=transport_info['id'])
            yacht.quantity += 1
            yacht.save()

        else:
            ic('ASHIBKA')

        money.create_notification('Транспорт успешно продан!')

        return Response({'success': True, 'message': 'Транспорт успешно продан!'})


class BuyTransportView(APIView):
    """
    Класс для обработки покупки транспорта. Он позволяет пользователю купить транспорт (автомобиль или яхту).
    В случае успешной покупки происходит списание средств с баланса пользователя и добавление транспорта в его коллекцию.
    """
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Метод для обработки POST-запроса на покупку транспорта. Проверяет:
        1. Тип транспорта (автомобиль или яхта).
        2. Доступность транспорта (есть ли его в наличии).
        3. Достаточно ли средств у пользователя.
        
        Если все проверки пройдены, транспорт добавляется в коллекцию пользователя и происходит списание средств.
        В случае ошибки возвращается ответ с соответствующим сообщением.
        """
        
        user = request.user
        transport_type = request.data.get('type')
        transport_id = request.data.get('id')
        ic(transport_type, transport_id)

        # Проверяем, что тип транспорта корректный
        if transport_type not in ['yacht', 'car']:
            return Response({'success': False, 'message': 'Invalid type'}, status=400)

        # Получаем информацию о транспорте
        if transport_type == 'yacht':
            transport_info = Yacht.objects.get(id=transport_id)
            
            if user.yacht.get('maxPlaces', 2) <= len(user.yacht.get('yachts', {})):
                send_message_to_user(request, {'text': 'Превышено максимальное количество мест в вашем флоте.'})
                return Response({'success': False})
            
        elif transport_type == 'car':
            transport_info = Car.objects.get(id=transport_id)
            
            if user.car.get('maxPlaces', 2) <= len(user.car.get('cars', {})):
                send_message_to_user(request, {'text': 'Превышено максимальное количество мест в вашем гараже.'})
                return Response({'success': False})

        # Проверяем наличие транспорта
        if transport_info.quantity <= 0:
            send_message_to_user(request, {'text': 'Транспорт раскуплен.'})
            return Response({'success': False})

        # Проверяем наличие средств у пользователя
        if user.money.get('cash', {}) < transport_info.price:
            send_message_to_user(request, {'text': 'Недостаточно средств.'})
            return Response({'success': False})

        # Проводим покупку
        sample = {
            'id': transport_info.id,
            'name': transport_info.name,
            'price': transport_info.price,
            'plate': None,
            'ucode': generate_ucode()
        }

        # Отнимаем деньги с баланса пользователя
        money = Money(request, -transport_info.price).give()

        # Добавляем транспорт в коллекцию пользователя
        if transport_type == 'car':
            user.car['cars'].append(sample)
            transport_info.quantity -= 1
            transport_info.save()
            
        elif transport_type == 'yacht':
            user.yacht['yachts'].append(sample)
            transport_info.quantity -= 1
            transport_info.save()

        # Сохраняем данные пользователя и уведомляем
        user.save()
        money.create_notification('Покупка прошла успешно!')

        return Response({'success': True, 'type': transport_type, 'id': transport_id})

class SellTransportToPlayer(APIView):
    """
    Класс для предложения продажи автомобиля другому пользователю
    """

    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def validate_positive_integer(self, value, field_name):
        """Проверяет, является ли значение положительным целым числом."""
        if isinstance(value, str) and value.isdigit():
            return int(value)
        else:
            raise ValueError("data is wrong")

    def post(self, request: Request):

        if not request.data:
            return JsonResponse({'success': False, 'error': 'data not found'})


        try:
            price = self.validate_positive_integer(request.data.get('price'), 'price')
            server_id = self.validate_positive_integer(request.data.get('user_id'), 'user_id')
            transport_id = self.validate_positive_integer(request.data.get('id'), 'id')
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})

        if server_id == request.user.server_id:
            return JsonResponse({'success': False, 'error': 'Вы не можете продавать сами себе.'})

        transport = get_transport_by_ucode(request, request.data.get('type'), request.data.get('ucode'))
        if not transport:
            return JsonResponse({'success': False, 'error': 'Данное транспортное средство не найдено в вашем владении.'})

        try:
            to_user = CustomUser.objects.get(server_id=server_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пользователь с таким ID не найден.'}, status=404)

        OfferModel.objects.create(
            thing_type=request.data['type'],
            thing_id=transport_id,
            seller=request.user,
            buyer=to_user,
            price=price
        )

        #TODO: Сделать, чтобы при заходе появлились уведомления, о том, что есть уведомление.
        text = (f'Ваше предложение о продаже {transport['name']} за {intcomma(price)}'
                f' отправлено пользователю {to_user.nickname['name']}')
        return JsonResponse({'success': True, 'message': text})