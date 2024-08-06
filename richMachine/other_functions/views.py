import json
from wsgiref.simple_server import WSGIRequestHandler

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from icecream import ic
from pymongo.errors import ConnectionFailure, OperationFailure
from utils import (client, coll, db_cars, db_houses, db_yachts,
                   get_district_by_id, get_house_by_id, get_messages,
                   give_money, verify_telegram_auth)

# Create your views here.
def inventory(request: WSGIRequestHandler):
    ic('inventory!!')
    
    return render(request, 'other_functions/inventory.html', {'my_server_id': request.user.server_id})