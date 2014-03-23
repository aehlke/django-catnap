# Adapted from django-piston's emitters.py,
# dojango's util/__init__.py,
# and from http://djangosnippets.org/snippets/1162/

import copy
import decimal
import inspect
import json
import re

from django.core.serializers.json import DateTimeAwareJSONEncoder

from django.db.models.query import QuerySet, ValuesQuerySet
from django.db.models import Model, permalink
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import smart_unicode
from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import HttpResponse
from django.core import serializers
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
import datetime
from rfc3339 import rfc3339

#from utils import HttpStatusCode

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

try:
    import cPickle as pickle
except ImportError:
    import pickle

# Allow people to change the reverser (default `permalink`).
reverser = permalink



def base_serialize(data):
    '''
    Super serializer. All other serializers should wrap
    this one. Returns a serialized `dict`. 

    Recursively serialize a lot of types, and
    in cases where it doesn't recognize the type,
    it will fall back to Django's `smart_unicode`.

    Uses RFC 3339 for datetimes, dates, and times.

    Returns `dict`.
    '''
    def _any(thing):
        '''
        Dispatch, all types are routed through here.
        '''
        ret = None

        if isinstance(thing, (QuerySet, ValuesQuerySet)):
            # Actually its the same as a list ...
            ret = _list(thing)
        #elif isinstance(
        elif isinstance(thing, (tuple, list, set)):
            ret = _list(thing)
        elif isinstance(thing, dict):
            ret = _dict(thing)
        elif isinstance(thing, decimal.Decimal):
            ret = str(thing)
        elif isinstance(thing,
                (datetime.datetime, datetime.date, datetime.time)):
            ret = rfc3339(thing, use_system_timezone=False)
        elif isinstance(thing, Model):
            # e.g. a single element from a queryset
            ret = _model(thing)
        #elif isinstance(thing, HttpResponse):
        #    raise HttpStatusCode(thing)
        # here we need to encode the string as unicode (otherwise we get utf-16 in the json-response)
        elif isinstance(thing, basestring):
            ret = unicode(thing)
        # see http://code.djangoproject.com/ticket/5868
        elif isinstance(thing, Promise):
            ret = force_unicode(thing)
        elif inspect.isfunction(thing):
            if not inspect.getargspec(thing)[0]:
                ret = _any(thing())
        elif hasattr(thing, '__emittable__'):
            f = thing.__emittable__
            if inspect.ismethod(f) and len(inspect.getargspec(f)[0]) == 1:
                ret = _any(f())
        elif repr(thing).startswith('<django.db.models.fields.related.RelatedManager'):
            ret = _any(thing.all())
        else:
            ret = smart_unicode(thing, strings_only=True)

        return ret

    def _fk(data, field):
        '''
        Foreign keys.
        '''
        return _any(getattr(data, field.name))

    def _related(data):
        '''
        Foreign keys.
        '''
        return [ _model(m) for m in data.iterator() ]

    def _m2m(data, field):
        '''
        Many to many (re-route to `_model`.)
        '''
        return [ _model(m) for m in getattr(data, field.name).iterator() ]

    def _model(data):
        ret = {}
        # If we only have a model, we only want to encode the fields.
        for f in data._meta.fields:
            ret[f.attname] = _any(getattr(data, f.attname))
        # And additionally encode arbitrary properties that had been added.
        fields = dir(data.__class__) + ret.keys()
        add_ons = [k for k in dir(data) if k not in fields]
        for k in add_ons:
            ret[k] = _any(getattr(data, k))
        return ret

    def _list(data):
        '''
        Lists. (or QuerySets. or ValuesQuerySets.)
        '''
        return [ _any(v) for v in data ]

    def _dict(data):
        '''
        Dictionaries.
        '''
        return dict([ (k, _any(v)) for k, v in data.iteritems() ])

    # Kickstart the seralizin'.
    return _any(data)




def xml_serialize(data):
    def to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement('resource', {})
                to_xml(xml, item)
                xml.endElement('resource')
        elif isinstance(data, dict):
            for key, value in data.iteritems():
                xml.startElement(key, {})
                to_xml(xml, value)
                xml.endElement(key)
        else:
            xml.characters(smart_unicode(data))

    stream = StringIO.StringIO()

    xml = SimplerXMLGenerator(stream, 'utf-8')
    xml.startDocument()
    xml.startElement('response', {})

    to_xml(xml, base_serialize(data))

    xml.endElement('response')
    xml.endDocument()

    return stream.getvalue()


def json_serialize(data):
    #TODO not sure we need this 'T' business
    #def _any(data):
    #    ret = None
    #    if isinstance(data, Decimal):
    #        # json.dumps() cant handle Decimal
    #        ret = str(data)
    #    elif isinstance(data, datetime.datetime):
    #        # For dojo.date.stamp we convert the dates 
    #        # to use 'T' as separator instead of space
    #        # i.e. 2008-01-01T10:10:10 instead of 2008-01-01 10:10:10
    #        ret = str(data).replace(' ', 'T')
    #    elif isinstance(data, datetime.date):
    #        ret = str(data)
    #    elif isinstance(data, datetime.time):
    #        ret = 'T' + str(data)
    #ret = _any(data)

    ret = base_serialize(data)
    return json.dumps(ret,
            cls=DateTimeAwareJSONEncoder,
            ensure_ascii=False, sort_keys=True, indent=4)
    
