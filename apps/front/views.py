""" Views for strava integration. """
from __future__ import unicode_literals

import operator
from collections import OrderedDict

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.base import TemplateView
from stravalib.client import Client

from .models import Athlete


class AuthorizeView(View):
    """ Redirect to authorize the app with strava. """

    @staticmethod
    def get(request):
        """ Request oauth via strava. """

        client = Client()

        return_uri = 'http://{}{}'.format(
            request.META['HTTP_HOST'],
            reverse_lazy('strava-authorized')
        )
        authorize_url = client.authorization_url(
            client_id=settings.STRAVA_CLIENT_ID,
            redirect_uri=return_uri
        )
        return HttpResponseRedirect(authorize_url)


class AuthorizedView(View):
    """ View to store an authorized user. """

    @staticmethod
    def get(request):
        """ Request -and store- a strava access token. """
        client = Client()

        # Extract the code from the response
        code = request.GET.get('code')
        access_token = client.exchange_code_for_token(
            client_id=settings.STRAVA_CLIENT_ID,
            client_secret=settings.STRAVA_CLIENT_SECRET,
            code=code
        )
        strava_athlete = client.get_athlete()

        try:
            athlete = Athlete.objects.get(strava_id=strava_athlete.id)
            athlete.strava_token = access_token
        except Athlete.DoesNotExist:
            athlete = Athlete(strava_id=strava_athlete.id, strava_token=access_token)
        athlete.save()

        cache.delete('summary')
        return HttpResponseRedirect(reverse_lazy('strava-summary'))


class SummaryView(TemplateView):
    """ Display a sorted summary of total time by participants. """

    template_name = "summary.html"
    client = None

    def get_context_data(self, **kwargs):
        context = super(SummaryView, self).get_context_data(**kwargs)

        summary = cache.get('summary')
        if summary:
            context['times'] = summary
        else:
            context['times'] = self.get_activity_summary()
            cache.set('summary', context['times'], 60)

        return context

    def get_activity_summary(self):
        """
        Get full activity summary.

        Gets a total active time for all authorized members of the challenge group
        sorted by time and name.
        """
        summary = {}

        # get list of club athletes
        club_athletes = self._get_club_members()

        for athlete in club_athletes:
            name = '{} {}'.format(athlete.firstname, athlete.lastname).title()
            summary[name] = self._get_athlete_summary(athlete.id)

        return self._sort_summary(summary)

    @staticmethod
    def _get_club_members():
        """ Get all athletes belonging to our club. """

        athlete = Athlete.objects.order_by('?').first()
        if not athlete:
            return []

        client = Client(access_token=athlete.strava_token)
        return client.get_club_members(settings.STRAVA_CHALLENGE_CLUB_ID)

    @staticmethod
    def _get_authed_athletes():
        """ Get a dict of all authed athletes. """
        athletes = {}

        for athlete in Athlete.objects.all():
            athletes[athlete.strava_id] = athlete.strava_token

        return athletes

    def _get_athlete_summary(self, athlete_id):
        """ Get a total activity time per athlete. """
        tokens = self._get_authed_athletes()
        total = 0

        if athlete_id in tokens:
            times = []

            client = Client(access_token=tokens.get(athlete_id))
            activities = client.get_activities(
                after=settings.STRAVA_CHALLENGE_START_DATE,
                before=settings.STRAVA_CHALLENGE_END_DATE,
            )
            for activity in activities:
                times.append(activity.moving_time)

            for time in times:
                total += time
        else:
            total = None

        return total

    @staticmethod
    def _sort_summary(summary):
        """
        Sort a prepared summary by time/name.

        Athletes are separated into authorized and unauthorized groups.
        The authorized group is sorted by total ACTIVE competition time.
        The unauthorized group is sorted by name
        """

        authed = OrderedDict()
        unauthed = OrderedDict()
        for name, total in summary.items():
            if total is not None:
                authed[name] = total
            else:
                unauthed[name] = total

        sorted_athletes = OrderedDict(
            sorted(authed.items(), key=operator.itemgetter(1), reverse=True) + sorted(unauthed.items())
        )

        return sorted_athletes
