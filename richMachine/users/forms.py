# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm

# Или использовать django.contrib.auth.models.User


# users/forms.py

from django import forms


class LoginUserForm(forms.Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
