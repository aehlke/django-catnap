import django.views.generic.edit

from catnap.rest_views import RestView, RestSingleObjectMixin


class FormMixin(django.views.generic.edit.FormMixin):
    def get_form_kwargs(self):
        kwargs = super(FormMixin, self).get_form_kwargs()

        if 'data' in kwargs:
            kwargs['data'] = self.request.DATA
            print self.request.DATA

        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        #TODO add Location header to response.
        return self.render_to_response(context, status=201)

    def form_invalid(self, form):
        context = form.errors
        return self.render_to_response(context, status=422)


class ModelFormMixin(FormMixin, RestSingleObjectMixin,
                     django.views.generic.edit.ModelFormMixin):
    def get_queryset(self):
        '''
        The built-in Django ModelFormMixin isn't smart enough to
        look inside the ModelForm for the model when `self.model`
        is missing, so we do so here.
        '''
        try:
            return super(ModelFormMixin, self).get_queryset()
        except ImproperlyConfigured as e:
            return self.get_form_class().Meta.model._default_manager.all()

    def form_valid(self, form):
        self.object = form.save()
        return super(ModelFormMixin, self).form_valid(form)


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

