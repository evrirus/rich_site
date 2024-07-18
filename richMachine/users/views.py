# users/views.py

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from icecream import ic
from utils import coll, get_district_by_id, get_house_by_id

from .forms import CustomUserCreationForm, LoginUserForm
from .models import CustomUser

# def signup_user(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             # После успешной регистрации пользователя можно выполнить дополнительные действия, например, войти в систему или отправить на другую страницу
#             return redirect('users:login')  # Перенаправляем на страницу входа после успешной регистрации
#     else:
#         form = UserCreationForm()

#     return render(request, 'users/signup.html', {'form': form})

# # users/views.py



# class CustomBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         # Получить пользователя из вашей собственной базы данных
#         try:
#             user = CustomUser.objects.get(username=username)
#             ic(user)
#         except CustomUser.DoesNotExist:
#             return None
        
#         # Проверить пароль
#         if user.check_password(password):
#             return user

#         return None

# def login_user(request):
#     if request.method == 'POST':
#         ic(request.POST.username)
#         form = LoginUserForm(request.POST)
#         ic(form.is_valid())
#         ic(form.data)
#         ic(form.username)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']

#             # Использовать переопределенный метод authenticate()
#             user = CustomBackend().authenticate(request, username=username, password=password)

#             if user:
#                 # Проверить, является ли пользователь новым пользователем
#                 if user.is_new_user:
#                     # Вывести имя пользователя в консоли
#                     ic(user.username)

#                 login(request, user)
#                 return redirect('homePage:profile')  # Замените 'home' на ваше имя представления или URL для профиля
#             else:
#                 form.add_error(None, "Неверные учетные данные")
#     else:
#         form = LoginUserForm()

#     return render(request, 'users/login.html', {'form': form})

def register(request):
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
def profile(request, server_id):
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
    
    return render(request, 'homePage/profile.html', data)

def login_user(request):
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
def change_nickname(request):
    if request.method == 'POST':
        new_nickname = request.POST.get('new_nickname')
        if new_nickname:
            user = request.user
            user.nickname['name'] = new_nickname
            user.save()
            messages.success(request, 'Profile updated successfully')
            return JsonResponse({'success': True, 'new_nickname': new_nickname})
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})