"""
Strava URL Configuration
"""
from django.conf.urls import include, url

urlpatterns = [
    url(r'^', include('front.urls')),
]
