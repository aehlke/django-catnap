# Some code adapted from the WebOb project: http://bitbucket.org/ianb/webob/

from webob.acceptparse import accept_property, Accept, MIMEAccept, NilAccept, MIMENilAccept, NoAccept

ALL_HTTP_METHODS = ['OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE']

class HttpAcceptMiddleware(object):
    '''
    Adds an `accept` property to `request`, which is a MIMEAccept instance,
    from the WebOb library. This lets you easily check whether the given
    `request.META['HTTP_ACCEPT']` header accepts various content types.
    It's intelligent enough to understand the various forms allowed by
    the HTTP RFC.

    See: http://pythonpaste.org/webob/reference.html#accept-headers 
    for usage examples.
    '''

    def process_request(self, request):
        '''
        Add an `accept` property and set its value, which parses it
        See HTTP RFC section 14.1
        '''
        accept_val = request.META.get('HTTP_ACCEPT', None)
        if accept_val:
            request.accept = MIMEAccept('Accept', accept_val)
        else:
            request.accept = MIMENilAccept('Accept')
        return None


class HttpMethodsFallbackMiddleware(object):
    '''
    Looks for `_method` param in POST requests, to change
    `request.method` to its value, if it's valid.

    Don't put this too early in the middleware chain, since
    it could break middleware that depends on POST being POST.
    '''
    FALLBACK_PARAM = '_method'

    def process_request(self, request):
        if request.POST and request.POST.has_key(self.FALLBACK_PARAM):
            method = request.POST[self.FALLBACK_PARAM]
            if method in ALL_HTTP_METHODS:
                request.method = request.POST[self.FALLBACK_PARAM]
            else:
                return HttpResponseNotAllowed(ALL_HTTP_METHODS)
        return None

