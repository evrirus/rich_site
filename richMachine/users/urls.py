from django.conf.urls import handler400, handler403, handler404, handler500
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'users'

# handler400 = 'users.views.bad_request'
# handler403 = 'users.views.permission_denied'
handler404 = 'users.views.page_not_found'
# handler500 = 'users.views.server_error'

urlpatterns = [
    path('register/', views.register, name='register'),
    # path('profile/<int:server_id>/', views.profile, name='profile'),
    # path('profile/', views.self_profile, name='self_profile'),
    # path('change_nickname/', views.change_nickname, name='change_nickname'),
    # path('change_language/', views.change_language, name='language'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.loguot_user, name='logout'),
    # path('sell_transport/<str:type>/<str:ucode>/', views.sell_transport, name='sell_transport'),
    # path('get_transport_profile/<str:type>/<str:ucode>/', views.get_transport_profile, name='get_transport_profile'),
    # path('get_house_profile/<int:id>/', views.get_house_profile, name='get_house_profile'),
    # path('sell_house/<int:id>/', views.sell_house, name='sell_house'),

    # path('telegram/', views.accept, name='accept'),
]
