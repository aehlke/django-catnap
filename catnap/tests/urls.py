from django.conf.urls.defaults import patterns, include, url
from api.views import DeckList, Deck, EntryPoint

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


api_urlpatterns = patterns('views',
    url('^$', EntryPoint.as_view(), name='api-entry_point'),
    url('^decks/$', DeckList.as_view(), name='api-deck_list'),
    url('^decks/(?P<pk>\d+)/$', Deck.as_view(), name='api-deck'),
)


urlpatterns = patterns('',
    url(r'api/', include(api_urlpatterns)),

    url(r'^admin/', include(admin.site.urls)),
)

