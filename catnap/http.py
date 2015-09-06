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


class HttpResponseNoContent(HttpResponse):
    status_code = 204


class HttpResponseSeeOther(HttpResponse):
    status_code = 303

    def __init__(self, redirect_to):
        HttpResponse.__init__(self)
        self['Location'] = iri_to_uri(redirect_to)


class HttpResponseTemporaryRedirect(HttpResponse):
    status_code = 307

    def __init__(self, redirect_to):
        HttpResponse.__init__(self)
        self['Location'] = iri_to_uri(redirect_to)


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

    def __init__(self, www_authenticate):
        HttpResponse.__init__(self)
        self['WWW-Authenticate'] = www_authenticate


class HttpResponseNotAcceptable(HttpResponse):
    status_code = 406


class HttpResponseConflict(HttpResponse):
    status_code = 409


class HttpResponseRequestEntityTooLarge(HttpResponse):
    status_code = 413


class HttpResponseUnsupportedMediaType(HttpResponse):
    status_code = 415
