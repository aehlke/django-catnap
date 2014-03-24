import django.views.generic.edit

from catnap.rest_views import RestView, RestSingleObjectMixin


class FormMixin(django.views.generic.edit.FormMixin):
    def form_valid(self, form):
        context = self.get_context_data()
        return self.render_to_response(context, status=201)

    def form_invalid(self, form):
        context = form.errors
        print 'testing'
        print form.errors.as_json()
        from catnap.serializers import base_serialize
        print base_serialize(form.errors)
        print form.errors.items()
        return self.render_to_response(context, status=422)


class ModelFormMixin(FormMixin, RestSingleObjectMixin,
                     django.views.generic.edit.ModelFormMixin):
    pass


class FormViewMixin(FormMixin, RestView):
    '''
    Currently only handles creation.
    '''
    def post(self, request, *args, **kwargs):
        '''
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        '''
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ModelFormViewMixin(ModelFormMixin, FormViewMixin):
    def post(self, request, *args, **kwargs):
        self.object = None

        return super(ModelFormViewMixin, self).post(request, *args, **kwargs)

