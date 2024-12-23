from django.shortcuts import render
from icecream import ic
from django.core.handlers.wsgi import WSGIRequest


# Create your views here.
def index(request: WSGIRequest):

    data = {
        'title': "Rich Machine",
        'username': request.user.username,
        "my_server_id": request.user.server_id if not request.user.is_anonymous else False
    }
    return render(request, 'homePage/index.html', data)
