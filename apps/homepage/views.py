from django.views.generic import TemplateView
from apps.transcripts.models import Mission


class Homepage(TemplateView):

    def get_template_names(self):
        if self.request.user.is_authenticated():
            return [ 'homepage/authenticated.html' ]
        else:
            return [ 'homepage/anonymous.html' ]

    def get_context_data(self, **kwargs):
        kwargs.update(
            {
                'mission': Mission.objects.current(),
            }
        )
        return super(Homepage, self).get_context_data(**kwargs)


homepage = Homepage.as_view()
