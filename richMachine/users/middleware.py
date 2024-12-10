import json
from django.utils.deprecation import MiddlewareMixin
from icecream import ic
from django.core.handlers.wsgi import WSGIRequest
from utils import coll

class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    def process_response(self, request, response: WSGIRequest):
        # Content Security Policy (CSP) заголовок
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://telegram.org https://oauth.telegram.org https://ajax.googleapis.com 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "frame-src https://telegram.org https://oauth.telegram.org; "
            "connect-src 'self' https://telegram.org; "
            "frame-ancestors 'self' https://oauth.telegram.org"
        )
        # X-Frame-Options заголовок
        response['X-Frame-Options'] = 'None'
        # print("[OPIFDI[PSDI[PFIASDOP[AFDIOP[FAIP[ODSI[FPO[PEO]]]]]]]]")
        return response

class RequestSourceMiddleware(MiddlewareMixin):
    def process_request(self, request: WSGIRequest):
        
        if request.path in ['/favicon.ico']:
            return
        
        # Проверяем заголовок
        source = request.headers.get('X-Requested-From')
        data = None
        
        # Если заголовка нет, проверяем тело запроса, когда отправлено JSON
        if not source:
            try:
                # Парсим JSON из request.body
                data = json.loads(request.body)
                source = data.get('source')

            except (json.JSONDecodeError, AttributeError):
                ...
        
        # Если данные переданы как POST форма, проверяем request.POST
        if not source and request.method == 'POST':
            source = request.POST.get('source')
            

        # Если данные переданы как GET параметры, проверяем request.GET
        if not source and request.method == 'GET':
            source = request.GET.get('source')

        # Добавляем источник запроса в request, чтобы он был доступен в views
        request.source = source
        request.data = data
        # ic(request.source, request.data)
        
class AuthenticationUserMiddleware(MiddlewareMixin):
    def process_request(self, request: WSGIRequest):

        user_server_id = None

        if request.source == 'telegram_bot':
            telegram_id = request.data.get('telegram_id')
            user_server_id = coll.find_one({"telegram_id": telegram_id}, projection={"_id": False, "server_id": True})['server_id']

        elif request.source == 'web':
            user_server_id = request.data.get('server_id')

        request.server_id = user_server_id

