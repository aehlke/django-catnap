from django.http import (HttpResponseBadRequest, HttpResponseNotFound,
        HttpResponseForbidden, HttpResponseGone)
from http import HttpResponseUnauthorized, HttpResponseTemporaryRedirect


class HttpException(Exception):
    def __init__(self, http_response=None):
        self.response = http_response
        super(HttpException, self).__init__(unicode(self.response))

class _HttpException(Exception):
    def __init__(self, *args, **kwargs):
        self.response = self._HTTP_RESPONSE_CLASS(*args, **kwargs)
        super(_HttpException, self).__init__(unicode(self.response))


# HttpException should really only be used for the cases listed below, in general.
# So instead of using it directly, use these instead.

class HttpBadRequestException(_HttpException):
    _HTTP_RESPONSE_CLASS = HttpResponseBadRequest

class HttpUnauthorizedException(_HttpException):
    _HTTP_RESPONSE_CLASS = HttpResponseUnauthorized

class HttpForbiddenException(_HttpException):
    _HTTP_RESPONSE_CLASS = HttpResponseForbidden

class HttpGoneException(_HttpException):
    _HTTP_RESPONSE_CLASS = HttpResponseGone

class HttpTemporaryRedirectException(_HttpException):
    _HTTP_RESPONSE_CLASS = HttpResponseTemporaryRedirect

