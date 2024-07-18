from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'users'


urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/<int:server_id>/', views.profile, name='profile'),
    path('change-nickname/', views.change_nickname, name='change_nickname'),
    path('login/', views.login_user, name='login'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
]