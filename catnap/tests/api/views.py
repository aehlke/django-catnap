from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import forms
from django.forms.models import modelformset_factory, formset_factory
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from catnap.rest_views import (JsonEmitterMixin, AutoContentTypeMixin,
        RestView, ListView, DetailView)
from rest_resources import UserResource, DeckResource
import models


class MyRestView(JsonEmitterMixin, AutoContentTypeMixin, RestView):
    '''
    Our JSON-formatted response base class.
    '''
    content_type_template_string = 'application/vnd.catnap-test.{0}+json'

    #@method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MyRestView, self).dispatch(*args, **kwargs)



# Resource views

class EntryPoint(MyRestView):
    '''
    Entry-point to our REST API.

    This view's URL is the only one that clients should need to know,
    and the only one that should be documented in the API!
    '''
    def get(self, request):
        '''
        List the available top-level resource URLs.
        '''
        context = {
            'deck_list_url': reverse('api-deck_list'),
            #'users': reverse('rest-users'),
        }
        return self.render_to_response(context)


class DeckList(ListView, MyRestView):
    '''
    List of decks.
    '''
    content_subtype = 'DeckList'
    resource = DeckResource

    def get_queryset(self):
        return models.Deck.objects.order_by('name')
    
    
class Deck(DetailView, MyRestView):
    '''
    Detail view of a single deck.
    '''
    content_subtype = 'Deck'

    def get_object(self):
        return get_object_or_404(pk=self.kwargs.get('pk'))



