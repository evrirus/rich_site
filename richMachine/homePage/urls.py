from django.urls import path
from . import views

app_name = 'homePage'

urlpatterns = [
    path('', views.index),
    path('profile/', views.profile, name='profile'),
]