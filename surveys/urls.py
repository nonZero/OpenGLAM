from django.conf.urls import url

from surveys import views

urlpatterns = (
    url(r'^$', views.SurveyListView.as_view(), name='list'),
    url(r'^(?P<pk>[\d]+)/$', views.SurveyDetailView.as_view(),
        name='detail'),
    url(r'^(?P<slug>[\w]+)/$', views.SurveyAnswerView.as_view(),
        name='answer'),
)
