# encoding: utf-8
import os.path

from django.conf import settings
from django.views.generic.base import TemplateView
import markdown


def read_faq(n):
    with open(os.path.join(os.path.dirname(__file__), 'faq%d.md' % n), encoding="utf8") as f:
        return markdown.markdown(f.read())


def get_faq():
    return [read_faq(n + 1) for n in range(2)]


FAQ = get_faq()


class WebsiteView(TemplateView):
    def get_template_names(self):
        assert self.name, 'name attribute must be defined'
        return "website/{}.html".format(self.name)


class HomeView(WebsiteView):
    name = 'home'


class ProgramView(WebsiteView):
    name = 'program'
    page_title = "על התכנית"


class FAQView(WebsiteView):
    name = 'faq'
    page_title = "שאלות ותשובות"

    def get_context_data(self, **kwargs):
        d = super(FAQView, self).get_context_data(**kwargs)
        d['faq'] = get_faq() if settings.DEBUG else FAQ
        return d


class AboutView(WebsiteView):
    name = 'about'
    page_title = "עלינו"


class TermsView(WebsiteView):
    name = 'terms'
    page_title = "הצהרת פרטיות"
