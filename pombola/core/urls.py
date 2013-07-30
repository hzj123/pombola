from django.conf.urls.defaults import patterns, include, url

from django.views.generic import DetailView, ListView
from django.views.generic.simple import direct_to_template, redirect_to

from core import models
from core.views import PlaceDetailView

person_patterns = patterns('core.views',
    url(r'^all/',
        ListView.as_view(model=models.Person),
        name='person_list'),

    url(
        r'^politicians/',
        redirect_to,
        {
            # This is what I'd like to have - but as the 'position' path does
            # not exist yet it gets confused. Hardcode instead - this end point
            # should be removed at some point - legacy from the MzKe site.
            # 'url': reverse('position', kwargs={'slug':'mp'}),
            'url': '/position/mp',
            'permanent': True,
        }
    ),
                           
    # featured person ajax load
    url(r'^featured/((?P<direction>(before|after))/)?(?P<current_slug>[-\w]+)',
        'featured_person', 
        name='featured_person'),
    
    url(r'^(?P<slug>[-\w]+)/$', 'person', name='person'),

  )

# ugly, must be a better way
for sub_page in ['scorecard', 'comments', 'experience', 'appearances', 'contact_details']:
    person_patterns += patterns(
        'core.views',
        url(
            '^(?P<slug>[-\w]+)/%s/' % sub_page,  # url regex
            'person_sub_page',                   # view function
            { 'sub_page': sub_page },            # pass in the 'sub_page' arg
            'person_%s' % sub_page               # url name for {% url ... %} tags
        )
    )



place_patterns = patterns('core.views',

    url( r'^all/',                 'place_kind', name='place_kind_all' ),
    url( r'^is/(?P<slug>[-\w]+)/$', 'place_kind', name='place_kind'     ),
    url( r'^is/(?P<slug>[-\w]+)/(?P<session_slug>[-\w]+)/?', 'place_kind', name='place_kind'     ),
    url( r'^mapit_area/(?P<mapit_id>\d+)/', 'place_mapit_area', name='place_mapit_area' ),

    url(r'^(?P<slug>[-\w]+)/$',
        PlaceDetailView.as_view(),      
        name='place'),

    # redirect .../candidates to .../aspirants so that the URL wording matches
    # that on the site. This is to fix originally using the word 'candidates'
    # and can probably be removed at some point when there are no more hits on
    # this path - after July 2013 feels about right.
    url(
        r'^(?P<slug>[-\w]+)/candidates/$',
        redirect_to,
        {
            'url':       '/place/%(slug)s/aspirants',
            'permanent': True,
        }
    ),

    
)

# ugly, must be a better way
for sub_page in ['aspirants', 'election', 'scorecard', 'comments', 'people', 'places', 'organisations', 'data', 'projects']:
    place_patterns += patterns(
        'core.views',
        url(
            '^(?P<slug>[-\w]+)/%s/' % sub_page,  # url regex
            'place_sub_page',                    # view function
            { 'sub_page': sub_page },            # pass in the 'sub_page' arg
            'place_%s' % sub_page                # url name for {% url ... %} tags
        )
    )


organisation_patterns = patterns('core.views',
    url(r'^all/', 'organisation_list', name='organisation_list'),
    url(r'^is/(?P<slug>[-\w]+)/', 'organisation_kind', name='organisation_kind'),
    url(r'^(?P<slug>[-\w]+)/$',   'organisation',      name='organisation'),
)    

# ugly, must be a better way
for sub_page in ['comments', 'contact_details', 'people']:
    organisation_patterns += patterns(
        'core.views',
        url(
            '^(?P<slug>[-\w]+)/%s/' % sub_page,  # url regex
            'organisation_sub_page',                    # view function
            { 'sub_page': sub_page },            # pass in the 'sub_page' arg
            'organisation_%s' % sub_page                # url name for {% url ... %} tags
        )
    )

urlpatterns = patterns('core.views',
    # Homepage
    url(r'^$', 'home', name='home'),

    (r'^person/', include(person_patterns)),
    (r'^place/', include(place_patterns)),
    (r'^organisation/', include(organisation_patterns)),

    url(r'^position/(?P<pt_slug>[-\w]+)/$', 'position_pt', name='position_pt'),
    url(r'^position/(?P<pt_slug>[-\w]+)/(?P<ok_slug>[-\w]+)/$', 'position_pt_ok', name='position_pt_ok'),
    url(r'^position/(?P<pt_slug>[-\w]+)/(?P<ok_slug>[-\w]+)/(?P<o_slug>[-\w]+)/$', 'position_pt_ok_o', name='position_pt_ok_o'),

    # specials
    url(r'^parties', 'parties', name='parties'),

    # Ajax select
    url(r'^ajax_select/', include('ajax_select.urls')),
)

urlpatterns += patterns('core.views',
    url(r'^status/memcached/',       'memcached_status', name='memcached_status'),
)

urlpatterns += patterns('',
    url(r'^status/down/', direct_to_template, {'template': 'down.html'} ),
)


# We handle the robots here rather than as a static file so that we can send
# different content on a staging server. We don't use direct_to_template as we
# want to set some caching headers too.
urlpatterns += patterns('core.views',
    url(r'robots.txt', 'robots' ),
)
