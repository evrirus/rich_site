# users/forms.py
import json

from django import forms
from django.contrib.auth.forms import (AuthenticationForm, UserChangeForm,
                                       UserCreationForm, UsernameField)
from django.contrib.auth import authenticate
from icecream import ic

from .models import CustomUser

from django import forms
from django.contrib.auth.forms import PasswordChangeForm


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", 'telegram_id')


class CustomUserCreationForm(UserCreationForm):
    telegram_id = forms.CharField(max_length=100, required=True, widget=forms.HiddenInput())

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'telegram_id']


class LoginUserForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True, "placeholder": "Логин"}), required=False)
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "Пароль"}),
        required=False
    )
    telegram_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    error_messages = {
        'invalid_login': "Неверное имя пользователя или пароль. Проверьте правильность ввода.",
        'inactive': "Этот аккаунт был деактивирован.",
    }
    
    class Meta:
        fields = ['username', 'password', 'telegram_id']

    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if self.data.get('telegram_auth_data', ):
            telegram_id = json.loads(self.data['telegram_auth_data']).get('id')
        else:
            telegram_id = 0

        ic(telegram_id)
        if not telegram_id:
            if not username:
                self.add_error('username', "Введите имя пользователя.")
            if not password:
                self.add_error('password', "Введите пароль.")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:

                raise forms.ValidationError(
                    "Неверное имя пользователя или пароль."
                )

        if telegram_id:
            if not CustomUser.objects.filter(telegram_id=telegram_id).exists():
                self.add_error('telegram_id', "Telegram ID не найден.")

        return cleaned_data



# class CustomPasswordChangeForm(PasswordChangeForm):
#     old_password = forms.CharField(
#         widget=forms.PasswordInput(attrs={'placeholder': 'Старый пароль'}),
#         label='Старый пароль'
#     )
#     new_password1 = forms.CharField(
#         widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'}),
#         label='Новый пароль'
#     )
#     new_password2 = forms.CharField(
#         widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите новый пароль'}),
#         label='Подтверждение пароля'
#     )

