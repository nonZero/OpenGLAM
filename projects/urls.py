from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ProjectListView.as_view(), name='list'),
    url(r'^bid/$', views.ProjectBidView.as_view(), name='bid'),
    url(r'^bid/results/$', views.ProjectBidsView.as_view(), name='bid_results'),
    url(r'^show-votes/$', views.ProjectVotesView.as_view(), name='list_votes'),
    url(r'^create-new/$', views.ProjectCreateView.as_view(), name='create'),
    url(r'^(?P<slug>\w+)/$', views.ProjectDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/edit/$', views.ProjectUpdateView.as_view(),
        name='update'),
    url(r'^edit-comment/(?P<pk>\d+)/$',
        views.ProjectCommentUpdateView.as_view(),
        name='update_comment'),
    url(r'^review-comment/(?P<pk>\d+)/$',
        views.ProjectCommentMarkReviewedView.as_view(),
        name='review_comment'),

    url(r'^latest-comments/$', views.ProjectCommentListView.as_view(),
        name='list_comments'),

]
