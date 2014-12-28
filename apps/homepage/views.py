from django.views.generic import TemplateView
from apps.transcripts.models import Mission


class Homepage(TemplateView):
    template_name = 'homepage/home.html'

    def get_context_data(self, **kwargs):
        kwargs.update(
            {
                'mission': Mission.objects.current(),
            }
        )
        return super(Homepage, self).get_context_data(**kwargs)


homepage = Homepage.as_view()
