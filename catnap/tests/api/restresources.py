from catnap.restresources import RestResource, RestModelResource
from django.core.urlresolvers import reverse


class UserResource(RestModelResource):
    fields = ('username', 'first_name', 'last_name', 'is_staff',
              'is_superuser', 'is_active', 'date_joined',)

    #def get_url(self):
        #return reverse('api-user', args=[self.obj.id])

    def get_data(self):
        return super(UserResource, self).get_data()



class DeckResource(RestModelResource):
    fields = ('name', 'description', 'owner', 'created_at', 'modified_at',)

    def get_url_path(self):
        return reverse('api-deck', args=[self.obj.id])

    def get_data(self):
        data = super(DeckResource, self).get_data()
        data['owner'] = UserResource(self.obj.owner).get_data()
        return data






