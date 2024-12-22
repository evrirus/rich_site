# users/views.py

import json
from wsgiref.simple_server import WSGIRequestHandler
from django.db import transaction

import requests
from django.conf import settings
from django.contrib import messages
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
                   get_messages, give_money, verify_telegram_auth)

from .forms import CustomUserCreationForm, LoginUserForm
from .models import CustomUser

DOMEN = 'http://127.0.0.1:8000/'

def register(request):
    if request.method == 'POST':
        # ic(request)
        form = CustomUserCreationForm(request.POST)
        username = form.data['username']
        
        telegram_id = request.POST.get('telegram_id')
        ic(telegram_id)

        if not telegram_id:
            messages.error(request, 'Telegram authentication is required.')
            return render(request, 'registration/signup.html', {'form': form})

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'A user with that username already exists.')
            return render(request, 'registration/signup.html', {'form': form})
        # ic(form.is_valid())
        if form.is_valid():
            ic('valid')
            if CustomUser.objects.filter(telegram_id=telegram_id).exists():
                
                CustomUser.objects.update(telegram_id=telegram_id, username=username)
                messages.info(request, 'Синхронизация данных | У вас уже имеется аккаунт зарегистрированный на этот телеграм.\nСвязываем телеграм и сайт.')

            
            else:
                user = form.save(commit=False)
                user.telegram_id = int(telegram_id)
                ic(user)
                user.save()
                ic('save')
            
                # example = {"server_id": user.server_id,
                #            "maxQuantity": 30,
                #            "inventory": [{'type': 'empty'}] * 30
                # }
                # db_inv.insert(example)
            #log authorizacia
            ic('pred login')
            
            login(request, user)
            ic('login')
            return redirect('profile', server_id=user.server_id)
        else:
            ic(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})





@login_required(login_url="/users/login/")
def profile(request, server_id: int):
    # if request.user.server_id != server_id:
    #     return HttpResponseNotFound(render(request, '404.html'))

    url_get_profile = DOMEN + 'api/get_profile/'
    data = {"action": "get_profile", "server_id": server_id, "source": "web"}
    response = requests.post(url_get_profile, json=data).json()
    ic(response)
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
                    messages.error(request, "Invalid Telegram data.")
                    return render(request, 'registration/login.html', {'form': form})

            if user:
                login(request, user)
                return redirect(reverse('profile', kwargs={'server_id': user.server_id}))
            else:
                messages.error(request, "Invalid username or password.")
        else:
            ic(form.errors)
            messages.error(request, "Invalid username or password.")
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
    messages.success(request, "Вы вышли с аккаунта")
    return logout_then_login(request, login_url='/profile/')

@login_required(login_url="/users/login/")
def sell_transport(request: WSGIRequestHandler, type: str, ucode: str):
    
    if type not in ('car', 'yacht'):
        return JsonResponse({'success': False, 'error': 'Неверный тип транспорта'})
    
    
    user = request.user
    if not user:
        return JsonResponse({'success': False, 'error': 'Пользователь не найден'})
    
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

    give_money(request, request.user.server_id, transport_info['price'] // 2)
    
    if type == 'car':
        car = Car.objects.get(id=transport_info['id'])
        car.quantity += 1
        car.save()

    elif type == 'yacht':
        yacht = Yacht.objects.get(id=transport_info['id'])
        yacht.quantity += 1
        yacht.save()

    else: ic('ASHIBKA')

    messages.success(request, 'Транспорт успешно продан!')
    return JsonResponse({'success': True, 'message': 'Транспорт успешно продан!', 'messages': get_messages(request)})
     


    

    
def sell_house(request: WSGIRequestHandler, id: int):

    house_info = get_house_by_id(id)



    # result = coll.update_one({'server_id': request.user.server_id},
    #                          {'$pull': {'house.houses': {'id': house_info.id}}})
    #
    # ic(request.user.house)
    # if result.modified_count < 1:
    #     return JsonResponse({'success': False, 'error': 'Не удалось удалить дом'})

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
    messages.success(request, 'Продажа прошла успешно!')
    return JsonResponse({'success': True, 'message': 'Продажа прошла успешно!', 'messages': get_messages(request)})

def page_not_found(request, exception):
    ic(exception)
    return render(request, "404.html")

def basement(request, id_house: int):
    
    url_get_basement = DOMEN + 'api/get_basement/' + str(id_house) + '/'
    data = {"action": "get_basement", "server_id": request.user.server_id, "source": "web"}
    ic(url_get_basement)
    response: dict = requests.get(url_get_basement, json=data).json()

    income = 0
    current_videocards = len(response.get('videocards', []))
    ic(response)
    limit_videocards = response['house_info']['basement'].get('maxQuantity', 0)
    for k in response['videocards']:
        income += k['performance']
    
    
    response.update({'my_server_id': request.user.server_id, 'income': income,
                     'quantity_videocards': current_videocards, 'limit_videocards': limit_videocards,
                     'mix_videocards': response['mix_videocards']})
    # response.update()
    ic(response)
    
    # if not response['house_info']['basement']:
        
    
    if not response.get('videocards', {}):
        response['success'] = False 

    return render(request, 'basement.html', response)
