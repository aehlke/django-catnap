from django.http import HttpResponse
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.core.exceptions import ImproperlyConfigured
from django.utils import simplejson as json
#from djclsview import View
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, BaseDetailView
from django.views.generic.list import MultipleObjectMixin, BaseListView
from serializers import json_serialize


class HttpResponseNotAcceptable(HttpResponse):
    status_code = 406


class RestView(View):
    '''
    A base class view that cares a little more about RESTy things,
    like strict content types.

    Also lets you use itself as a function rather than making
    you put as_view() in your URL conf. (-not yet implemented-!)

    Requires `HttpAcceptMiddleware` to be installed.
    '''
    def dispatch(self, request, *args, **kwargs):
       # Make sure the `Accept` header matches our content type.
       if self.content_type not in request.accept:
           return HttpResponseNotAcceptable()

       return super(RestView, self).dispatch(request, *args, **kwargs)


    def get_response(self, content, **httpresponse_kwargs):
        'Construct an `HttpResponse` object.'
        ## The following are for IE especially
        #response['Pragma'] = 'no-cache'
        #response['Cache-Control'] = 'must-revalidate'
        #response['If-Modified-Since'] = str(datetime.datetime.now())
        return HttpResponse(content,
                            content_type=self.content_type,
                            **httpresponse_kwargs)
    

#class ResourceView(View):
#    '''
#    Currently we only support a single content type per resource.
#    '''
#    content_type = None

#    def __call__(self):
#        resp = self._route(self.request.method)
#        resp = self._process_response(resp)
#        return self.process_response(resp)
        
#    def _process_response(self, response):
#        if self.content_type:
#            response['Content-Type'] = self.content_type

#        # Make sure the `Accept` header matches our content type.
#        if self.content_type not in self.request.accept:
#            return HttpResponseNotAcceptable()
            
#        return response

#    def process_response(self, response):
#        '''
#        Called on each view method return value.
#        Override this in a sublcass to add filtering to the HTTP
#        response object.
#        '''
#        return response
        

#class JsonMixin(object):
#    '''
#    View methods should return data structures which are 
#    serializable into JSON. This serializes them and puts them
#    into an HttpResponse instance.

#    Sets `content_type` to "application/json" which should absolutely 
#    be overridden with a more descriptive content type.
#    '''
#    # Override this for vendor-specific content types.
#    #     e.g "application/vnd.mycompany.FooBar+json"
#    content_type = 'application/json'


class SerializableMultipleObjectMixin(MultipleObjectMixin):
    '''
    This is a version of MultipleObjectMixin which is more careful
    to avoid duplicate or otherwise unnecessary context items.

    For example, instead of having both `\{modelname\}_list` and
    `object_list` items, it only has `\{modelname\}_list`.

    It also accepts a `fields` property which limits the queryset
    in the context to only including certain fields.
    '''
    fields = None

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
        #queryset = kwargs.pop('object_list')
        #import pdb;pdb.set_trace()
        queryset = self.get_queryset()
        page_size = self.get_paginate_by(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(
                    queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
            }
        context.update(kwargs)

        ## Limit our queryset?
        #if self.fields:
        #    queryset = queryset.values(self.fields)

        context_object_name = self.get_context_object_name(queryset)
        context[context_object_name] = queryset

        return context


class RestMultipleObjectMixin(SerializableMultipleObjectMixin):
    resource = None

    def get_context_data(self, object_list=None, **kwargs):
        context = super(RestMultipleObjectMixin, self).get_context_data(**kwargs)

        if not self.resource:
            raise ImproperlyConfigured(
                    u"'%s' must define 'resource', a class which takes "
                    "a model instance and implements a 'get_data' method."
                    % self.__class__.__name__)

        context_object_name = self.get_context_object_name(self.get_queryset())
        #import pdb;pdb.set_trace()
        context[context_object_name] = list(
                self.resource(_).get_data()
                for _ in context[context_object_name])
        return context


class SerializableSingleObjectMixin(SingleObjectMixin):
    '''
    This is a version of SingleObjectMixin which is more careful
    to avoid duplicate or otherwise unnecessary context items.

    For example, instead of having both `\{modelname\}_list` and
    `object_list` items, it only has `\{modelname\}_list`.

    It also accepts a `fields` property which limits the queryset
    in the context to only including certain fields.
    '''
    fields = None

    def get_context_object_name(self, obj):
        '''
        Get the name to use for the object.
        '''
        return super(SerializableSingleObjectMixin, self).get_context_object_name(
            obj) or 'object'

    def get_context_data(self, **kwargs):
        context = kwargs
        #context_object_name = self.get_context_object_name(self.object)
        #if context_object_name:
            #context[context_object_name] = self.object
        return context

class BaseSerializableDetailView(SingleObjectMixin, View):
    def get(self, request, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class BaseSerializableListView(BaseListView, RestMultipleObjectMixin):
    pass
    

class DetailView(BaseSerializableDetailView):
    pass

class ListView(BaseSerializableListView):
    pass


class JsonResponseMixin(object):
    # Override this for vendor-specific content types.
    #     e.g "application/vnd.mycompany.FooBar+json"
    #content_type = 'application/json'

    def render_to_response(self, context):
        'Returns a JSON response containing `context` as payload'
        return self.get_response(self.convert_context_to_json(context))

    def convert_context_to_json(self, context):
        'Convert the context dictionary into a JSON object'
        return json_serialize(context)


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

    









