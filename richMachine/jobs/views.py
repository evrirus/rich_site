from icecream import ic
from django.views.generic import TemplateView

from jobs.models import Jobs


class WorkView(TemplateView):
    template_name = 'jobs/work.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_server_id'] = self.request.user.server_id
        context['balance'] = self.request.user.money['cash']

        job_level_now = self.request.user.job['level'] # лвл работы в данный момент работы
        open_job_level = self.request.user.job_lvl # максимальный лвл работы, который в принципе доступен сейчас


        job = Jobs.objects.get(level=job_level_now)
        next_job = Jobs.objects.filter(level=job_level_now + 1).first()

        context['sphere'] = job.sphere
        context['name'] = job.name
        context['salary'] = int(job.salary)

        context['level'] = job.level
        context['total_earnings'] = self.request.user.job['total_earnings']
        context['required_exp'] = next_job.required_exp
        context['current_exp'] = self.request.user.job['tasks_completed']

        return context
