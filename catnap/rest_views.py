from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, BaseDetailView
from django.views.generic.list import MultipleObjectMixin, BaseListView
from django_urls import UrlMixin

from catnap.http import (HttpResponseNotAcceptable, HttpResponseNoContent,
        HttpResponseCreated, HttpResponseTemporaryRedirect)
from catnap.serializers import json_serialize
from catnap.parsers import JsonParser


class _HttpResponseShortcuts(object):
    '''
    Shortcuts for `RestView.get_response`.
    '''
    def __init__(self, parent_view):
        self.parent = parent_view

    def see_other(self, redirect_to):
        return self.parent.get_response(redirect_to,
                content_type='',
                response_class=HttpResponseSeeOther)

    def created(self, location):
        return self.parent.get_response(location,
                content_type='',
                response_class=HttpResponseCreated)

    def temporary_redirect(self, redirect_to):
        return self.parent.get_response(redirect_to,
                content_type='',
                response_class=HttpResponseTemporaryRedirect)

    def no_content(self):
        return self.parent.get_response(None,
                content_type='',
                response_class=HttpResponseNoContent)


class RestView(View):
    '''
    A base class view that cares a little more about RESTy things,
    like strict content types and HTTP response codes.

    Also lets you use itself as a function rather than making
    you put as_view() in your URL conf. (-not yet implemented-!)

    Requires `HttpAcceptMiddleware` to be installed.
    '''
    request_parsers = [JsonParser]

    def __init__(self, *args, **kwargs):
        self.responses = _HttpResponseShortcuts(self)

    def _set_parsed_request_data(self):
        data = self.request.POST
        content_type = self.request.META.get('HTTP_CONTENT_TYPE',
                                             self.request.META.get('CONTENT_TYPE', ''))

        if content_type:
            for parser_cls in self.request_parsers:
                print content_type
                print self.request.encoding
                print parser_cls.accepts(content_type)
                if parser_cls.accepts(content_type):
                    data = parser_cls().parse(self.request)
                    continue

        self.request.DATA = data

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Make sure the `Accept` header matches our content type.
        if self.content_type not in request.accept:
            return HttpResponseNotAcceptable()

        self._set_parsed_request_data()

        return super(RestView, self).dispatch(request, *args, **kwargs)

    def allowed_methods(self, request, *args, **kwargs):
        '''Returns a list of allowed HTTP verbs.'''
        return [m for m in self.http_method_names if hasattr(self, m)]

    def options(self, request, *args, **kwargs):
        resp = self.get_response(None, content_type='')
        resp['Access-Control-Allow-Methods'] = ', '.join(
                self.allowed_methods(request, *args, **kwargs)).upper()
        return resp

    def get_response(self,
            content,
            content_type=None,
            response_class=HttpResponse,
            **response_kwargs):
        '''
        Construct an `HttpResponse` object, or whatever response class
        is specified by `response_class`.

        The `content_type` defaults to whatever `self.content_type`
        evaluates to.

        To take advantage of `self.content_type` and other mixins
        which may process responses, this method should always be used 
        to construct `HttpResponse` objects (or any other methods
        which end up calling this one) instead of using `HttpResponse`
        directly.
        '''
        ## The following are for IE especially
        #response['Pragma'] = 'no-cache'
        #response['Cache-Control'] = 'must-revalidate'
        #response['If-Modified-Since'] = str(datetime.datetime.now())
        if content_type is None:
            content_type = self.content_type

        if content_type == '':
            content_type = None

        return response_class(content or '',
                              content_type=content_type,
                              **response_kwargs)


class SerializableMultipleObjectMixin(MultipleObjectMixin):
    '''
    This is a version of MultipleObjectMixin which is more careful
    to avoid duplicate or otherwise unnecessary context items.

    For example, instead of having both `\{modelname\}_list` and
    `object_list` items, it only has `\{modelname\}_list`.
    '''

    def get_context_object_name(self, object_list):
        '''
        Get the name of the item to be used in the context.
        '''
        return super(
                SerializableMultipleObjectMixin, self).get_context_object_name(
                object_list) or 'object_list'
    
    def get_context_data(self, **kwargs):
        '''
        Get the context for this view.
        '''
        queryset = self.get_queryset()

        context = {}

        # Add the list of objects
        context_object_name = self.get_context_object_name(queryset)
        context[context_object_name] = queryset

        context.update(kwargs)

        return context


class _ResourceClassDependencyMixin(object):
    resource_class = None

    def get_resource_class(self):
        if not self.resource_class:
            raise ImproperlyConfigured(
                    u"'%s' must define 'resource_class', a class which takes "
                    "a model instance and implements a 'get_data' method."
                    % self.__class__.__name__)
        return self.resource_class


class RestMultipleObjectMixin(SerializableMultipleObjectMixin,
                              _ResourceClassDependencyMixin,
                              UrlMixin):
    '''
    Extends the `SerializableMultipleObjectMixin` class to instantiate
    `Resource` objects for every object in the list.

    Since this is a convenience class for representing a list of resources,
    this list itself doesn't have its own corresponding `Resource` subclass,
    but we still support a `get_url` method to add a `url` key to the
    context, as `Resource` does. (Or `get_url_path`, which will be expanded
    to become an absolute URL, as per `UrlMixin`'s behavior.)
    '''
    def get_context_data(self, object_list=None, **kwargs):
        context = super(RestMultipleObjectMixin, self).get_context_data(**kwargs)
        context_object_name = self.get_context_object_name(self.get_queryset())

        try:
            context['url'] = self.get_url()
        except NotImplementedError:
            pass

        resource_class = self.get_resource_class()
        context[context_object_name] = list(
                resource_class(_).get_data()
                for _ in context[context_object_name])
        return context


class RestSingleObjectMixin(SingleObjectMixin,
                            _ResourceClassDependencyMixin):
    '''
    This is a version of `SingleObjectMixin` which is more careful
    to avoid duplicate or otherwise unnecessary context items.

    Instantiates a `Resource` object for the given detail object, and uses 
    its `get_data` return value for the context. The entire context is 
    the object itself, instead of the default Django behavior of having 
    the object a level deep, e.g. `{"object": etc}`.
    '''
    def get_context_data(self, **kwargs):
        '''
        Relies on `self.object` to retrieve the desired object used to
        instantiate a `Resource`. Don't pass an `object` kwarg to this
        method -- if you want to specify an object rather than have this
        class find one automatically from our queryset or model class,
        then override the `get_object` method to return what you want
        or set `self.object`.

        Any `kwargs` passed to this will be added to the context.
        '''
        context = {}

        if self.object:
            resource_class = self.get_resource_class()
            resource = resource_class(self.object)
            context = resource.get_data()

        context.update(kwargs)
        return context


class DetailView(RestSingleObjectMixin, View):
    def get(self, request, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        return self.render_to_response(context)


class ListView(RestMultipleObjectMixin, BaseListView):
    pass


class DeletionMixin(object):
    '''
    A mixin providing the ability to delete objects.
    '''
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseNoContent()


class _BaseEmitterMixin(object):
    @property
    def serialize_context(self):
        raise NotImplementedError(
                'serialize_context method must be implemented in subclass.')

    def render_to_response(self, context, **response_kwargs):
        '''
        Returns a response containing `context` as payload,
        using the implemented serializer method.
        '''
        return self.get_response(self.serialize_context(context),
                                 **response_kwargs)


class JsonEmitterMixin(_BaseEmitterMixin):
    # Override this for vendor-specific content types.
    #     e.g "application/vnd.mycompany.FooBar+json"
    content_type = 'application/json'

    def convert_context_to_json(self, context):
        'Convert the context dictionary into a JSON object'
        return json_serialize(context)

    serialize_context = convert_context_to_json


class AutoContentTypeMixin(object):
    '''
    Inherit from this after `ResourceView`
    (e.g. class `MyResourceView(ResourceView, AutoContentTypeMixin):`)
    to have the `content_type` property automatically set based off
    your view's class name.

    You must set an additional property, `content_type_template_string`,
    which is formatted to include the class name.

    In practice, you should subclass this and `ResourceView` to add
    your own defaults.

    Ex.:
        
        class MyAppResourceView(ResourceView, AutoContentTypeMixin):
            content_type_template_string = "application/vnd.myapp.\{0\}+json"
        
        class AuthorList(MyAppResourceView):
            # This class will have a content_type property containing:
            #   "application/vnd.myapp.AuthorList+json"
            pass

    You can still override this by specifying a `content_type` property
    in your subclass, of course. You'd want to do that if you had 
    several views which respond with the same content types. This mixin 
    works best for the common case of one content type per view.
    '''
    # Override this when you subclass AutoContentTypeMixin.
    content_type_template_string = None

    # For finer-grained overriding, if set, this value will be used
    # instead of the class's name for formatting the template string.
    content_subtype = None

    @property
    def content_type(self):
        return 'application/json'
        if self.content_type_template_string:
            subtype = self.content_subtype or self.__class__.__name__
            return self.content_type_template_string.format(subtype)



#def ModelResourceView(ResourceView):


#TODO get_absolute_url helper. just a generic 'url for this thing' for resourceviews


#############################
# Example:
#
#class ManabiResourceView(JsonResourceView, AutoContentTypeMixin):
#    content_type_template_string = 'application/vnd.manabi.{0}+json'
#
#class Deck(ManabiResourceView):
#    def GET(self, request):
#        pass

