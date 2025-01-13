from django.contrib.humanize.templatetags.humanize import intcomma
from django.shortcuts import render
from icecream import ic
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView

from authentication import SiteAuthentication, TelegramAuthentication
from casino.models import CasinoModel


class MainCasinoView(APIView):
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]

    @staticmethod
    def get(request):
        return render(request, 'casino/casino_main.html', {'my_server_id': request.user.server_id})


class SlotMachineView(APIView):
    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]

    @staticmethod
    def get(request):
        casino_model = CasinoModel.objects.get(user=request.user)
        # if not casino_model:
        #     return


        balance = {}

        currency = {'bitcoin': {'translate': 'Биткоин', 'symbol': '₿'},
                    'cash': {'translate': 'Рубли', 'symbol': '₽'},
                    'dollar': {'translate': 'Доллары', 'symbol': '$'}}

        usable_currency = currency.copy()



        for x in request.user.money.items():
            if x[0] == 'bank':
                continue

            if x[0] in currency.keys():
                usable_currency[x[0]]['amount'] = intcomma(x[1])
            else:
                usable_currency[x[0]]['amount'] = intcomma(x[1])
                usable_currency[x[0]]['translate'] = False
                usable_currency[x[0]]['symbol'] = '(?)'

        ic(usable_currency)
            # balance[x[0]] = intcomma(x[1]) + ' ' +(f'{currency_symbols[x[0]]}' if currency_symbols.get(x[0]) else '(?)')

        ic(balance)

        return render(request, 'casino/casino_slot.html',
                      {'my_server_id': request.user.server_id,
                       # 'is_authenticated': casino_model.is_authenticated,
                       'freespins': casino_model.freespins_available,
                       'balance': usable_currency,
                       })
