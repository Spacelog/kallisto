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
        kwargs['leaderboard_overall'] = User.objects.raw(
            """
            SELECT id, name, pages_cleaned, pages_approved
            FROM people_user
            WHERE (pages_cleaned > 0 OR pages_approved > 0)
            ORDER BY (2 * pages_cleaned + pages_approved) DESC
            """
        )[:10]
        return super(Homepage, self).get_context_data(**kwargs)


homepage = Homepage.as_view()
