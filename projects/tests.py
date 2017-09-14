from django.test import TestCase

from . import models
from users.models import User



class ProjectTests(TestCase):
    def test_create(self):
        u = User.objects.create_user('x@y.z', 'xyzzy')
        o = models.Project(
            created_by=u,
            title="foo",
            summary_markdown="foo bar",
            link="http://example.com/link/"
        )
        o.save()
        self.assertIn("foo", o.summary_html)



