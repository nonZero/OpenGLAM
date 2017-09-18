from django.test import TestCase
from django.urls import reverse

from . import models
from users.models import User


class ProjectTests(TestCase):
    def test_create(self):
        u = User.objects.create_user('x@y.z', 'xyzzy')
        p = self.create_sample_project(u)
        self.assertIn("foo bar", p.summary_html)
        url = p.get_absolute_url()
        resp = self.client.get(url)
        self.assertContains(resp, "foo bar")

    def test_comments(self):
        su = User.objects.create_superuser(email='super@user.com',
                                           password='xyzzy')
        u = User.objects.create_user('x@y.z', 'xyzzy')
        p = self.create_sample_project(u)

        self.client.force_login(u)
        data = {
            'type': 'comment',
            'scope': models.ProjectComment.Scope.PRIVATE,
            'content': "yo123",
        }
        url = p.get_absolute_url()
        resp = self.client.post(url, data)
        self.assertEqual(p.comments.count(), 1)
        c = p.comments.first()

        self.client.force_login(su)
        url = reverse("projects:update_comment", args=(c.id,))
        resp = self.client.get(url)
        self.assertContains(resp, "yo123")

    def create_sample_project(self, u):
        o = models.Project(
            created_by=u,
            title="foo",
            summary_markdown="foo bar",
            link="http://example.com/link/",
            is_published=True,
            slug='foo',
        )
        o.full_clean()
        o.save()
        return o
