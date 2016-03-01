""" Strava application urls. """

from django.conf.urls import url

from .views import AuthorizeView
from .views import AuthorizedView
from .views import SummaryView


urlpatterns = [
    url(r'^authorize/$', AuthorizeView.as_view(), name='strava-auth'),
    url(r'^authorized/$', AuthorizedView.as_view(), name='strava-authorized'),
    url(r'^$', SummaryView.as_view(), name='strava-summary'),
]
