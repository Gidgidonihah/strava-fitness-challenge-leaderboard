"""
Strava URL Configuration
"""
from django.conf.urls import include, url

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^', include('apps.front.urls')),
]
