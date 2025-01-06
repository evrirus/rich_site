from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'jobs'

urlpatterns = [
    # path('', views.magazin, name='get_proptery'),
    path('work/', views.WorkView.as_view(), name='work'),

]