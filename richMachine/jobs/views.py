from django.views import View
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated

from .models import Jobs

class WorkView(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/users/login/')  # перенаправление на страницу входа

        job_level_now = request.user.job['level']  # уровень работы в данный момент
        open_job_level = request.user.job_lvl  # максимальный уровень работы

        # Получение информации о текущей и следующей работе
        job = Jobs.objects.get(level=job_level_now)
        next_job = Jobs.objects.filter(level=job_level_now + 1).first()

        # Формирование контекста для шаблона
        context = {
            'my_server_id': request.user.server_id,
            'balance': request.user.money['cash'],
            'sphere': job.sphere,
            'name': job.name,
            'salary': int(job.salary),
            'level': job.level,
            'total_earnings': request.user.job['total_earnings'],
            'required_exp': next_job.required_exp if next_job else None,
            'current_exp': request.user.job['tasks_completed'],
        }

        return render(request, 'jobs/work.html', context)
