from datetime import timedelta
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils import timezone
from django_webtest import WebTest
import factory
import os.path

from .factories import *
from .models import Page
from apps.people.models import User


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'apps/transcripts/test_media'),
)
class Clean(WebTest):
    """Test the page cleaning mechanics."""

    def test_simple(self):
        """Can clean a page to create a new revision."""

        mission = MissionFactory()
        pages = PageFactory.create_batch(2, mission=mission)
        user = UserFactory()

        resp = self.app.get(
            reverse(
                "mission-clean-next",
                kwargs={ 'slug': mission.short_name }
            ),
            user=user.email,
        )
        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse(
                "mission-page",
                kwargs={
                    'slug': mission.short_name,
                    'page': pages[0].number,
                }
            ),
            resp.headers['location'],
        )
        resp = resp.follow()
        form = resp.forms['clean']
        form.set('text', 'A totally different bit of text.')
        resp = form.submit()
        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse(
                "mission-clean-next",
                kwargs={ 'slug': mission.short_name }
            ),
            resp.headers['location'],
        )
        resp = resp.follow()
        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse(
                "mission-page",
                kwargs={
                    'slug': mission.short_name,
                    'page': pages[1].number,
                }
            ),
            resp.headers['location'],
        )

        self.assertEqual(1, pages[0].revisions.count())
        self.assertEqual(0, pages[1].revisions.count())
        self.assertEqual(False, Page.objects.get(pk=pages[0].pk).approved)
        self.assertEqual(1, User.objects.get().pages_cleaned)
        self.assertEqual(0, User.objects.get().pages_approved)

    def test_approved(self):
        """Cleaning a page with no changes approves the last revision."""

        mission = MissionFactory()
        pages = PageFactory.create_batch(2, mission=mission)
        user = UserFactory()

        resp = self.app.get(
            reverse(
                "mission-clean-next",
                kwargs={ 'slug': mission.short_name }
            ),
            user=user.email,
        )
        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse(
                "mission-page",
                kwargs={
                    'slug': mission.short_name,
                    'page': pages[0].number,
                }
            ),
            resp.headers['location'],
        )
        resp = resp.follow()
        form = resp.forms['clean']
        # don't change the cleaned text
        resp = form.submit()
        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse(
                "mission-clean-next",
                kwargs={ 'slug': mission.short_name }
            ),
            resp.headers['location'],
        )
        resp = resp.follow()
        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse(
                "mission-page",
                kwargs={
                    'slug': mission.short_name,
                    'page': pages[1].number,
                }
            ),
            resp.headers['location'],
        )

        self.assertEqual(1, pages[0].revisions.count())
        self.assertEqual(0, pages[1].revisions.count())
        self.assertEqual(True, Page.objects.get(pk=pages[0].pk).approved)
        self.assertEqual(0, User.objects.get().pages_cleaned)
        self.assertEqual(1, User.objects.get().pages_approved)

    def test_lock_expired(self):
        """When the lock expires before submitting, we can still submit."""
        # if no one else has claimed the lock, we might as well use our
        # stale one

        mission = MissionFactory()
        pages = PageFactory.create_batch(2, mission=mission)
        user = UserFactory()

        resp = self.app.get(
            reverse(
                "mission-clean-next",
                kwargs={ 'slug': mission.short_name }
            ),
            user=user.email,
        )
        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse(
                "mission-page",
                kwargs={
                    'slug': mission.short_name,
                    'page': pages[0].number,
                }
            ),
            resp.headers['location'],
        )
        resp = resp.follow()
        form = resp.forms['clean']
        form.set('text', 'A totally different bit of text.')
        # expire the lock
        Page.objects.filter(
            locked_by__isnull=False,
        ).update(
            locked_until=timezone.now() - timedelta(seconds=1),
        )
        resp = form.submit()
        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse(
                "mission-clean-next",
                kwargs={ 'slug': mission.short_name }
            ),
            resp.headers['location'],
        )
        resp = resp.follow()
        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse(
                "mission-page",
                kwargs={
                    'slug': mission.short_name,
                    'page': pages[1].number,
                }
            ),
            resp.headers['location'],
        )

        self.assertEqual(1, pages[0].revisions.count())
        self.assertEqual(0, pages[1].revisions.count())
        self.assertEqual(False, Page.objects.get(pk=pages[0].pk).approved)
        self.assertEqual(1, User.objects.get().pages_cleaned)
        self.assertEqual(0, User.objects.get().pages_approved)

    def test_lock_released(self):
        """When the lock is lost before submitting, a helpful error."""

        mission = MissionFactory()
        pages = PageFactory.create_batch(2, mission=mission)
        user = UserFactory()

        resp = self.app.get(
            reverse(
                "mission-clean-next",
                kwargs={ 'slug': mission.short_name }
            ),
            user=user.email,
        )
        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse(
                "mission-page",
                kwargs={
                    'slug': mission.short_name,
                    'page': pages[0].number,
                }
            ),
            resp.headers['location'],
        )
        resp = resp.follow()
        form = resp.forms['clean']
        # release the lock
        Page.objects.filter(
            locked_by__isnull=False,
        ).update(
            locked_by=None,
            locked_until=None,
        )
        resp = form.submit()
        self.assertEqual(200, resp.status_int)
        self.assertTrue(
            "Lock expired" in resp.body
        )

        self.assertEqual(0, pages[0].revisions.count())
        self.assertEqual(0, pages[1].revisions.count())
        self.assertEqual(False, Page.objects.get(pk=pages[0].pk).approved)
        self.assertEqual(0, User.objects.get().pages_cleaned)
        self.assertEqual(0, User.objects.get().pages_approved)

    def test_nothing_to_clean(self):
        """When there's nothing to clean, we go back to the homepage."""

        mission = MissionFactory()
        pages = PageFactory.create_batch(3, mission=mission, approved=True)
        user = UserFactory()
        
        resp = self.app.get(
            reverse(
                "mission-clean-next",
                kwargs={ 'slug': mission.short_name }
            ),
            user=user.email,
        )
        self.assertEqual(302, resp.status_int)
        self.assertEqual("http://localhost:80" + reverse("homepage"), resp.headers['location'])
