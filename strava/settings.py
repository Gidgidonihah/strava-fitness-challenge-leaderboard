"""
Django settings for strava project.
"""
import os

from strava.private_settings import *  # noqa: F401

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
INSTALLED_APPS = (
    'apps.front',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]

# Strava settings (actually stored in private_settings.py)
# STRAVA_CLIENT_ID = ''
# STRAVA_CLIENT_SECRET = ''
# The following are hardcoded because quick and dirty
# TODO: implement so that these aren't needed in this file
# STRAVA_CHALLENGE_START_DATE = datetime.datetime(2016, 1, 1)
# STRAVA_CHALLENGE_END_DATE = datetime.datetime(2016, 5, 30)
# STRAVA_CHALLENGE_CLUB_ID = '12345'  # Not a real id
