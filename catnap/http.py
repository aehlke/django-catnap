'''
This module adds missing django.http.HttpResponse subclasses for more 
status codes.
'''
from django.http import HttpResponse


class HttpResponseNotAcceptable(HttpResponse):
    status_code = 406

class HttpResponseConflict(HttpResponse):
    status_code = 409

class HttpResponseRequestEntityTooLarge(HttpResponse):
    status_code = 413

class HttpResponseUnsupportedMediaType(HttpResponse):
    status_code = 415

