from django.http import (HttpResponseBadRequest, HttpResponseNotFound,
        HttpResponseForbidden, HttpResponseGone)

from catnap.http import HttpResponseUnauthorized, HttpResponseTemporaryRedirect


class HttpException(Exception):
    '''
    Should not really be used directly. Instead, use e.g. `NotAuthenticated`.
    '''
    def __init__(self, http_response=None):
        self.response = http_response
        super(HttpException, self).__init__(unicode(self.response))


class _HttpException(HttpException):
    def __init__(self, *args, **kwargs):
        super(_HttpException, self).__init__(http_response=self._HTTP_RESPONSE_CLASS(*args, **kwargs))


class NotAuthenticated(HttpException):
    def __init__(self, challenge='Basic', realm=None):
        www_authorize = '{} realm="{}"'.format(challenge, realm)

        response = HttpResponseUnauthorized(www_authorize)

        super(NotAuthenticated, self).__init__(http_response=response)


class AuthenticationFailed(NotAuthenticated):
    pass


class ParseError(_HttpException):
    _HTTP_RESPONSE_CLASS = HttpResponseBadRequest


#class HttpGoneException(_HttpException):
#    _HTTP_RESPONSE_CLASS = HttpResponseGone

#class HttpTemporaryRedirectException(_HttpException):
#    _HTTP_RESPONSE_CLASS = HttpResponseTemporaryRedirect

