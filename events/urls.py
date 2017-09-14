from django.conf.urls import url

from . import views

urlpatterns = (
    url(r'^$', views.EventListView.as_view(), name='list'),
    url(r'^(?P<slug>[-\w]+)/$', views.EventDetailView.as_view(),
        name='detail'),

    url(r'^(?P<slug>[-\w]+)/contacts/$', views.EventContactsView.as_view(),
        name='contacts'),

    url(r'^invitation/(?P<slug>\w+)/$',
        views.InvitationDetailView.as_view(), name='invitation'),

    url(r'^invitation/(?P<slug>\w+)/preview/$',
        views.InvitationPreviewView.as_view(), name='invitation_preview'),

    url(r'^invitation/(?P<slug>\w+)/edit/$',
        views.InvitationUpdateView.as_view(), name='invitation_edit'),

)
