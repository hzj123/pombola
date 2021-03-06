import re
import datetime

from django.shortcuts  import render_to_response, get_object_or_404, redirect
from django.http import Http404
from django.template   import RequestContext
from django.views.generic import TemplateView, DetailView, ListView

from pombola.hansard.models import Sitting, Entry
from pombola.core.models import Person

# import models
# from django.shortcuts  import render_to_response, redirect
# from django.template   import RequestContext
#
#
# def default(request):
#     return render_to_response(
#         'hansard/default.html',
#         {
#             'chunks': models.Chunk.objects.all(),
#         },
#         context_instance=RequestContext(request)
#     )
#
# #   /hansard/venue/yyyy/mm/dd/hh:mm
#

"""
Hansard views - possible url structure:

The url to the various hansard pages follow this sort of structure:

  ../venue/yyyy/mm/dd/day_id-slug-that-can-be-ignored

'venue' is the slug of the debating chamber, committee etc that the report is
for.

'yyyy', 'mm', 'dd', 'hh:mm' is the date down to the start of the sitting. It is
assumed that one chamber can only do one thing at a time so there will never be
a conflict.

    ^
    ^(?P<venue>[\w\-]+)/
    ^(?P<venue>[\w\-]+)/(?P<year>\d{4})/
    ^(?P<venue>[\w\-]+)/(?P<year>\d{4})/(?P<month>\d{2})/
    ^(?P<venue>[\w\-]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>)/
    ^(?P<venue>[\w\-]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>)/(?P<day_id>\d+)-(?P<slug>[\w\-]+)

"""

class IndexView(TemplateView):
    template_name = "hansard/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['sittings'] = Sitting.objects.all() # FIXME - put a limit on here [0:10]

        return context


class SittingView(DetailView):
    model = Sitting

    def get_object(self):
        """Get the object based on venue and start date and time"""

        venue_slug = self.kwargs['venue_slug']
        start_date_and_time = self.kwargs['start_date_and_time']

        query_args = {
            'venue__slug':     venue_slug,
        }

        # add blank HH-MM-SS if needed
        start_time_parts = re.split('-', start_date_and_time)
        if len(start_time_parts) == 3:
            start_time_parts.extend( [ '00','00','00' ] )

        # split the date and time up into the relevant fields
        (year,month,day,hour,minute,second) = [ int(x) for x in start_time_parts ]

        # add start_date to the query
        query_args['start_date'] = datetime.date(year=year,month=month,day=day)

        # if there is a time use it
        if hour or minute or second:
            query_args['start_time__gte'] = datetime.time(hour=hour, minute=minute, second=second)

        # get all matching sittings
        sittings = Sitting.objects.filter( **query_args ).order_by('start_time')

        if not len(sittings):
            raise Http404

        return sittings[0]


# class BaseView ( View ):
#     pass
#
# class VenueMixin( object ):
#
#     def get_venue(self):
#         "Return the venue that should be searched for. 404s if not found."
#         return get_object_or_404(Venue, slug=self.kwargs['slug'])
#
# class IndexView( BaseView ):
#     pass
#
# class VenueView( VenueMixin, BaseView ):
#     pass
#
# class YearView( YearMixin, VenueView ):
#     pass
#




# TODO - change to class based views.

# TODO - implement a view of all of a persons speeches
#
# def person_entries(request, slug):
#     """Display entries for a person"""
#
#     person = get_object_or_404( Person, slug=slug )
#
#     return render_to_response(
#         'hansard/person_entries.html',
#         {
#             'object': person,
#         },
#         context_instance=RequestContext(request)
#     )


def person_summary(request, slug):
    """Display summary of a person's contributions to Hansard"""

    person = get_object_or_404( Person, slug=slug )

    entries_qs = Entry.objects.filter(speaker=person)

    lifetime_summary = entries_qs.monthly_appearance_counts()



    return render_to_response(
        'hansard/person_summary.html',
        {
            'person':           person,
            'entry_count':      entries_qs.count(),
            'recent_entries':   entries_qs.all().order_by('-sitting__start_date')[0:5],
            'lifetime_summary': lifetime_summary,
        },
        context_instance=RequestContext(request)
    )


class PersonAllAppearancesView(ListView):

    def get_context_data(self, **kwargs):
        context = super(PersonAllAppearancesView, self).get_context_data(**kwargs)
        context['object'] = self.person
        return context

    def get_queryset(self):

        # Extract the person slug from the URL
        person_slug = self.kwargs['slug']

        # Find (or 404) the person
        self.person = get_object_or_404(Person, slug=person_slug)

        # Specify the filter for the list of entries
        return Entry.objects.filter(speaker=self.person).select_related('sitting__venue')


class HansardPersonMixin(object):

    def get_context_data(self, **kwargs):
        context = super(HansardPersonMixin, self).get_context_data(**kwargs)
        entries = Entry.objects.filter(speaker=self.object)
        context['hansard_entries'] = entries.order_by('-sitting__start_date')
        return context
