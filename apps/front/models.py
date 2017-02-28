""" Models for the strava contents app. """
from django.db import models


class Athlete(models.Model):
    """ A authorized athlete. """
    strava_id = models.IntegerField(unique=True)
    strava_token = models.CharField(unique=True, max_length=50)
