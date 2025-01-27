from django.http import JsonResponse

from django.db.models import Max
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from icecream import ic
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.views import APIView

from authentication import SiteAuthentication, TelegramAuthentication
from jobs.models import Jobs
from jobs.serializers import JobsSerializer
from utils import send_message_to_user
from rest_framework.permissions import IsAuthenticated


class WorkAPI(APIView):

    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='1/s', block=False))
    def post(self, request: Request):
        if getattr(request, 'limited', False):  # Проверка флага ограничения

            return JsonResponse({ 'success': False, 'error': 'Попробуйте позже'}, status=429)

        ic(request.data)
        clicks = request.data.get('clicks', 0)
        user_job = request.user.job
        ic(user_job)
        job_level_now = user_job.get('level', 0)

        user_job['tasks_completed'] += clicks

        job = Jobs.objects.get(level=job_level_now)
        next_job = Jobs.objects.filter(level=job_level_now + 1).first()

        max_level = Jobs.objects.aggregate(Max('level'))['level__max']

        ic(user_job['level'] + 1 <= max_level)
        ic(user_job['tasks_completed'] == job.required_exp)

        ic(request.user.job_lvl, max_level, user_job['tasks_completed'], next_job.required_exp, user_job['level'], next_job.level)
        if (request.user.job_lvl + 1 <= max_level and user_job['tasks_completed'] >= next_job.required_exp and
                user_job['level'] == next_job.level - 1 and user_job['level'] == request.user.job_lvl):
            # Если нынешний уровень + 1 меньше или равен максимально возможному уровню
            # Если количество кликов больше или равно обязательному количеству кликов следующей работы
            # Если используемый и будущий-1 уровни равны
            # Если используемый и открытый уровни равны

            send_message_to_user(request, {'text': 'Поздравляем! Вы открыли новую работу!'})
            user_job['tasks_completed'] = 0
            request.user.job_lvl += 1

        if (user_job['tasks_completed'] >= next_job.required_exp and user_job['tasks_completed'] % 7 == 0 and
            request.user.job_lvl < max_level):
            # Если количество кликов больше или равно обязательному количеству кликов следующей работы
            # Если остаток от деления количества кликов на 7 равно 0
            # Если открытый уровень меньше максимально возможному уровню(сейчас не максимальный уровень работы)

            send_message_to_user(request, {'text': 'Вам открыт следующий уровень работы!'})

        if request.user.job_lvl == max_level and user_job['tasks_completed'] == 0:
            send_message_to_user(request, {'text': 'Вы достигли последнего уровня работы!'})

        salary = int(job.salary * clicks)
        request.user.money['cash'] += salary

        request.user.job['total_earnings'] += salary
        request.user.save()
        #todo: доделать повышение уровня

        serializer = JobsSerializer(job)
        ic(serializer.data)


        return JsonResponse({'success': True, 'salary': int(job.salary),
                             'current_level': request.user.job_lvl,
                             'current_balance': request.user.money['cash'],
                             'job': serializer.data,
                             'current_exp': user_job['tasks_completed'],
                             'total_earnings': request.user.job['total_earnings'],
                             'required_exp': next_job.required_exp or 0
                             })