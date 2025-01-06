from icecream import ic
from django.views.generic import TemplateView


class WorkView(TemplateView):
    template_name = 'jobs/work.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_server_id'] = self.request.user.server_id
        return context
