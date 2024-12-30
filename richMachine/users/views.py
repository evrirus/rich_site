# users/views.py

import json
from wsgiref.simple_server import WSGIRequestHandler
from django.db import transaction

from django.conf import settings
# from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from icecream import ic
from magazine.models import Car, Yacht, Houses

from utils import (coll, db_cars, db_houses, db_yachts, get_house_by_id,
                   get_messages, give_money, verify_telegram_auth, DoRequest, send_message_to_user)

from .forms import CustomUserCreationForm, LoginUserForm
from .models import CustomUser
from authentication import SiteAuthentication, TelegramAuthentication
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

DOMEN = 'http://127.0.0.1:8000/'

def register(request):
    if request.method == 'POST':
        ic(request.user.username)
        form = CustomUserCreationForm(request.POST)
        username = form.data['username']
        telegram_id = request.POST.get('telegram_id')

        if not telegram_id:
            send_message_to_user(telegram_id, {'text': 'Авторизация через телеграм обязательна.'})
            # messages.error(request, 'Telegram authentication is required.')
            return render(request, 'registration/signup.html', {'form': form})

        if CustomUser.objects.filter(username=username).exists():
            send_message_to_user(telegram_id, {'text': 'A user with that username already exists.'})
            # messages.error(request, 'A user with that username already exists.')
            return render(request, 'registration/signup.html', {'form': form})

        if form.is_valid():
            ic('valid')
            if CustomUser.objects.filter(telegram_id=telegram_id).exists():
                
                CustomUser.objects.update(telegram_id=telegram_id, username=username)
                send_message_to_user(telegram_id, {'text': 'Синхронизация данных | У вас уже имеется аккаунт зарегистрированный на этот телеграм.\nСвязываем телеграм и сайт.'})
                # messages.info(request, 'Синхронизация данных | У вас уже имеется аккаунт зарегистрированный на этот телеграм.\nСвязываем телеграм и сайт.')

            else:
                user = form.save(commit=False)
                user.telegram_id = int(telegram_id)
                user.save()
            
            login(request, user)
            return redirect('profile', server_id=user.server_id)
        else:
            for err in form.errors.get('password2', []):
                send_message_to_user(telegram_id, {'text': err})

    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})



@login_required(login_url="/users/login/")
def profile(request, server_id: int):
    # if request.user.server_id != server_id:
    #     return HttpResponseNotFound(render(request, '404.html'))

    data = {"action": "get_profile", "server_id": server_id, "source": "web"}
    response = DoRequest('api/get_profile/', 'POST', data=data)
    response['title'] = f'User profile ID: {response['server_id']}'
    
    return render(request, 'profile.html', response)


@login_required(login_url="/users/login/")
def self_profile(request: WSGIRequestHandler):
    return redirect(reverse('profile', kwargs={'server_id': request.user.server_id}))

def login_user(request):
    if request.method == 'POST':
        form = LoginUserForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            if request.POST.get('telegram_auth_data'):
                telegram_auth_data = json.loads(request.POST.get('telegram_auth_data'))
            else: telegram_auth_data = None

            user = None
            
            if username and password:
                user = authenticate(request, username=username, password=password)
                ic(user)
            elif telegram_auth_data:
                try:
                    if verify_telegram_auth(telegram_auth_data, settings.TELEGRAM_BOT_TOKEN):
                        telegram_id = telegram_auth_data['id']
                        user = authenticate(request, telegram_id=telegram_id)
                except (json.JSONDecodeError, KeyError):
                    send_message_to_user(request.user.id, {'text': 'Invalid Telegram data.'})
                    # messages.error(request, "Invalid Telegram data.")
                    return render(request, 'registration/login.html', {'form': form})

            if user:
                login(request, user)
                return redirect(reverse('profile', kwargs={'server_id': user.server_id}))
            else:
                send_message_to_user(request.user.id, {'text': 'Invalid username or password.'})
                # messages.error(request, "Invalid username or password.")
        else:
            ic(form.errors)
            send_message_to_user(request.user.id, {'text': 'Invalid username or password.'})
            # messages.error(request, "Invalid username or password.")
    else:
        form = LoginUserForm()
    return render(request, 'registration/login.html', {'form': form})


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'
    
    
class LoginView(CreateView):
    form_class = LoginUserForm
    success_url = reverse_lazy("login")
    template_name = "registration/login.html"

def loguot_user(request):
    send_message_to_user(request.user.id, {'text': 'Вы вышли с аккаунта'})
    # messages.success(request, "Вы вышли с аккаунта")
    return logout_then_login(request, login_url='/profile/')





    
class SellHouseView(APIView):
    """API для смены никнейма
    :param: NewNickname

    returns: success: bool, old_nickname: str, new_nickname: str,
             server_id: int, max_lenght: int"""
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []

    def post(self, request: Request, id: int):

        house_info = get_house_by_id(id)

        with transaction.atomic():
            for k, tr in enumerate(request.user.house['houses']):
                if tr['id'] == house_info.id:
                    request.user.house['houses'].remove(tr)
                    request.user.save()
                    break

            house = Houses.objects.get(id=house_info.id)
            house.owner = None
            house.save()

        give_money(request, request.user.server_id, house_info.price // 2)
        send_message_to_user(request.user.id, {'text': 'Продажа прошла успешно!'})
        # messages.success(request, 'Продажа прошла успешно!')
        return JsonResponse({'success': True})

def page_not_found(request, exception):
    ic(exception)
    return render(request, "404.html")


class RenderBasementView(APIView):
    """API для смены никнейма
    :param: NewNickname

    returns: success: bool, old_nickname: str, new_nickname: str,
             server_id: int, max_lenght: int"""
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []

    def get(self, request: Request, id_house: int):

        data = {"action": "get_basement", "server_id": request.user.server_id, "source": "web"}
        ic('api/get_basement/' + str(id_house) + '/')
        response = DoRequest('api/get_basement/' + str(id_house) + '/', 'GET', json=data)

        ic(response)

        income = 0
        current_videocards = len(response.get('videocards', []))

        limit_videocards = response['house_info']['basement'].get('maxQuantity', 0)
        for k in response['videocards']:
            income += k['performance']

        response.update({'my_server_id': request.user.server_id, 'income': income,
                         'quantity_videocards': current_videocards, 'limit_videocards': limit_videocards,
                         'mix_videocards': response['mix_videocards']})

        if not response.get('videocards', {}):
            response['success'] = False

        return render(request, 'basement.html', response)
