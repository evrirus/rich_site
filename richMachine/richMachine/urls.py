"""
URL configuration for richMachine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from users.views import profile, self_profile
# from other_functions.views import inventory, casino
from users.views import RenderBasementView
from casino import views as CasinoViews
from inventory import views as InventoryViews



app_name = 'richMachine'

urlpatterns = [
    path('api/', include('API.urls', namespace='api')), 
    
    path('admin/', admin.site.urls, name='admin'),
    path('', include('homePage.urls', namespace='homePage')),
    path('users/', include('users.urls', namespace='users'), name='users'),
    path('magazine/', include('magazine.urls', namespace='magazine'), name='magazine'),
    path('profile/', self_profile, name='self_profile'),
    path('profile/<int:server_id>', profile, name='profile'),
    path('inventory/', InventoryViews.RenderInventory.as_view(), name='inventory'),
    
    path('basement/<int:id_house>/', RenderBasementView.as_view(), name='basement'),
    
    path('casino/', CasinoViews.MainCasinoView.as_view(), name='casino'),
    path('casino/slot/', CasinoViews.SlotMachineView.as_view(), name='slot_machine'),

    path('jobs/', include('jobs.urls', namespace='jobs'), name='jobs'),
    # path('casino/slot/generate_combination/', casino.GenerateCombinationView.as_view(), name='generate_combination'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
