import json
import random


from wsgiref.simple_server import WSGIRequestHandler

from rest_framework.views import APIView

from authentication import SiteAuthentication, TelegramAuthentication
from rest_framework.authentication import SessionAuthentication

from django.contrib import messages

from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse
from django.shortcuts import  render

from django.views import View
from django.views.decorators.csrf import csrf_exempt

from icecream import ic

import requests
from utils import (DOMEN,get_item_by_id,get_messages, give_money,  get_symbol_money)


class MainCasinoView(APIView):
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]

    @staticmethod
    def get(request):
        return render(request, 'other_functions/casino_main.html', {'my_server_id': request.user.server_id})


class SlotMachineView(APIView):
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]

    @staticmethod
    def get(request):
        return render(request, 'other_functions/casino_slot.html', {'my_server_id': request.user.server_id})

