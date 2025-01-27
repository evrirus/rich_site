# users/views.py

from wsgiref.simple_server import WSGIRequestHandler

from django.http import  HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse

from rest_framework.authentication import SessionAuthentication

from rest_framework.views import APIView

from utils import DoRequest
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from icecream import ic
from rest_framework.request import Request

from django.views import View



DOMEN = 'http://127.0.0.1:8000/'


# Register
class SignUpView(View):
    def get(self, request: Request):
        return render(request, 'registration/signup.html')


# Login
class SignInView(View):
    def get(self, request: Request):
        return render(request, 'registration/login.html')



@login_required(login_url="/users/login/")
def profile(request, server_id: int):
    # Проверяем, соответствует ли текущий пользователь запрашиваемому серверному ID
    # Если нет, возвращаем 404 (раскомментировать при необходимости)
    # if request.user.server_id != server_id:
    #     return HttpResponseNotFound(render(request, '404.html'))

    # Формируем данные для отправки в API
    data = {"action": "get_profile", "server_id": server_id, "source": "web"}
    
    # Выполняем запрос к API для получения профиля пользователя
    response = DoRequest('api/get_profile/', 'POST', data=data)
    
    # Если API вернул пустой ответ, возвращаем 404 страницу
    if not response:
        return HttpResponseNotFound(render(request, '404.html'))
    
    # Добавляем заголовок к данным ответа
    response['title'] = f"User profile ID: {response['server_id']}"
    
    # Рендерим страницу профиля с данными из API
    return render(request, 'profile.html', response)



@login_required(login_url="/users/login/")
def self_profile(request: WSGIRequestHandler):
    """
    Перенаправляет текущего пользователя на страницу его профиля.

    :param request: Объект HTTP-запроса.
    :return: Перенаправление на страницу профиля пользователя.
    """
    # Используем серверный ID текущего пользователя для формирования URL профиля
    return redirect(reverse('profile', kwargs={'server_id': request.user.server_id}))










def page_not_found(request, exception):
    """
    Обработчик для ошибок 404 (страница не найдена).

    :param request: Объект HTTP-запроса.
    :param exception: Исключение, вызвавшее ошибку 404.
    :return: Ответ с рендерингом шаблона 404.html.
    """
    # Логируем информацию об исключении для отладки
    ic(exception)

    # Рендерим пользовательскую страницу ошибки
    return render(request, "404.html", status=404)




class RenderBasementView(APIView):
    """
    API для отображения информации о подвале дома.

    Параметры:
        :param id_house: int - Идентификатор дома.

    Возвращает:
        - HTML-страницу с данными о подвале.
        - Если данных нет, устанавливается флаг `success: False`.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = []  # Измените на нужные права доступа.

    def get(self, request: Request, id_house: int):
        """
        Обрабатывает GET-запрос для получения информации о подвале дома.
        """

        # Подготовка данных для запроса к API
        data = {
            "action": "get_basement",
            "server_id": request.user.server_id,
            "source": "web"
        }

        # Логирование запроса (для отладки)
        api_endpoint = f'api/get_basement/{id_house}/'
        ic(api_endpoint)

        # Выполнение запроса к стороннему API
        response = DoRequest(api_endpoint, 'GET', json=data)
        ic(response)

        if not response:
            return render(request, 'basement.html', {'success': False, 'message': 'Данные не найдены.'})

        # Расчёт дохода и текущего количества видеокарт
        income = 0
        videocards = response.get('videocards', [])
        current_videocards = len(videocards)
        limit_videocards = response.get('house_info', {}).get('basement', {}).get('maxQuantity', 0)

        for videocard in videocards:
            income += videocard.get('performance', 0)

        # Подготовка данных для передачи в шаблон
        response.update({
            'my_server_id': request.user.server_id,
            'income': income,
            'quantity_videocards': current_videocards,
            'limit_videocards': limit_videocards,
            'mix_videocards': response.get('mix_videocards', []),
            'success': bool(videocards)  # Устанавливаем `False`, если видеокарт нет
        })

        # Рендерим страницу
        return render(request, 'basement.html', response)
