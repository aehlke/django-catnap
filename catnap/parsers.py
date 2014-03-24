# Adapted from https://github.com/tomchristie/django-rest-framework/blob/3d999e4be38f0836063aacdf31d1396fbbb3a5fc/rest_framework/parsers.py

import json

from webob.acceptparse import MIMEAccept


class BaseParser(object):
    mime_accept = None

    @classmethod
    def accepts(self, media_type):
        media_type = media_type.split(';')[0].strip()

        if not getattr(self, '_mime_accept', None):
            self._mime_accept = MIMEAccept('Accept', self.mime_accept)

        return media_type in self._mime_accept

    def parse(self, request):
        raise NotImplementedError("Must override the parse method.")


class JsonParser(BaseParser):
    mime_accept = 'application/json'

    def parse(self, request):
        try:
            return json.loads(request.body, request.encoding)
        except ValueError:
            raise ParseError()

