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

# from .models import UserToken

coefficients = {
        1: ['🍭', '🍭', '🍭'],
        2: ['🍭', '🍭', '🦄'],
        3: ['🍭', '🍭', '💵'],
        4: ['🍭', '🍭', '🦖'],
        5: ['🍭', '🍭', '👻'],
        6: ['🍭', '🦄', '🍭'],
        7: ['🍭', '🦄', '🦄'],
        8: ['🍭', '🦄', '💵'],
        9: ['🍭', '🦄', '🦖'],
        10: ['🍭', '🦄', '👻'],
        11: ['🍭', '💵', '🍭'],
        12: ['🍭', '💵', '🦄'],
        13: ['🍭', '💵', '💵'],
        14: ['🍭', '💵', '🦖'],
        15: ['🍭', '💵', '👻'],
        16: ['🍭', '🦖', '🍭'],
        17: ['🍭', '🦖', '🦄'],
        18: ['🍭', '🦖', '💵'],
        19: ['🍭', '🦖', '🦖'],
        20: ['🍭', '🦖', '👻'],
        21: ['🍭', '👻', '🍭'],
        22: ['🍭', '👻', '🦄'],
        23: ['🍭', '👻', '💵'],
        24: ['🍭', '👻', '🦖'],
        25: ['🍭', '👻', '👻'],
        26: ['🦄', '🍭', '🍭'],
        27: ['🦄', '🍭', '🦄'],
        28: ['🦄', '🍭', '💵'],
        29: ['🦄', '🍭', '🦖'],
        30: ['🦄', '🍭', '👻'],
        31: ['🦄', '🦄', '🍭'],
        32: ['🦄', '🦄', '🦄'],
        33: ['🦄', '🦄', '💵'],
        34: ['🦄', '🦄', '🦖'],
        35: ['🦄', '🦄', '👻'],
        36: ['🦄', '💵', '🍭'],
        37: ['🦄', '💵', '🦄'],
        38: ['🦄', '💵', '💵'],
        39: ['🦄', '💵', '🦖'],
        40: ['🦄', '💵', '👻'],
        41: ['🦄', '🦖', '🍭'],
        42: ['🦄', '🦖', '🦄'],
        43: ['🦄', '🦖', '💵'],
        44: ['🦄', '🦖', '🦖'],
        45: ['🦄', '🦖', '👻'],
        46: ['🦄', '👻', '🍭'],
        47: ['🦄', '👻', '🦄'],
        48: ['🦄', '👻', '💵'],
        49: ['🦄', '👻', '🦖'],
        50: ['🦄', '👻', '👻'],
        51: ['💵', '🍭', '🍭'],
        52: ['💵', '🍭', '🦄'],
        53: ['💵', '🍭', '💵'],
        54: ['💵', '🍭', '🦖'],
        55: ['💵', '🍭', '👻'],
        56: ['💵', '🦄', '🍭'],
        57: ['💵', '🦄', '🦄'],
        58: ['💵', '🦄', '💵'],
        59: ['💵', '🦄', '🦖'],
        60: ['💵', '🦄', '👻'],
        61: ['💵', '💵', '🍭'],
        62: ['💵', '💵', '🦄'],
        63: ['💵', '💵', '💵'],
        64: ['💵', '💵', '🦖'],
        65: ['💵', '💵', '👻'],
        66: ['💵', '🦖', '🍭'],
        67: ['💵', '🦖', '🦄'],
        68: ['💵', '🦖', '💵'],
        69: ['💵', '🦖', '🦖'],
        70: ['💵', '🦖', '👻'],
        71: ['💵', '👻', '🍭'],
        72: ['💵', '👻', '🦄'],
        73: ['💵', '👻', '💵'],
        74: ['💵', '👻', '🦖'],
        75: ['💵', '👻', '👻'],
        76: ['🦖', '🍭', '🍭'],
        77: ['🦖', '🍭', '🦄'],
        78: ['🦖', '🍭', '💵'],
        79: ['🦖', '🍭', '🦖'],
        80: ['🦖', '🍭', '👻'],
        81: ['🦖', '🦄', '🍭'],
        82: ['🦖', '🦄', '🦄'],
        83: ['🦖', '🦄', '💵'],
        84: ['🦖', '🦄', '🦖'],
        85: ['🦖', '🦄', '👻'],
        86: ['🦖', '💵', '🍭'],
        87: ['🦖', '💵', '🦄'],
        88: ['🦖', '💵', '💵'],
        89: ['🦖', '💵', '🦖'],
        90: ['🦖', '💵', '👻'],
        91: ['🦖', '🦖', '🍭'],
        92: ['🦖', '🦖', '🦄'],
        93: ['🦖', '🦖', '💵'],
        94: ['🦖', '🦖', '🦖'],
        95: ['🦖', '🦖', '👻'],
        96: ['🦖', '👻', '🍭'],
        97: ['🦖', '👻', '🦄'],
        98: ['🦖', '👻', '💵'],
        99: ['🦖', '👻', '🦖'],
        100: ['🦖', '👻', '👻'],
        101: ['👻', '🍭', '🍭'],
        102: ['👻', '🍭', '🦄'],
        103: ['👻', '🍭', '💵'],
        104: ['👻', '🍭', '🦖'],
        105: ['👻', '🍭', '👻'],
        106: ['👻', '🦄', '🍭'],
        107: ['👻', '🦄', '🦄'],
        108: ['👻', '🦄', '💵'],
        109: ['👻', '🦄', '🦖'],
        110: ['👻', '🦄', '👻'],
        111: ['👻', '💵', '🍭'],
        112: ['👻', '💵', '🦄'],
        113: ['👻', '💵', '💵'],
        114: ['👻', '💵', '🦖'],
        115: ['👻', '💵', '👻'],
        116: ['👻', '🦖', '🍭'],
        117: ['👻', '🦖', '🦄'],
        118: ['👻', '🦖', '💵'],
        119: ['👻', '🦖', '🦖'],
        120: ['👻', '🦖', '👻'],
        121: ['👻', '👻', '🍭'],
        122: ['👻', '👻', '🦄'],
        123: ['👻', '👻', '💵'],
        124: ['👻', '👻', '🦖'],
        125: ['👻', '👻', '👻'],
    }





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

