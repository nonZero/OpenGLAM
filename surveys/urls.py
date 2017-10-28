from django.conf.urls import url

from surveys import views

urlpatterns = (
    url(r'^$', views.SurveyListView.as_view(), name='list'),
    url(r'^create/$', views.SurveyCreateView.as_view(),
        name='create'),
    url(r'^(?P<pk>[\d]+)/$', views.SurveyDetailView.as_view(),
        name='detail'),
    url(r'^(?P<pk>[\d]+)/edit/$', views.SurveyUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<slug>[\w]+)/$', views.SurveyAnswerView.as_view(),
        name='answer'),
)
