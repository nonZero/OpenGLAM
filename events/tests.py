import datetime

from django.test import TestCase
from django.utils import timezone

from users.models import User
from . import models


class EventsTests(TestCase):
    def setUp(self):
        self.password = 'secret'
        self.su = User.objects.create_superuser(email='super@user.com',
                                                password=self.password,
                                                team_member=True,
                                                )

        now = timezone.now()
        tmrw = now + datetime.timedelta(1)
        title = "Party 123"
        self.e = models.Event.objects.create(
            title=title,
            slug="party123",
            created_by=self.su,
            starts_at=tmrw,
            ends_at=tmrw + datetime.timedelta(hours=2),
            registration_ends_at=now + datetime.timedelta(hours=5),
            location="Our house",
            description="Best.\nParty.\nEver.",
        )

        self.u1 = User.objects.create_user(email='user1@user.com')
        self.i1, created = self.e.invite_user(self.u1, self.su,
                                              "http://hackita.com/")
        self.assertTrue(created)

        x, created = self.e.invite_user(self.u1, self.su,
                                        "http://hackita.com/")
        self.assertFalse(created)

        self.assertEquals(x, self.i1)

    def login(self, user):
        self.client.login(email=user.email, password=self.password)

    def test_event(self):
        url = self.e.get_absolute_url()

        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)

        self.login(self.su)
        resp = self.client.get(url)
        self.assertContains(resp, self.e.title)

    def test_invitation(self):
        url = self.i1.get_absolute_url()

        resp = self.client.get(url)
        self.assertContains(resp, "title")
        # print(resp.content)
