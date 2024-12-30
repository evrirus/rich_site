from authentication import SiteAuthentication, TelegramAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import TokenAuthentication
# from django.contrib import messages
from icecream import ic

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from utils import (get_full_houses_info,
                   send_message_to_user)
from users.models import CustomUser


# API смены никнейма
class ChangeNicknameView(APIView):
    """API для смены никнейма
    :param: NewNickname
    
    returns: success: bool, old_nickname: str, new_nickname: str,
             server_id: int, max_lenght: int"""
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []

    def post(self, request: Request):
        if not request.data:
            return Response({"success": False, "error": "data_is_empty"})
        
        data = request.data
        
        new_nickname = data.get('new_nickname')
        server_id = request.user.server_id
        old_nickname = request.user.nickname['name']
        max_length = request.user.nickname['max']
        
        if not new_nickname:
            send_message_to_user(request.user.id, {'text': 'Вы не указали нового имени.'})
            # messages.error(request, f"Вы не указали нового имени.")
            return Response({"success": False, "error": "nickname_is_empty"})
        
        if len(new_nickname) < 3:
            send_message_to_user(request.user.id, {'text': 'Указанное имя слишком короткое. Имя должно содержать более 3 символов'})
            # messages.error(request, f"Указанное имя слишком короткое. Имя должно содержать более 3 символов")
            return Response({"success": False, "error": "nickname_is_short"})
        
        if len(new_nickname) > max_length:
            send_message_to_user(request.user.id,
                                 {'text': f'Указанное имя слишком длинное. Максимальное количество символов: {max_length}'})
            # messages.error(request, f"Указанное имя слишком длинное. Максимальное количество символов: {max_length}")
            return Response({"success": False, "error": "nickname_is_long"})
        
        if new_nickname == old_nickname:
            send_message_to_user(request.user.id, {'text': 'Указанное имя совпадает с предыдущим.'})
            # messages.error(request, f"Указанное имя совпадает с предыдущим.")
            return Response({"success": False, "error": "nickname_is_the_same"})
        
        user = CustomUser.objects.get(server_id=server_id)
        user.nickname['name'] = new_nickname
        user.save()

        send_message_to_user(request.user.id, {'text': f'Теперь вы известны как {new_nickname}'})
        # messages.success(request, f"Теперь вы известны как {new_nickname}")
        return Response({"success": True, 
                         "old_nickname": old_nickname, "new_nickname": new_nickname, 
                         "server_id": server_id, "max_lenght": max_length})


class ProfileView(APIView):
    """API для получения информации о профиле
    :param: ID
    
    returns: success: bool, couple: dict, donate_balance: int, house: dict,
             is_active: bool, is_staff: bool, is_superuser: bool, job: str,
             job_lvl: int, language: str, last_login: datetime, money: dict,
             nickname: dict, registration: datetime, server_id: int, telegram_id: int,
             user_id: int, username: str, username_tg: str"""
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication, TokenAuthentication]
    permission_classes = []
    
    def post(self, request: Request):
        user_info = request.user
        my_server_id = user_info.server_id
        if not user_info:
            return Response({"success": False, "error": "user_not_found"})

        houses = [get_full_houses_info(x['id']) for x in user_info.house['houses']]
        # ic(houses[0].id)
        houses_standard_view = []
        for house in houses:

            houses_standard_view.append({'id': house.id, 'district_info': {'name': house.district_info.name},
                                        'price': house.price})

        ic(user_info.car)
        response_data = {
            "success": True,
            # "_id": user_info.get('_id'),
            "cars": user_info.car['cars'],
            # "yacht": user_info.yacht,
            "couple": user_info.couple,
            "donate_balance": user_info.donate_balance,
            "house": houses_standard_view,
            "is_active": user_info.is_active,
            "is_staff": user_info.is_staff,
            "is_superuser": user_info.is_superuser,
            "job": user_info.job['title'] if user_info.job['title'] else "Безработный",
            "job_lvl": user_info.job_lvl,
            "language": user_info.language,
            "last_login": user_info.last_login,
            "money": user_info.money,
            "nickname": user_info.nickname,
            "registration": user_info.registration,
            "server_id": user_info.server_id,
            "telegram_id": user_info.telegram_id,
            "user_id": user_info.user_id,
            "username": user_info.username,
            "username_tg": user_info.username_tg,
            
        }
        response_data.update(user_info.car)
        response_data.update(user_info.yacht)
        response_data['my_server_id'] = my_server_id
        
        # ic(user_info.car)

        if not request.user.is_anonymous:
            response_data['my_server_id'] = request.user.server_id
            response_data['my_username'] = request.user.username
        ic(response_data)
        return Response(response_data)

class ChangeLanguageView(APIView):
    """API для смены языка
    :param: None
    
    returns: success: bool, old_language: str, new_language: str"""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []
    
    def post(self, request: Request):
        
        languages = ['ru', 'en']

        language = request.user.language
        server_id = request.user.server_id

        index = languages.index(language)

        new_language_index = index + 1 if len(languages) - 1 >= index + 1 else 0
        new_language = languages[new_language_index]

        user = CustomUser.objects.get(server_id=server_id)
        user.language = new_language
        user.save()
        
        result = {"success": True, "old_language": language, "new_language": new_language}
        if not request.user.is_anonymous:
            send_message_to_user(request.user.id,
                                 {'text': f'Вы поменяли язык на {'Русский' if languages[new_language_index] == 'ru' else 'Английский'}'})
            # messages.success(request, f"Вы поменяли язык на {'Русский' if languages[new_language_index] == 'ru' else 'Английский'}")
        
        return Response(result)
    
class GetBalance(APIView):
    """API для получения баланса пользователя
    :param: None
    
    returns: success: bool, cash: int, bitcoin: int, ..."""
    
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []
    
    def post(self, request: Request):
        balance = request.user.money
        return Response({"success": True, "balance": balance})
    
    
class WarningAcceptSellTransportToState(APIView):
    """telegram | warning API для продажи транспорта пользователя государству
    :param: None
    
    returns: success: bool, type: str, info: dict"""
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
