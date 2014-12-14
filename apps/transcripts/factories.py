from datetime import timedelta
from django.utils import timezone
import factory

from .models import Mission, Page, Revision, LockExpired
from apps.people.models import User


class MissionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Mission

    name = factory.Sequence(lambda n: "Mission %i" % n)
    short_name = factory.Sequence(lambda n: "MI%i" % n)
    start = timezone.now()
    end = timezone.now() + timedelta(days=1)
    patch = "dummy-patch.png"


class PageFactory(factory.DjangoModelFactory):
    class Meta:
        model = Page

    number = factory.Sequence(lambda n: n)
    original = "dummy-original.png"
    original_text = factory.Sequence(lambda n: u"Original text %i." % n)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: "user-%i@example.com" % n)
    name = factory.Sequence(lambda n: "User %i" % n)
