""" Views for strava integration. """
from __future__ import unicode_literals

import datetime
import operator

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.base import TemplateView
from stravalib.client import Client


class AuthorizeView(View):

    def get(self, request):
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

    def get(self, request):
        """ Request -and store- a strava access token. """
        client = Client()

        # Extract the code from the response
        code = request.GET.get('code')
        access_token = client.exchange_code_for_token(
            client_id=settings.STRAVA_CLIENT_ID,
            client_secret=settings.STRAVA_CLIENT_SECRET,
            code=code
        )

        athlete = client.get_athlete()
        # TODO: We would persist this data, if were were to keep this around
        print "For {id}, I now have an access token {token}".format(
            id=athlete.id,
            token=access_token
        )

        return HttpResponseRedirect(reverse_lazy('strava-summary'))


class SummaryView(TemplateView):
    """ Display a sorted summary of total time by participants. """

    template_name = "summary.html"

    def get_context_data(self, **kwargs):
        context = super(SummaryView, self).get_context_data(**kwargs)
        context['times'] = self.get_activity_summary()
        return context

    def get_activity_summary(self):
        """ Organize, sum & sort the activities by athlese and total time. """
        athletes = self.get_activities()
        summary = {}

        for _, values in athletes.iteritems():
            summary[values.get('name')] = reduce(
                operator.add,
                values.get('times')
            )

        sorted_summary = sorted(summary.items(), key=operator.itemgetter(1))
        sorted_summary.reverse()
        return sorted_summary

    def get_activities(self):
        """ Load all club activities from the Strava API. """
        # TODO: Caching. We don't want to load everything EVERY. SINGLE. TIME.
        #       Cache for a sane time and allow overriding.

        client = Client()
        # TODO: we would load a persisted access_token
        #       or redirect to auth if we were to keep this around.
        client.access_token = settings.STRAVA_USER_ACCESS_TOKEN
        activities = client.get_club_activities(settings.DFC_CLUB_ID)

        ppl = {}
        for activity in activities:
            # TODO: Pull the dates from settings/querystring params
            if not self._is_current_activity(activity):
                continue

            if activity.athlete.id not in ppl:
                ppl[activity.athlete.id] = {}
                ppl[activity.athlete.id]['name'] = '{} {}'.format(
                    activity.athlete.firstname,
                    activity.athlete.lastname
                )
                ppl[activity.athlete.id]['times'] = []

            ppl[activity.athlete.id]['times'].append(activity.moving_time)

        return ppl

    @staticmethod
    def _is_current_activity(activity):
        # TODO: Pull the dates from settings/querystring params
        return activity.start_date_local >= datetime.datetime(2016, 1, 25) \
            and activity.start_date_local <= datetime.datetime(2016, 5, 30)
