import re
import random

from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts  import render_to_response, get_object_or_404, redirect
from django.template   import RequestContext
from django.views.generic.list_detail import object_detail, object_list

from mzalendo.core import models
from mzalendo.helpers import geocode


def home(request):
    """Homepage"""
    featured_person = None
    current_slug = False
    if request.GET.get('next_from'):
        current_slug = request.GET.get('next_from')
        want_previous = False
    elif request.GET.get('prev_from'):
        current_slug = request.GET.get('prev_from')
        want_previous = True
    if current_slug:
        featured_person = models.Person.objects.get_next_featured(current_slug, want_previous)
    if featured_person == None:
        featured_people = models.Person.objects.filter(can_be_featured=True)
        if featured_people.exists():
            featured_person = random.choice(featured_people)
    return render_to_response(
        'core/home.html',
        {
          'featured_person': featured_person,
        },
        context_instance=RequestContext(request)
    )


def person_list(request):
    return object_list(
        request,
        queryset=models.Person.objects.all(),
    )

def organisation_list(request):
    return object_list(
        request,
        queryset=models.Organisation.objects.all(),
    )

def person(request, slug):
    return object_detail(
        request,
        queryset = models.Person.objects,
        slug     = slug,
    )


def place(request, slug):
    return object_detail(
        request,
        queryset = models.Place.objects,
        slug     = slug,
    )

def place_kind(request, slug):
    print slug
    place_kind = get_object_or_404(
        models.PlaceKind,
        slug=slug
    )

    return object_list(
        request,
        queryset = place_kind.place_set.all(),
        extra_context = { 'kind': place_kind, },
    )


def position(request, slug):
    title = get_object_or_404(
        models.PositionTitle,
        slug=slug
    )
    
    return render_to_response(
        'core/position_detail.html',
        {
            'object': title,
        },
        context_instance=RequestContext(request)
    )


def organisation(request, slug):
    org = get_object_or_404(
        models.Organisation,
        slug=slug
    )

    return render_to_response(
        'core/organisation_detail.html',
        {
            'object': org,
            'positions': org.position_set.all().order_by('person__legal_name'),
        },
        context_instance=RequestContext(request)
    )


def organisation_kind(request, slug):
    org_kind = get_object_or_404(
        models.OrganisationKind,
        slug=slug
    )
    
    orgs = (
        org_kind
            .organisation_set
            .all()
            .annotate(num_positions = Count('position'))
            .order_by('-num_positions', 'name')
    )
    
    return object_list(
        request,
        queryset = orgs,
        extra_context = { 'kind': org_kind, },
    )

def parties(request):
    """Show all parties that currently have MPs sitting in parliament"""
    
    parties = models.Organisation.objects.all().active_parties()
    
    return render_to_response(
        'core/parties.html',
        {
            'parties': parties,
        },
        context_instance = RequestContext( request ),
    )
