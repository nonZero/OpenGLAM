from django.test import TestCase

from website.views import FAQ


class WebsiteTest(TestCase):
    def test_faq(self):
        """
        Checks FAQ parsing
        """
        self.assertEqual(2, len(FAQ))

        for s in FAQ:
            self.assertIsInstance(s, str)
