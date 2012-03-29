# This module mostly taken from django-tastypie (thanks!), 
# which is also BSD-licensed.
# Also uses part of Django-Rest-Framework.
import base64

from django.contrib.auth import authenticate as django_authenticate
from django.middleware.csrf import CsrfViewMiddleware

from exceptions import HttpUnauthorizedException


class Authentication(object):
    '''
    A simple base class to establish the protocol for auth.
    
    By default, this indicates the user is always authenticated.
    '''
    def authenticate(self, request, **kwargs):
        '''
        Identifies if the user is authenticated to continue or not.
        
        Should usually set `request.user`. Doesn't return anything, 
        but if authentication fails, it should raise an exception, 
        usually an `HttpException` subclass.
        '''
    

class BasicAuthentication(Authentication):
    '''
    Handles HTTP Basic auth against a specific auth backend if provided,
    or against all configured authentication backends using the
    ``authenticate`` method from ``django.contrib.auth``.
    
    Optional keyword arguments:

    ``backend``
        If specified, use a specific ``django.contrib.auth`` backend instead
        of checking all backends specified in the ``AUTHENTICATION_BACKENDS``
        setting.
    ``realm``
        The realm to use in the ``HttpUnauthorized`` response.  Default:
        ``django-catnap``.
    '''
    def __init__(self, backend=None, realm='django-catnap'):
        self.backend = backend
        self.realm = realm

    def _unauthorized(self):
        #FIXME: Sanitize realm.
        raise HttpUnauthorizedException("Basic Realm='%s'" % self.realm)
        #raise HttpUnauthorizedException("Basic Realm='%s'" % self.realm)

    def authenticate(self, request, **kwargs):
        '''
        Checks a user's basic auth credentials against the current
        Django auth backend.
        
        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        '''
        if not request.META.get('HTTP_AUTHORIZATION'):
            self._unauthorized()
        
        try:
            (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()
            if auth_type.lower() != 'basic':
                return self._unauthorized()
            user_pass = base64.b64decode(data)
        except:
            self._unauthorized()

        bits = user_pass.split(':')
        
        if len(bits) != 2:
            self._unauthorized()

        if self.backend:
            user = self.backend.authenticate(username=bits[0], password=bits[1])
        else:
            user = django_authenticate(username=bits[0], password=bits[1])

        if user is None:
            self._unauthorized()

        request.user = user


class DjangoContribAuthentication(Authentication):
    '''Use Djagno's built-in request session for authentication.'''
    def authenticate(self, request, **kwargs):
        if getattr(request, 'user', None) and request.user.is_active:                
            resp = CsrfViewMiddleware().process_view(request, None, (), {})
            if resp is None:  # csrf passed
                return request.user
        return None


class AuthenticationMixin(object):
    '''
    Mixin to use for catnap REST views.

    You must override the `authenticator` property with whichever
    authentication method you want. It defaults to a debug-mode
    one which always authenticates successfully.
    '''
    # Which authentication to use.
    authenticator = Authentication()
    authenticators = None

    def dispatch(self, request, *args, **kwargs):
        if getattr(self, 'authenticators', None):
            # Try the authenticators until one works.
            for authenticator in self.authenticators:
                try:
                    authenticator.authenticate(request)
                except HttpUnauthorizedException:
                    pass
                else:
                    break
        else:
            self.authenticator.authenticate(request)

        return super(AuthenticationMixin, self).dispatch(
            request, *args, **kwargs)

