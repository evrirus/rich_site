# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser  # Или использовать django.contrib.auth.models.User



class SignUpForm(UserCreationForm):
    # Добавьте здесь любые дополнительные поля формы, если нужно
    # Например:
    # email = forms.EmailField()

    class Meta:
        model = CustomUser  # Или django.contrib.auth.models.User
        fields = ('username', 'password1', 'password2')  # Поля, которые нужно заполнить при регистрации


# users/forms.py

from django import forms


class LoginUserForm(forms.Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
