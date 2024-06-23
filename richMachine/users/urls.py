from django.urls import path, include
from . import views

app_name = "users"

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('set_session/', views.set_session, name='set_session'),
    path('get_session/', views.get_session, name='get_session'),
]