from django.urls import path
from . import views

app_name = 'homePage'

urlpatterns = [
    path('', views.index, name='home'),
    # path('profile/<str:username>/', views.profile, name='profile'),
]