# Taken from http://code.djangoproject.com/wiki/ReplacingGetAbsoluteUrl
# See: http://github.com/jezdez/django-urls/

from django.conf import settings
from django.core.urlresolvers import reverse
import urlparse


def relative_to_absolute_url(path):
        # Should we look up a related site?
        #if getattr(self._meta, 'url_by_site'):
        prefix = getattr(settings, 'DEFAULT_URL_PREFIX', None)
        if prefix is None:
            prefix = u'http://localhost'
            if 'django.contrib.sites' in settings.INSTALLED_APPS:
                from django.contrib.sites.models import Site
                try:
                    prefix = 'http://%s' % Site.objects.get_current().domain
                except Site.DoesNotExist:
                    pass
        return prefix + path

class UrlMixin(object):
    def get_url(self):
        if hasattr(self.get_url_path, 'dont_recurse'):
            raise NotImplementedError
        try:
            path = self.get_url_path()
        except NotImplementedError:
            raise
        return relative_to_absolute_url(path)
    get_url.dont_recurse = True
    
    def get_url_path(self):
        if hasattr(self.get_url, 'dont_recurse'):
            raise NotImplementedError
        try:
            url = self.get_url()
        except NotImplementedError:
            raise
        bits = urlparse.urlparse(url)
        return urlparse.urlunparse(('', '') + bits[2:])
    get_url_path.dont_recurse = True


def absolute_reverse(viewname, *args, **kwargs):
    path = reverse(viewname, *args, **kwargs)
    return relative_to_absolute_url(path)

