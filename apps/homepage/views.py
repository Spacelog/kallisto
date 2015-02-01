from django.views.generic import TemplateView
from apps.transcripts.models import Mission
from apps.people.models import User


class Homepage(TemplateView):
    template_name = 'homepage/home.html'

    def get_context_data(self, **kwargs):
        try:
            kwargs['mission'] = Mission.objects.current()
        except IndexError:
            # no missions in the system!
            pass
        kwargs['leaderboard_overall'] = User.objects.all().order_by(
            '-pages_cleaned',
        )
        return super(Homepage, self).get_context_data(**kwargs)


homepage = Homepage.as_view()
