from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^signup/$', views.SignupView.as_view(), name='signup'),
    url(r'^set-password/$', views.SetPasswordView.as_view(),
        name='set_password'),
    url(r'^set-names/$', views.UserDisplayNamesView.as_view(),
        name='set_names'),
    url(r'^check-your-email/$', views.ValidationSentView.as_view(),
        name='validation_sent'),
    url(r'^validate/(?P<code>\w{32})/$', views.ValidateView.as_view(),
        name='validate'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),

    url(r'^$', views.UserListView.as_view(), name='list'),

    url(r'^community/$', views.CommunityListView.as_view(),
        name='community'),
    url(r'^community/(?P<pk>\d+)/$', views.CommunityDetailView.as_view(),
        name='community_user'),
    url(r'^community-profile/$', views.UserCommunityDetailsUpdateView.as_view(),
        name='community_profile'),

    url(r'^(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/contact\.vcf$', views.UserVCFView.as_view(), name='vcf'),
    url(r'^(?P<pk>\d+)/tags/$', views.UserTagsEditView.as_view(), name='tags'),

    url(r'^all-emails/$', views.AllEmailsView.as_view(), name='list_emails'),

    url(r'^notes/$', views.UserNoteListView.as_view(), name='list_notes'),
    url(r'^notes/open/$', views.OpenUserNoteListView.as_view(),
        name='list_notes_open'),

    url(r'^notes/(?P<pk>\d+)/close/$', views.UserNoteCloseView.as_view(),
        name='close_note'),

    # url(r'^$', views.UserListView.as_view(),
    #     name='users'),
    #
    # url(r'^(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='user'),

]
