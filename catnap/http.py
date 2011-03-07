'''
This module adds missing django.http.HttpResponse subclasses for more 
status codes.
'''
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri


class HttpResponseCreated(HttpResponse):
    status_code = 201

    def __init__(self, location, **kwargs):
        HttpResponse.__init__(self, **kwargs)
        self['Location'] = iri_to_uri(location)

class HttpResponseSeeOther(HttpResponse):
    status_code = 303

    def __init__(self, redirect_to):
        HttpResponse.__init__(self)
        self['Location'] = iri_to_uri(redirect_to)

class HttpResponseNotAcceptable(HttpResponse):
    status_code = 406

class HttpResponseConflict(HttpResponse):
    status_code = 409

class HttpResponseRequestEntityTooLarge(HttpResponse):
    status_code = 413

class HttpResponseUnsupportedMediaType(HttpResponse):
    status_code = 415

