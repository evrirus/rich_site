# users/forms.py

from django import forms
from django.contrib.auth.forms import (AuthenticationForm, UserChangeForm,
                                       UserCreationForm, UsernameField)

from .models import CustomUser


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
    telegram_id = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())
    
    class Meta:
        fields = ['username', 'password', 'telegram_id']
