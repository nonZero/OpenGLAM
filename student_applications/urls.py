from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.Dashboard.as_view(), name='dashboard'),
    url(r'^personal-details/$', views.PersonalDetailsView.as_view(),
        name='personal_details'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^review/$', views.ReviewView.as_view(), name='review'),

    # STAFF ONLY

    url(r'^app/$', views.ApplicationListView.as_view(), name='app_list'),
    url(r'^app/(?P<pk>\d+)/$', views.ApplicationDetailView.as_view(),
        name='app_detail'),
    url(r'^app/(?P<pk>\d+)/status/$', views.ApplicationStatusUpdateView.as_view(),
        name='app_status'),
    url(r'^app/(?P<pk>\d+)/review/$',
        views.ApplicationReviewCreateView.as_view(), name='app_review'),
    url(r'^edit-app-review/(?P<pk>\d+)/$',
        views.ApplicationReviewUpdateView.as_view(), name='app_review_update'),
    # url(r'^users/(?P<pk>\d+)/add-note/$', users_views.CreateUserNoteView.as_view(),
    #     name='user_add_note'),
    # url(r'^users/(?P<pk>\d+)/edit/$', sa_views.UserCohortUpdateView.as_view(),
    #     name='user_edit'),
    # url(r'^users/log/$', users_views.AllUsersLogView.as_view(),
    #     name='users_log'),
    #
    # url(r'^cohort/$', sa_views.CohortListView.as_view(), name='cohorts'),
    # url(r'^cohort/(?P<slug>\d+)/$', sa_views.CohortDetailView.as_view(),
    #     name='cohort'),
    #
    # url(r'^survey/', include('surveys.urls')),
    #
    # url(r'^learn/', include('lms.urls')),
    #
    #
    # # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^hadmin/doc/', include('django.contrib.admindocs.urls')),
    #
    # # Uncomment the next line to enable the admin:
    # url(r'^hadmin/', include(admin.site.urls)),
]
#
# if settings.DEBUG:
#     urlpatterns += patterns('',
#         (r'^500/$', 'django.views.defaults.server_error'),
#         (r'^404/$', 'django.views.defaults.page_not_found'),
#     )
#
#     import debug_toolbar
#     urlpatterns += patterns('',
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     )
