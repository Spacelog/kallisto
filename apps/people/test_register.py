from bs4 import BeautifulSoup
from django.core import mail
from django.core.urlresolvers import reverse
from django_webtest import WebTest


from .models import User


class Register(WebTest):
    EMAIL = 'test@example.com'
    NAME = 'Test user'
    PASSWORD = 'fish'

    def test_success(self):
        """
        Signing up creates an inactive user, sends an email to
        confirm (and convert to active) whose link also logs
        you in.
        """

        resp = self.app.get(reverse('register'))
        form = resp.forms['register']
        form.set('email', self.EMAIL)
        form.set('name', self.NAME)
        form.set('password', self.PASSWORD)
        resp = form.submit()

        self.assertEqual(302, resp.status_int)
        self.assertEqual(
            "http://localhost:80" + reverse("registered"),
            resp.headers['location'],
        )
        resp = resp.follow()
        # not logged in yet
        self.assertFalse(self.NAME in resp)

        self.assertEqual(1, User.objects.count())
        user = User.objects.get()
        self.assertEqual(self.EMAIL, user.email)
        self.assertEqual(self.NAME, user.name)
        self.assertEqual(False, user.is_active)

        # Check welcome email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue('welcome' in email.subject.lower())
        email = mail.outbox[0]
        self.assertEqual('text/html', email.alternatives[0][1])
        soup = BeautifulSoup(email.alternatives[0][0])
        confirm_url = soup.findAll('a')[0]['href'] # FIXME: fragile dependency on HTML email details!

        # user should be inactive; when we hit the URL it should become active
        self.assertEqual(1, User.objects.filter(is_active=False, email=self.EMAIL).count())
        response = self.app.get(confirm_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, User.objects.filter(is_active=False, email=self.EMAIL).count())
        form = response.forms['confirm-email-form']
        response = form.submit()
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, User.objects.filter(is_active=True, email=self.EMAIL).count())
        # also our session (ie access via self.app) should be logged in
        # we test this by hitting the password change URL and seeing if we're
        # redirected (not logged in)
        response = self.app.get(reverse('password_change'))
        self.assertEqual(200, response.status_code)

    def test_duplicate_email(self):
        """Can't sign up with an existing email."""

        User.objects.create(
            email=self.EMAIL,
            name=self.NAME,
        )
        
        resp = self.app.get(reverse('register'))
        form = resp.forms['register']
        form.set('email', self.EMAIL)
        form.set('name', self.NAME)
        form.set('password', self.PASSWORD)
        resp = form.submit()

        self.assertEqual(200, resp.status_int)
        self.assertEqual(1, len(resp.html.find_all("ul", class_="errorlist")))
        self.assertEqual(1, User.objects.count())
