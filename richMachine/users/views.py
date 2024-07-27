# users/views.py

from wsgiref.simple_server import WSGIRequestHandler

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from icecream import ic
from utils import (coll, db_cars, db_yachts, get_district_by_id,
                   get_house_by_id, give_money, db_houses)

from .forms import CustomUserCreationForm, LoginUserForm
from .models import CustomUser


def register(request: WSGIRequestHandler):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        username = form.data['username']

        if coll.find_one({'username': username}):
            messages.error(request, 'A user with that username or email already exists.')
            return render(request, 'registration/signup.html', {'form': form})
        if form.is_valid():
            

            user = form.save()
            login(request, user)
            return redirect('users:profile', server_id=user.server_id)
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required(login_url="/users/login/")
def profile(request: WSGIRequestHandler, server_id: int):
    user = coll.find_one({'server_id': server_id})
    
    if not user:
        return HttpResponseNotFound(render(request, '404.html'))
    
    houses_id = user['house']['houses']
    houses = []
    for x in houses_id:
        house_info = get_house_by_id(x['id'])
        district_info = get_district_by_id(house_info['district_id'])
        house_info['district_info'] = district_info
        houses.append(house_info)
    
    data = {
        "nickname": user.get('nickname'),
        "money": user.get('money'),
        "donate_balance": user.get('donate_balance'),
        "job": user.get('job', {}).get('title') if user.get('job', {}).get('title') else 'Безработный',
        "car": user.get('car'),
        "yacht": user.get('yacht'),
        "houses": houses,
        "couple": user.get('couple'),
        "registration": user.get('registration'),
        "language": user.get('language'),
        "username": user.get('username'),
        "my_username": request.user.username,
        "server_id": user.get('server_id'),
        "my_server_id": request.user.server_id,
        "is_authenticated": user.get('is_authenticated'),
    }
    
    return render(request, 'profile.html', data)


def login_user(request: WSGIRequestHandler):
    if request.method == 'POST':
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('users:profile', kwargs={'server_id': user.server_id}))
            else:
                messages.error(request, "Invalid username or password.")
        else:
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


@login_required(login_url="/users/login/")
def change_nickname(request: WSGIRequestHandler):
    ic(request.method)
    if request.method == 'POST':
        new_nickname = request.POST.get('new_nickname')
        if not new_nickname:
            return JsonResponse({'success': False, 'error': 'Invalid new nickname'})
        if len(new_nickname) <= 3:
            return JsonResponse({'success': False, 'error': 'Название никнейма слишком короткое'})
        
        user_info = coll.find_one({'server_id': request.user.server_id})
        
        if len(new_nickname) > user_info['nickname']['max']:
            return JsonResponse({'success': False, 'error': 'Название никнейма слишком длинное'})
        
        coll.update_one({'server_id': request.user.server_id},
                        {'$set': {'nickname.name': new_nickname}})

        messages.success(request, 'Profile updated successfully')
            
        return JsonResponse({'success': True, 'new_nickname': new_nickname})
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})

@login_required(login_url="/users/login/")
def change_language(request: WSGIRequestHandler):
    languages = ['ru', 'en']
    language = request.user.language
    index = languages.index(language)
    
    new_language_index = index + 1 if len(languages) - 1 >= index + 1 else 0

    coll.update_one({'server_id': request.user.server_id},
                    {'$set': {'language': languages[new_language_index]}})
    ic(languages[new_language_index])
    return JsonResponse({'success': True, 'new_language': languages[new_language_index]})

@login_required(login_url="/users/login/")
def sell_transport(request: WSGIRequestHandler, type: str, id: int, numerical_order: int):
    
    if type not in ('car', 'yacht'):
        return JsonResponse({'success': False, 'error': 'Неверный тип транспорта'})
    
    user_info = coll.find_one({'server_id': request.user.server_id})
    if not user_info:
        return JsonResponse({'success': False, 'error': 'Пользователь не найден'})
    
    transport_info = user_info[f'{type}'][f'{type}s'][numerical_order-1]
    if not transport_info:
        return JsonResponse({'success': False, 'error': 'Транспорт не найден'})
    
    items = user_info.get(f'{type}', {}).get(f'{type}s', [])
    items.pop(numerical_order-1)
    
    coll.update_one(
        {'server_id': request.user.server_id},
        {'$set': {f'{type}.{type}s': items}}
    )
    give_money(request.user.server_id, transport_info['price'] // 2)
    
    return JsonResponse({'success': True, 'message': 'Транспорт успешно продан!'})

@login_required(login_url="/users/login/")
def get_transport_profile(request: WSGIRequestHandler, type: str, id: int, numerical_order: int):
    
    if type not in ('car', 'yacht'):
        return JsonResponse({'success': False, 'error': 'Неверный тип транспорта'})
    
    user_info = coll.find_one({'server_id': request.user.server_id})
    if not user_info:
        return JsonResponse({'success': False, 'error': 'Пользователь не найден'})
    
    transport_info = user_info[f'{type}'][f'{type}s'][numerical_order-1]
    if not transport_info:
        return JsonResponse({'success': False, 'error': 'Транспорт не найден'})
    
    if type == 'car':
        global_trasport_info = db_cars.find_one({'id': transport_info['id']})
    else: 
        global_trasport_info = db_yachts.find_one({'id': transport_info['id']})
    
    ic(transport_info)
    
    return JsonResponse({
        'success': True,
        'type': type,
        'id': transport_info['id'],
        'numerical_order': numerical_order,
        'maxQuantity': global_trasport_info['maxQuantity'],
        'quantity': global_trasport_info['quantity'],
        'price': intcomma(transport_info['price']),
        'name': transport_info['name'],
        'plate': transport_info['plate'] if transport_info['plate'] else 'Отсутствуют',
    })
    
    
def get_house_profile(request: WSGIRequestHandler, id: int):
    ic(id)
    house_info = get_house_by_id(id)
    district_info = get_district_by_id(house_info['district_id'])

    house_info['district_info'] = district_info
    house_info['basement'] = f"Имеется[<span style='color: rgb(255, 28, 28);'>lvl</span>={house_info['basement']['level']}]" if house_info['basement'] else "Отсутствует"
    house_info['price'] = intcomma(house_info['price'])
    house_info['type'] = 'Дом' if house_info['type'] == 'house' else 'Квартира'
    return JsonResponse({'success': True, 'message': 'ok',
                         **house_info})
    
def sell_house(request: WSGIRequestHandler, id: int):
    house_info = get_house_by_id(id)
    
    result = coll.update_one({'server_id': request.user.server_id},
                    {'$pull': {'house.houses': {'id': house_info['id']}}})
    
    if result.modified_count < 1:
        return JsonResponse({'success': False, 'error': 'Не удалось удалить дом'})
    
    db_houses.update_one({'id': house_info['id']},
                         {'$set': {'owner': None}})
    give_money(request.user.server_id, house_info['price'] // 2)
    
    return JsonResponse({'success': True, 'message': 'Продажа прошла успешно!'})


def accept(request: WSGIRequestHandler):
    ic('telegraaaaaam')
    return JsonResponse({'ok': True})
    
    # return JsonResponse({'address': request.client_address})