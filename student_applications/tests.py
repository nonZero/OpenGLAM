import json

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.forms.utils import ErrorDict
from django.test import TestCase

from users.models import User, PersonalInfo


class StudentApplicationsTests(TestCase):
    def setUp(self):
        self.u_password = "foobar"
        self.u = User.objects.create_user("foo@bar.com",
                                          self.u_password)
        self.staff = User.objects.create_user("staff@bar.com", "staff")

    def login(self):
        self.client.login(email=self.u.email, password=self.u_password)

    def test_personal_details(self):
        self.login()
        self.assertFalse(hasattr(self.u, 'personalinfo'))
        url = reverse('sa:personal_details')
        r = self.client.get(url)
        self.assertEquals(200, r.status_code)

        data = {
        }

        r = self.client.post(url, data)
        self.assertEquals(200, r.status_code)
        form = r.context['form']
        assert isinstance(form.errors, ErrorDict)
        self.assertNotEquals(len(form.errors), 0)

        data = {
            "hebrew_first_name": "פו",
            "hebrew_last_name": "בר",
            "english_first_name": "foo",
            "english_last_name": "bar",

            "main_phone": "050-5555555",
            "alt_phone": "050-7654321",

            "city": "Jerusalem",
            "address": "123 ACME St.",

            "gender": PersonalInfo.MALE,
        }

        r = self.client.post(url, data)
        self.assertEquals(302, r.status_code)

        # self.u.refresh_from_db() # Does not work
        self.u = User.objects.get(id=self.u.id)

        for k, v in data.items():
            actual = getattr(self.u.personalinfo, k)
            self.assertEquals(actual, v)

        self.assertEquals(self.u.hebrew_display_name, "פו בר")
        self.assertEquals(self.u.english_display_name, "Foo Bar")

        # Filling personal details once is enough
        r = self.client.get(url)
        self.assertRedirects(r, reverse('sa:dashboard'))

    def test_register(self):
        self.test_personal_details()
        url = reverse('sa:register')
        r = self.client.get(url)
        self.assertEquals(200, r.status_code)

        r = self.client.post(url)
        self.assertGreater(len(r.context['form'].errors), 0)
        self.assertEquals(200, r.status_code)
        self.assertEquals(0, self.u.answers.count())

        data = {
            "about": "Shalom"
        }

        r = self.client.post(url, data)
        self.assertEquals(302, r.status_code)
        self.assertEquals(1, self.u.answers.count())
        self.assertEquals(1, self.u.application.forms_filled)

    def test_dashboard(self):
        url = reverse('sa:dashboard')

        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)

        self.login()
        resp = self.client.get(url)
        self.assertContains(resp, self.u.email)
        self.assertNotContains(resp, 'xyzzy1')

        resp = self.client.post(url)
        self.assertEquals(resp.status_code, 400)

        mail.outbox = []
        resp = self.client.post(url, {
            'content': 'xyzzy1',
        })
        self.assertEquals(resp.status_code, 200)
        d = json.loads(resp.content.decode('utf8'))
        self.assertIn('result', d)
        self.assertRegex(d['result'], 'xyzzy1')
        self.assertEquals(len(mail.outbox), len(settings.MANAGERS))

        resp = self.client.get(url)
        self.assertContains(resp, 'xyzzy1')
