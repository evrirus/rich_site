# users/views.py

import json
from wsgiref.simple_server import WSGIRequestHandler

from django.conf import settings
# from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from icecream import ic
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.views import APIView


from authentication import SiteAuthentication, TelegramAuthentication
from inventory.models import Inventory
from magazine.models import Houses
from utils import (get_house_by_id,
                   verify_telegram_auth, DoRequest, send_message_to_user,
                   send_message_to_session, Money)
from .forms import CustomUserCreationForm, LoginUserForm  # , CustomPasswordChangeForm
from .models import CustomUser

DOMEN = 'http://127.0.0.1:8000/'

@method_decorator(csrf_exempt, name='dispatch')
class RegistrationView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = []

    def get(self, request: Request):
        return render(request, 'registration/signup.html')

    def post(self, request: Request):

        if not request.session.session_key:
            request.session.create()

        form = CustomUserCreationForm(request.POST)
        telegram_id = request.POST.get('telegram_id')
        session_key = request.session.session_key
        errors = []

        if not telegram_id or not telegram_id.isdigit():
            errors.append('Авторизация через Telegram обязательна.')

        if CustomUser.objects.filter(username=form.data['username']).exists():
            errors.append('Пользователь с таким именем уже существует.')

        if errors:
            ic(errors)
            return JsonResponse({'success': False, 'errors': errors})

        if form.is_valid():
            user = form.save(commit=False)
            user.telegram_id = int(telegram_id)
            user.save()

            Inventory.objects.create(user=user)
            send_message_to_session(session_key, {'text': 'Добро пожаловать! |'})

            login(request, user)
            return JsonResponse(
                {'success': True, 'redirect_url': reverse('profile', kwargs={'server_id': user.server_id})})

        else:
            ic(form.errors)
            for err in form.errors:
                for error in form.errors[err]:
                   errors.append(error)

                send_message_to_session(session_key, {'text': '\n'.join(errors)})
            return JsonResponse({'success': False, 'errors': '\n'.join(errors)})

        return JsonResponse({'success': True})





@login_required(login_url="/users/login/")
def profile(request, server_id: int):
    # if request.user.server_id != server_id:
    #     return HttpResponseNotFound(render(request, '404.html'))

    data = {"action": "get_profile", "server_id": server_id, "source": "web"}
    response = DoRequest('api/get_profile/', 'POST', data=data)
    ic(response)
    response['title'] = f'User profile ID: {response['server_id']}'
    
    return render(request, 'profile.html', response)


@login_required(login_url="/users/login/")
def self_profile(request: WSGIRequestHandler):
    return redirect(reverse('profile', kwargs={'server_id': request.user.server_id}))


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = []

    def get(self, request: Request):
        ic(request)
        return render(request, 'registration/login.html')

    def post(self, request: Request):
        if not request.session.session_key:
            request.session.create()

        form = LoginUserForm(request, data=request.POST)
        session_key = request.session.session_key
        errors = []

        if request.POST.get('telegram_auth_data'):
            telegram_auth_data = json.loads(request.POST.get('telegram_auth_data'))

            if not CustomUser.objects.filter(telegram_id=telegram_auth_data['id']).exists():
                errors.append('Вы ещё не зарегистрированы.')
        else:
            telegram_auth_data = None

        if errors:
            ic(errors)
            return JsonResponse({'success': False, 'errors': errors})
        ic(form)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = None

            if username and password:
                user = authenticate(request, username=username, password=password)

            elif telegram_auth_data:
                try:

                    if verify_telegram_auth(telegram_auth_data, settings.TELEGRAM_BOT_TOKEN):

                        telegram_id = telegram_auth_data.get('id')
                        user = authenticate(request, telegram_id=telegram_id)

                except (json.JSONDecodeError, KeyError):

                    send_message_to_session(session_key, {'text': 'Invalid Telegram data.'})
                    # messages.error(request, "Invalid Telegram data.")
                    return JsonResponse({'success': False, 'errors': 'Invalid Telegram data.'})

            if user:
                login(request, user)
                send_message_to_session(session_key, {'text': f'Вы успешно авторизовались как {user.get_username()}'})
                return JsonResponse({'success': True})
            else:
                send_message_to_session(session_key, {'text': 'Invalid username or password.'})

            return JsonResponse({'success': True})
                # messages.error(request, "Invalid username or password.")
        else:

            for err in form.errors:
                for error in form.errors[err]:
                    errors.append(error)

                send_message_to_session(session_key, {'text': '\n'.join(errors)})
            return JsonResponse({'success': False, 'errors': '\n'.join(errors)})
        return JsonResponse({'success': True})



# class SignUpView(CreateView):
#     form_class = CustomUserCreationForm
#     success_url = reverse_lazy('home')
#     template_name = 'registration/signup.html'
    
    
# class LoginView(CreateView):
#     form_class = LoginUserForm
#     success_url = reverse_lazy("login")
#     template_name = "registration/login.html"

def loguot_user(request):
    send_message_to_user(request.user.server_id, {'text': 'Вы вышли с аккаунта'})
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

        money = Money(request, house_info.price // 2).give()
        money.create_notification('Продажа прошла успешно!')

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
