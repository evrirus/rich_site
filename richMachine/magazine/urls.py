from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'magazine'


urlpatterns = [
    path('', views.magazin, name='get_proptery'),
    path('cars', views.get_cars, name='get_cars'),
    # path('cars/<int:car_id>', views.render_free_cars, name='get_car_by_id'),
    path('yachts', views.get_yachts, name='get_yachts'),
    path('districts', views.get_districts, name='get_districts'),
    path('districts/<int:district_id>', views.get_houses, name='get_district'),
    path('get_transport_info/<str:type>/<int:id>/', views.get_transport_info, name='get_transport_info'),
    path('buy_transport/<str:type>/<int:id>/', views.buy_transport, name='buy_transport'),
    path('get_house_info/<int:id>/', views.get_house_info, name='get_house_info'),
    path('buy_house/<int:id>/', views.buy_house, name='buy_house'),
]