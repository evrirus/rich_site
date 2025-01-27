from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views.api_casino import GenerateCombinationView
from .views.api_house import (BuyHouseView, CreateBasementView,
                              GetBalanceBasementView, GetBasementView,
                              GetHouseView, GetMyHousesView,
                              GetTakeProfitBasementView, SellHouseView,
                              UpgradeBasementView)
from .views.api_jobs import WorkAPI
from .views.api_items import GetItem, BuyItem
from .views.api_other import GetInventory, GetSymbolCrypt
from .views.api_transport import (BuyTransportView, CheckTransportInfo,
                                  GetMyCarsView, GetMyYachtsView,
                                  SellTransportToState, SellTransportToPlayer)
from .views.api_users import (ChangeLanguageView, ChangeNicknameView,
                              GetBalance, ProfileView)

from .views.api_login import LoginView, LogoutUserView, loguot_user
from .views.api_register import RegistrationView

app_name = 'api'

urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    path('change_nickname/', ChangeNicknameView.as_view(), name='change_nickname'),
    path('change_language/', ChangeLanguageView.as_view(), name='change_language'),
    path('get_profile/', ProfileView.as_view(), name='get_profile'),
    
    # Property views
    path('get_my_cars/', GetMyCarsView.as_view(), name='get_my_cars'),
    path('get_my_yachts/', GetMyYachtsView.as_view(), name='get_my_yachts'),
    path('get_my_houses/', GetMyHousesView.as_view(), name='get_my_houses'),
    path('get_house/<int:id_house>/', GetHouseView.as_view(), name='get_house'),
    path('get_basement/<int:id_house>/', GetBasementView.as_view(), name='get_basement'),
    path('take_profit_basement/', GetTakeProfitBasementView.as_view(), name='take_profit_basement'),
    path('sell_house/<int:id>/', SellHouseView.as_view(), name='sell_house'),
    path('create_basement/', CreateBasementView.as_view(), name='create_basement'),
    path('upgrade_basement/<int:id_house>/', UpgradeBasementView.as_view(), name='upgrade_basement'),
    path('get_balance_basement/<int:id_house>/', GetBalanceBasementView.as_view(), name='get_balance_basement'),
    path('sell_transport_to_player/', SellTransportToPlayer.as_view(), name='sell_transport_to_player'),
    
    path('buy_transport/', BuyTransportView.as_view(), name='buy_transport'),
    path('buy_house/', BuyHouseView.as_view(), name='buy_house'),
    path('buy_item/', BuyItem.as_view(), name='buy_item'),
    
    # Banking
    path('get_balance/', GetBalance.as_view(), name='get_balance'),
    path('transport_info/', CheckTransportInfo.as_view(), name='transport_info'),
    path('sell_transport_to_state/<str:type>/<str:ucode>/', SellTransportToState.as_view(), name='sell_transport_to_state'),
    path('symbol_crypt/', GetSymbolCrypt.as_view(), name='get_symbol_crypt'),
    
    # Other
    path('get_inventory/', GetInventory.as_view(), name='get_inventory'),
    path('slot/generate/', GenerateCombinationView.as_view()),
    path('item/', GetItem.as_view(), name='get_item'),

    # Jobs
    path('update_clicks/', WorkAPI.as_view(), name='upd_clicks'),


    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', loguot_user, name='logout'),
    # House functions
    # path('house/change_class/', ChangeClassHouse.as_view(), name='change_class')
]
