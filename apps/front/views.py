""" Views for strava integration. """
from __future__ import unicode_literals

import datetime
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

        return_uri = 'http://{}{}?start_date={}&end_date={}'.format(
            request.META['HTTP_HOST'],
            reverse_lazy('strava-authorized'),
            request.GET.get('start_date'),
            request.GET.get('end_date'),
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

        cache_key = _get_cache_key(request)
        cache.delete(cache_key)
        redir_url = '{}?start_date={}&end_date={}'.format(
            reverse_lazy('strava-summary'),
            _get_start_date(request),
            _get_end_date(request)
        )
        return HttpResponseRedirect(redir_url)


class SummaryView(TemplateView):
    """ Display a sorted summary of total time by participants. """

    template_name = "summary.html"
    client = None

    def get_context_data(self, **kwargs):
        context = super(SummaryView, self).get_context_data(**kwargs)

        cache_key = _get_cache_key(self.request)

        summary = cache.get(cache_key)
        if summary:
            context['times'] = summary
        else:
            context['times'] = self.get_activity_summary()
            cache.set(cache_key, context['times'], 60*15)  # 15 minute cache

        context['start_date'] = _get_start_date(self.request)
        context['end_date'] = _get_end_date(self.request)

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

        if athlete_id in tokens:
            times = []

            client = Client(access_token=tokens.get(athlete_id))
            activities = client.get_activities(
                after=_get_start_date(self.request),
                before=_get_end_date(self.request, include_full_day=True),
            )
            for activity in activities:
                times.append(activity.moving_time)

            total = datetime.timedelta()
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


def _get_cache_key(request):
    start_date = _get_start_date(request)
    end_date = _get_end_date(request)

    return 'summary_{}_to_{}'.format(start_date.replace('-', ''), end_date.replace('-', ''))


def _get_start_date(request):
    try:
        day = request.GET.get('start_date', '')
        start = datetime.datetime.strptime(day, '%Y-%m-%d')
        start_date = start.strftime('%Y-%m-%d')
    except ValueError:
        # Default to start of week
        now = datetime.datetime.now()
        default = now - datetime.timedelta(days=(now.weekday()))
        start_date = default.strftime('%Y-%m-%d')
    return start_date


def _get_end_date(request, include_full_day=False):
    try:
        day = request.GET.get('end_date', '')
        end = datetime.datetime.strptime(day, '%Y-%m-%d')
        end_date = end.strftime('%Y-%m-%d')
    except ValueError:
        # Default to end of week
        now = datetime.datetime.now()
        default = now + datetime.timedelta(days=6)
        end_date = default.strftime('%Y-%m-%d')

    if include_full_day:
        full_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        end_date = full_end_date.strftime('%Y-%m-%d')

    return end_date
