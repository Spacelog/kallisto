from datetime import timedelta
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
import os.path

from .models import Page
from .factories import *


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'apps/transcripts/test_media'),
)
class NextPage(TestCase):

    def test_basic(self):
        """next_page_for_user() locks different pages for different users"""
        mission = MissionFactory()
        pages = PageFactory.create_batch(3, mission=mission)
        users = UserFactory.create_batch(2)

        page1 = mission.next_page_for_user(users[0])
        page2 = mission.next_page_for_user(users[1])

        self.assertIsNotNone(page1)
        self.assertIsNotNone(page2)
        self.assertNotEqual(page1.pk, page2.pk)
        self.assertEqual(page1.pk, pages[0].pk)
        self.assertEqual(page2.pk, pages[1].pk)

    def test_skips_approved(self):
        """next_page_for_user() doesn't locked already-approved pages"""
        mission = MissionFactory()
        pages = PageFactory.create_batch(
            1,
            mission=mission,
            approved=True
        ) + PageFactory.create_batch(
            2,
            mission=mission,
        )
        users = UserFactory.create_batch(2)

        page1 = pages[0]
        page2 = mission.next_page_for_user(users[0])
        page3 = mission.next_page_for_user(users[1])

        self.assertIsNotNone(page2)
        self.assertIsNotNone(page3)
        self.assertNotEqual(page2.pk, page3.pk)
        self.assertNotIn(page1, (page2, page3))

    def test_repeat_query(self):
        """next_page_for_user() will keep returning the same page"""
        mission = MissionFactory()
        pages = PageFactory.create_batch(3, mission=mission)
        users = UserFactory.create_batch(2)

        page1 = mission.next_page_for_user(users[0])
        page2 = mission.next_page_for_user(users[0])

        self.assertIsNotNone(page1)
        self.assertIsNotNone(page2)
        self.assertEqual(page1.pk, page2.pk)

    def test_repeat_query_approved(self):
        """next_page_for_user() won't return the same page once it's approved"""
        mission = MissionFactory()
        pages = PageFactory.create_batch(3, mission=mission)
        users = UserFactory.create_batch(2)

        page1 = mission.next_page_for_user(users[0])
        Page.objects.filter(pk=page1.pk).update(approved=True)
        page2 = mission.next_page_for_user(users[0])

        self.assertIsNotNone(page1)
        self.assertIsNotNone(page2)
        self.assertNotEqual(page1.pk, page2.pk)

    def test_claims_expired_locks(self):
        """next_page_for_user() can grab an expired lock"""
        mission = MissionFactory()
        pages = PageFactory.create_batch(3, mission=mission)
        users = UserFactory.create_batch(2)

        Page.objects.filter(pk=pages[0].pk).update(
            locked_by=users[1],
            locked_until=timezone.now() - timedelta(seconds=1),
        )

        page = mission.next_page_for_user(users[0])
        self.assertIsNotNone(page)
        self.assertEqual(pages[0].pk, page.pk)

    def test_claims_expired_unapproved_locks(self):
        """next_page_for_user() can't grab expired lock for an approved page"""
        # note this should never actually happen because we release the lock
        # when we approve a page
        mission = MissionFactory()
        pages = PageFactory.create_batch(1, mission=mission)
        users = UserFactory.create_batch(2)

        Page.objects.filter(pk=pages[0].pk).update(
            locked_by=users[1],
            locked_until=timezone.now() - timedelta(seconds=1),
            approved=True,
        )

        page = mission.next_page_for_user(users[0])
        self.assertIsNone(page)

    def test_fails_gracefully(self):
        """next_page_for_user() fails to find a page cleanly"""
        mission = MissionFactory()
        pages = PageFactory.create_batch(1, mission=mission)
        users = UserFactory.create_batch(2)

        page1 = mission.next_page_for_user(users[0])
        page2 = mission.next_page_for_user(users[1])
        self.assertIsNotNone(page1)
        self.assertIsNone(page2)
