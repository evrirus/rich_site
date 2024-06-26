from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('login/', views.login_user, name='login'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
]