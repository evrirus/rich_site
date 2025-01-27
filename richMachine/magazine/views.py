from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse
from django.shortcuts import render

from rest_framework.request import Request


from utils import get_district_by_id, get_house_by_id
from .models import Car, Yacht, Districts, Houses, Items
from django.http import HttpRequest, HttpResponse
from django.views import View
from django.core.handlers.asgi import ASGIRequest


# Create your views here.

class MagazineView(View):
    login_url = "/users/login/"
    
    def read_svg(self, file_path: str) -> str:
        """Helper function to read SVG files."""
        with open(file_path, 'r') as file:
            return file.read()

    def get(self, request: ASGIRequest) -> HttpResponse:
        """Handle GET requests to the magazin view."""
        
        file_paths = {
            "cars": 'magazine/static/magazine/img/transport.svg',
            "districts": 'magazine/static/magazine/img/district.svg',
            "videocards": 'magazine/static/magazine/img/videocard.svg',
            "yachts": 'magazine/static/magazine/img/yacht.svg'
        }

        # Read all SVG files
        svg_icons = {key: self.read_svg(path) for key, path in file_paths.items()}

        data = {
            "items": [
                {"code": "car", "title": "Автомобили", "svg": svg_icons["cars"]},
                {"code": "district", "title": "Районы", "svg": svg_icons["districts"]},
                {"code": "videocard", "title": "Видеокарты", "svg": svg_icons["videocards"]},
                {"code": "yacht", "title": "Яхты", "svg": svg_icons["yachts"]},
            ],
            'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
            'title': 'Magazine'
        }

        return render(request, 'magazine/magazine.html', data)




@login_required(login_url="/users/login")
def get_house_info(request: Request, house_id: int):
    house_info = get_house_by_id(house_id)
    district_info = get_district_by_id(house_info.district_id)
    house_info.district_info = district_info

    return JsonResponse({'district_name': house_info.district_info.name,
                         'house_type': "Дом" if house_info.type_field == "house" else "Квартира",
                         'house_id': intcomma(house_info.id),
                         'house_id_for_district': house_info.id_for_district,
                         'house_price': intcomma(house_info.price),
                         'house_basement': f"Имеется[<span style='color: rgb(255, 28, 28);'>lvl</span>={house_info.basement['level']}]" if
                         house_info.basement else "Отсутствует",
                         #  'house_basement_level': house_info['basement']['level'] if house_info['basement'] else 0,
                         'house_floor': house_info.floors,
                         'house_class': house_info.class_field})



class Magazine:
    """
    Класс Magazine предоставляет статические методы для получения информации о различных товарах.
    Все методы работают с моделями: Car, Yacht, Districts, Houses, Items.
    """

    @staticmethod
    def get_cars():
        """
        Метод для получения всех доступных автомобилей (с количеством больше 0).
        Возвращает список объектов Car.
        """
        return Car.objects.filter(quantity__gt=0)

    @staticmethod
    def get_yachts():
        """
        Метод для получения всех доступных яхт (с количеством больше 0).
        Возвращает список объектов Yacht.
        """
        return Yacht.objects.filter(quantity__gt=0)

    @staticmethod
    def get_districts():
        """
        Метод для получения всех районов.
        Возвращает список объектов Districts.
        """
        return Districts.objects.all()

    @staticmethod
    def get_free_houses_by_district_id(district_id):
        """
        Метод для получения всех доступных (свободных) домов в заданном районе.
        Свободные дома — это дома без владельца.
        Возвращает список объектов Houses.
        """
        return list(set(Houses.objects.filter(district_id=district_id, owner=None)))

    @staticmethod
    def get_videocards():
        """
        Метод для получения всех видеокарт.
        Возвращает список объектов Items, у которых тип равен 'videocard'.
        """
        return Items.objects.filter(type='videocard')



def get_cars(request: Request):
    with open(r'magazine\static\magazine\img\transport.svg',
              'r') as file:
        icon_content = file.read()

    return render(request,
                  'magazine/magazine_transport.html',
                  {
                      'type': 'car',
                      'icon': icon_content,
                      'transport': Magazine().get_cars(),
                      'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
                      'title': 'Cars'})


def get_yachts(request: Request):

    with open(r'C:\Users\kovalskiy\Documents\GitHub\rich_site\richMachine\magazine\static\magazine\img\yacht.svg',
              'r') as file:
        icon_content = file.read()
    return render(request,
                  'magazine/magazine_transport.html',
                  {
                      'type': 'yacht',
                      'icon': icon_content,
                      'transport': Magazine().get_yachts(),
                      'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
                      'title': 'Yachts'})


def get_districts(request: Request):

    with open(r'C:\Users\kovalskiy\Documents\GitHub\rich_site\richMachine\magazine\static\magazine\img\district.svg',
              'r') as file:
        icon_content = file.read()

    return render(request,
                  'magazine/magazine_districts.html',
                  {
                      'type': 'district',
                      'icon': icon_content,
                      'districts': Magazine().get_districts(),
                      'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
                      'title': 'Districts'})


def get_houses(request: Request, district_id: int):
    with open(r'C:\Users\kovalskiy\Documents\GitHub\rich_site\richMachine\magazine\static\magazine\img\house.svg',
              'r') as file:
        icon_content = file.read()

    return render(request,
                  'magazine/magazine_houses.html',
                  {'type': 'house',
                   'icon': icon_content,
                   'houses': Magazine().get_free_houses_by_district_id(district_id),
                   'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
                   'title': 'Houses'})


def get_videocards(request: Request):
    with open(r'C:\Users\kovalskiy\Documents\GitHub\rich_site\richMachine\magazine\static\magazine\img\videocard.svg',
              'r') as file:
        icon_content = file.read()

    return render(request,
                    'magazine/magazine_videocards.html',
                  {
                      'type': 'videocard',
                   'icon': icon_content,
                   'my_server_id': request.user.server_id if not request.user.is_anonymous else False,
                   'title': 'Videocards',
                   'videocards': Magazine().get_videocards()
                  }
                  )
