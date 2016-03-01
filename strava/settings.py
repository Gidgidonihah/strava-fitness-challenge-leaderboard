"""
Django settings for strava project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i=bc(3sltj&y4qn)dio4m9bieb&t3d6f-r8hej%^9w9@g4v0b-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
INSTALLED_APPS = (
    'front',
    'django.contrib.auth',
    'django.contrib.contenttypes',
)
ROOT_URLCONF = 'strava.urls'
WSGI_APPLICATION = 'strava.wsgi.application'
STATIC_URL = '/static/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'stravalib': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

MIDDLEWARE_CLASSES = (
    # We don't need no stinking middleware!
)

# Strava settings
STRAVA_CLIENT_ID = ''
STRAVA_CLIENT_SECRET = ''
# The following are hardcoded because quick and dirty
STRAVA_USER_ACCESS_TOKEN = ''
DFC_CLUB_ID = ''  # Doba Fitness Challenge club id.
