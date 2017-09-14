import json

import re
from django.conf import settings
from django.contrib import auth
from django.core import mail

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import User, Code


class UsersTests(TestCase):
    def setUp(self):
        self.password = 'secret'
        self.su = User.objects.create_superuser(email='super@user.com',
                                                password=self.password,
                                                is_staff=True,
                                                team_member=True)

        now = timezone.now()
        self.u1 = User.objects.create_user(email='user1@user.com',
                                           password=self.password)
        self.u2 = User.objects.create_user(email='user2@user.com',
                                           password=self.password,
                                           community_member=True)

    def login(self, user):
        assert self.client.login(email=user.email, password=self.password)

    def test_user_detail(self):
        url = self.u1.get_absolute_url()

        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)

        self.login(self.su)
        resp = self.client.get(url)
        self.assertContains(resp, self.u1.email)

        resp = self.client.post(url)
        self.assertEquals(resp.status_code, 400)

        mail.outbox = []
        resp = self.client.post(url, {
            'content': 'xyzzy',
        })
        self.assertEquals(resp.status_code, 200)
        d = json.loads(resp.content.decode('utf8'))
        self.assertIn('result', d)
        self.assertRegex(d['result'], 'id="note-\d+"')
        self.assertEquals(len(mail.outbox), len(settings.MANAGERS))

        # Do not send if not visible to user
        mail.outbox = []
        resp = self.client.post(url, {
            'content': 'xyzzy',
            'send_to_user': '1',
        })
        self.assertEquals(resp.status_code, 200)
        d = json.loads(resp.content.decode('utf8'))
        self.assertIn('result', d)
        self.assertRegex(d['result'], 'id="note-\d+"')
        self.assertEquals(len(mail.outbox), len(settings.MANAGERS))

        mail.outbox = []
        resp = self.client.post(url, {
            'content': 'xyzzy',
            'visible_to_user': '1',
            'send_to_user': '1',
        })
        self.assertEquals(resp.status_code, 200)
        d = json.loads(resp.content.decode('utf8'))
        self.assertIn('result', d)
        self.assertRegex(d['result'], 'id="note-\d+"')
        self.assertEquals(len(mail.outbox), len(settings.MANAGERS) + 1)

    def test_community_list(self):
        url = reverse("users:community")

        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)

        self.login(self.u1)
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 403)

        self.login(self.u2)
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_community_edit_profile(self):
        url = reverse("users:community_profile")

        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)

        self.login(self.u1)
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 403)

        self.login(self.u2)
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_signup(self):
        mail.outbox = []
        email = "user123@example.com"

        user_qs = User.objects.filter(email=email)
        code_qs = Code.objects.filter(email=email)

        self.assertEqual(user_qs.count(), 0)
        self.assertEqual(code_qs.count(), 0)

        url = reverse("users:signup")
        resp = self.client.post(url, {'email': email})
        self.assertEquals(resp.status_code, 302)

        self.assertEqual(user_qs.count(), 0)
        self.assertEqual(code_qs.count(), 1)

        self.assertEquals(len(mail.outbox), 1)
        html = mail.outbox[0].body
        validate_url = re.search(r"http://testserver/[\w/]+", html)[0]

        resp = self.client.get(validate_url)
        self.assertEquals(resp.status_code, 302)

        self.assertEqual(user_qs.count(), 1)
        self.assertEqual(code_qs.count(), 0)

        resp = self.client.get(resp.url)
        self.assertEquals(resp.status_code, 200)

        user = auth.get_user(self.client)
        self.assertEquals(user, user_qs.first())

