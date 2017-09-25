from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.defaults import page_not_found
from django.views.generic.base import RedirectView

from website import views

i = lambda s, prefix=None: url(r'^{}/'.format(prefix or s),
                               include('{}.urls'.format(s),
                                       namespace=prefix or s))

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^program/$', views.ProgramView.as_view(), name='program'),
    url(r'^faq/$', views.FAQView.as_view(), name='faq'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^terms/$', views.TermsView.as_view(), name='terms'),
    # url(r'^$', views.CreateProjectView.as_view(), name='home'),
    # url(r'^blog/', include('blog.urls')),
    i("projects"),
    i("users"),
    i("student_applications", "sa"),
    i("surveys"),
    i("events"),


    url('^social/', include('social_django.urls', namespace='social')),

    url(r'^hadmin/', include(admin.site.urls)),

    url(r'^404/$', lambda r: page_not_found(r, ValueError("Testing 123"))),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns.append(
        url(r'^xyzzy/$', views.TeaserView.as_view()),
    )