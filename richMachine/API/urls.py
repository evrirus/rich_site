from django.urls import path

from .views.api_house import GetMyHousesView, GetHouseView, GetBasementView, GetTakeProfitBasementView
from .views.api_transport import (CheckTransportInfo, GetMyCarsView,
                                  GetMyYachtsView, SellTransportToState)
from .views.api_users import (ChangeLanguageView, ChangeNicknameView,
                              GetBalance, ProfileView)
from .views.api_other import GetSymbolCrypt, GetInventory
from .views.api_casino import GenerateCombinationView

app_name = 'api'

urlpatterns = [
    path('change_nickname/', ChangeNicknameView.as_view(), name='change_nickname'),
    path('change_language/', ChangeLanguageView.as_view(), name='change_language'),
    path('get_profile/', ProfileView.as_view(), name='get_profile'),
    
    # Property views
    path('get_my_cars/', GetMyCarsView.as_view(), name='get_my_cars'),
    path('get_my_yachts/', GetMyYachtsView.as_view(), name='get_my_yachts'),
    path('get_my_houses/', GetMyHousesView.as_view(), name='get_my_houses'),
    path('get_house_profile/<int:id_house>/', GetHouseView.as_view(), name='get_house_profile'),
    path('get_basement/<int:id_house>/', GetBasementView.as_view(), name='get_basement'),
    path('take_profit_basement/', GetTakeProfitBasementView.as_view(), name='take_profit_basement'),
    
    # Banking
    path('get_balance/', GetBalance.as_view(), name='get_balance'),
    path('transport_info/', CheckTransportInfo.as_view(), name='transport_info'),
    path('sell_transport_to_state/', SellTransportToState.as_view(), name='sell_transport_to_state'),
    path('symbol_crypt/', GetSymbolCrypt.as_view(), name='get_symbol_crypt'),
    
    # Other
    path('get_inventory/', GetInventory.as_view(), name='get_inventory'),
    path('slot/generate/', GenerateCombinationView.as_view())
    
    # House functions
    # path('house/change_class/', ChangeClassHouse.as_view(), name='change_class')
]
