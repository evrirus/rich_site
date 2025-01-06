import time

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from authentication import SiteAuthentication, TelegramAuthentication
from icecream import ic
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from django.db.models import Max
from rest_framework.permissions import AllowAny

from inventory.models import Inventory
from utils import (coll, db_cars, db_crypt, db_inv, get_car_by_id,
                   get_district_by_id, get_full_houses_info, get_house_by_id,
                   get_yacht_by_id, give_money, send_message_to_user)
from jobs.models import Jobs
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.core.cache import cache


class WorkAPI(APIView):

    authentication_classes = [SessionAuthentication, TelegramAuthentication, SiteAuthentication]
    permission_classes = []

    @method_decorator(ratelimit(key='ip', rate='1/3s', block=False))
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

        level_now = request.user.job_lvl
        max_level = Jobs.objects.aggregate(Max('level'))['level__max']


        ic(user_job['level'] + 1 <= max_level)
        ic(user_job['tasks_completed'] == job.required_exp)

        if user_job['level'] + 1 <= max_level and user_job['tasks_completed'] >= next_job.required_exp:
            send_message_to_user(request.user.server_id, {'text': 'Поздравляем! Вы открыли новую работу!'})
            user_job['tasks_completed'] = 0
            level_now += 1

        if level_now == max_level and user_job['tasks_completed'] == 0:
            send_message_to_user(request.user.server_id, {'text': 'Вы достигли последнего уровня работы!'})

        salary = int(job.salary * clicks)
        request.user.money['cash'] += salary


        request.user.save()
        #todo: доделать повышение уровня


        ic(job_level_now, level_now)



        return JsonResponse({'success': True})