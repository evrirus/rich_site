from django.http import HttpResponse
from django.shortcuts import render
from icecream import ic
from django.core.handlers.wsgi import WSGIRequest

from .forms import LoginUserForm

# Create your views here.

def login_user(request):
    form = LoginUserForm()
    return render(request, 'users/login.html', {'form': form})

def logout_user(request):
    return HttpResponse("logout")

def set_session(request: WSGIRequest):
    request.session['username'] = 'evrirus'
    ic(request.user)
    return HttpResponse("Session is set")

def get_session(request: WSGIRequest):
    username = request.session.get('username', 'Guest')
    return HttpResponse(f"Hello {username}")