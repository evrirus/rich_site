# users/forms.py

from django import forms
from django.contrib.auth.forms import (AuthenticationForm, UserChangeForm,
                                       UserCreationForm, UsernameField)

from .models import CustomUser


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")

# users/forms.py


# forms.py



class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        # Удаляем лишние сообщения о пароле
        # self.fields['password1'].help_text = ''
        # self.fields['password2'].help_text = ''
        # self.fields['username'].help_text = ''
        
        # self.fields['username'].widget.attrs.update({'placeholder': 'Логин'})
        # self.fields['password1'].widget.attrs.update({'placeholder': 'Пароль'})
        # self.fields['password2'].widget.attrs.update({'placeholder': 'Подтвердите пароль'})
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')




class LoginUserForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True, "placeholder": "Логин"}))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "Пароль"}),
    )
