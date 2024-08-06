from django.utils.deprecation import MiddlewareMixin

class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
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
