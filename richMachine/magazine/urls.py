from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'magazine'


urlpatterns = [
    path('', views.MagazineView.as_view(), name='get_proptery'),
    path('car', views.get_cars, name='get_cars'),
    path('yacht', views.get_yachts, name='get_yachts'),
    path('district', views.get_districts, name='get_districts'),
    path('district/<int:district_id>', views.get_houses, name='get_district'),
    path('videocard', views.get_videocards, name='get_videocards'),
    # path('get_videocard_info/<int:videocard_id>/', views.get_videocard_info, name='get_videocard_info'),
    # path('buy_videocard/<int:videocard_id>/', views.buy_videocard, name='buy_videocard'),
    # path('get_transport_info/<str:type>/<int:id>/', views.get_transport_info, name='get_transport_info'),
    # path('buy_transport/<str:type>/<int:id>/', views.buy_transport, name='buy_transport'),
    # path('get_house_info/<int:house_id>/', views.get_house_info, name='get_house_info'),
    # path('buy_house/<int:id>/', views.buy_house, name='buy_house'),
]