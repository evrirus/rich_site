# users/views.py

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from .forms import LoginUserForm  # Подключаем форму входа


def signup_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # После успешной регистрации пользователя можно выполнить дополнительные действия, например, войти в систему или отправить на другую страницу
            return redirect('users:login')  # Перенаправляем на страницу входа после успешной регистрации
    else:
        form = UserCreationForm()

    return render(request, 'users/signup.html', {'form': form})

# users/views.py


def login_user(request):
    if request.method == 'POST':
        form = LoginUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homePage:profile')  # Замените 'home' на ваше имя представления или URL для профиля
            else:
                form.add_error(None, "Неверные учетные данные")
    else:
        form = LoginUserForm()

    return render(request, 'users/login.html', {'form': form})
