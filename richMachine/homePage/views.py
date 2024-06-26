from django.shortcuts import render
from utils import coll, get_district_by_id, get_house_by_id
from icecream import ic
from django.core.handlers.wsgi import WSGIRequest


# Create your views here.
def index(request: WSGIRequest):
    
    data = {
        'title': "Rich Machine",
        'username': request.user.username
    }
    return render(request, 'homePage/index.html', data)
