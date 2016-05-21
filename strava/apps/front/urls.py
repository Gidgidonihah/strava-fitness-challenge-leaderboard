""" Strava application urls. """

from django.conf.urls import url

from strava.apps.front import views

# pylint: disable=invalid-name
urlpatterns = [
    url(r'^authorize/$', views.AuthorizeView.as_view(), name='strava-auth'),
    url(r'^authorized/$', views.AuthorizedView.as_view(), name='strava-authorized'),
    url(r'^$', views.SummaryView.as_view(), name='strava-summary'),
]
