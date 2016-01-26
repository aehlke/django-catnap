'''
Django middleware for HTTP authentication.

Copyright (c) 2007, Accense Technology, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.
  * Neither the name of the Accense Technology nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import base64

from django.contrib.auth import authenticate
from django.conf import settings

from catnap.exceptions import AuthenticationFailed, ParseError

# Written by sgk, adapted by Alex Ehlke for django-catnap.

# This code depends on the implementation internals of the Django builtin
# 'django.contrib.auth.middleware.AuthenticationMiddleware' authentication
# middleware, specifically the 'request._cached_user' member.


class BasicAuthMiddleware(object):
    '''
    Django implementation of HTTP basic authentication.

    This middleware must be placed in the 'settings.py' MIDDLEWARE_CLASSES
    definition before the Django builtin 'AuthenticationMiddleware'.

    Uses the settings `BASIC_AUTH_CHALLENGE` and `BASIC_AUTH_REALM`.
    '''
    def _process_request(self, request):
        if hasattr(request, '_cached_user'):
            return

        if not request.META.get('HTTP_AUTHORIZATION'):
            return

        try:
            method, encoded = request.META['HTTP_AUTHORIZATION'].split()
        except ValueError:
            raise ParseError()

        if method.lower() != 'basic':
            return

        try:
            username, password = base64.b64decode(encoded).split(':')
        except ValueError:
            raise ParseError()

        user = authenticate(username=username, password=password)

        if user is None or not user.is_active:
            raise AuthenticationFailed(
                challenge=getattr(settings, 'BASIC_AUTH_CHALLENGE', 'Basic'),
                realm=getattr(settings, 'BASIC_AUTH_REALM', 'django-catnap'))

        request._cached_user = user

    def process_request(self, request):
        try:
            self._process_request(request)
        except AuthenticationFailed as e:
            return e.response

