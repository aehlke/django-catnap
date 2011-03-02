


class RestResource(object):
    def get_data(self):
        '''
        Adds a `url` field if this class has a `get_url` method.
        '''
        data = {}
        if hasattr(self, 'get_url'):
            data['url'] = self.get_url()
        return data


class RestModelResource(RestResource):
    '''
    Represents a single object, in a queryset.
    '''
    # If left as None, it will not filter the fields.
    fields = None

    def __init__(self, obj):
        self.obj = obj

    def _model_to_dict(self, obj):
        fields = self.fields

        ret = {}
        # If we only have a model, we only want to encode the fields.
        for f in obj._meta.fields:
            if not self.fields or f.attname in self.fields:
                #ret[f.attname] = _any(getattr(obj, f.attname))
                ret[f.attname] = getattr(obj, f.attname)
        # And additionally encode arbitrary properties 
        # that had been added.
        fields = dir(obj.__class__) + ret.keys()
        add_ons = [k for k in dir(obj) if k not in fields]
        for k in add_ons:
            if not self.fields or k in self.fields:
                #ret[k] = _any(getattr(obj, k))
                ret[k] = getattr(obj, k)
        #import pdb;pdb.set_trace()
        return ret

    def get_data(self):
        data = super(RestModelResource, self).get_data()
        data.update(self._model_to_dict(self.obj))
        return data


