from django.http import (HttpResponseBadRequest, HttpResponseNotFound,
        HttpResponseForbidden, HttpResponseGone)



class HttpException(Exception):
    def __init__(self, http_response):
        self.response = http_response


# HttpException should really only be used for the cases listed below, in general.
# So instead of using it directly, use these instead.

class HttpBadRequestException(HttpException):
    def __init__(self, *args, **kwargs):
        self.response = HttpResponseBadRequest(*args, **kwargs)

class HttpForbiddenException(HttpException):
    def __init__(self, *args, **kwargs):
        self.response = HttpResponseForbidden(*args, **kwargs)

class HttpGoneException(HttpException):
    def __init__(self, *args, **kwargs):
        self.response = HttpResponseGone(*args, **kwargs)

