# users/urls.py

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup_user, name='signup'),
    # path('profile/', views.profile, name='profile'), 
]
