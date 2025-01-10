from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView

from authentication import SiteAuthentication, TelegramAuthentication


class MainCasinoView(APIView):
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]

    @staticmethod
    def get(request):
        return render(request, 'casino/casino_main.html', {'my_server_id': request.user.server_id})


class SlotMachineView(APIView):
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]

    @staticmethod
    def get(request):
        return render(request, 'casino/casino_slot.html', {'my_server_id': request.user.server_id})
